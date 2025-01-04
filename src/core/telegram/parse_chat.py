from json import dumps
from pathlib import Path

from telethon import TelegramClient
from telethon.tl.types import Channel
from telethon.tl.patched import Message
from telethon.sessions import SQLiteSession
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.channels import GetForumTopicsRequest, GetFullChannelRequest

# Project
from logger import logger
from config import settings
from core.tool import format_datetime, ensure_folder_exists, prepare_folder
from core.telegram.consts import EXPORT_PATH, SESSION_PATH
from core.telegram.models import TelegramMessage


class TelegramChatParser:
    def __init__(self) -> None:
        self.export_path: Path = Path(EXPORT_PATH)
        self.session_path: Path = Path(SESSION_PATH)

        ensure_folder_exists(folder=self.session_path)
        session_file: Path = self.session_path / 'my_session'
        session: SQLiteSession = SQLiteSession(str(session_file))

        self.client: TelegramClient = TelegramClient(
            session=session,
            api_id=settings.TELEGRAM_API_ID,
            api_hash=settings.TELEGRAM_API_HASH
        )

    async def connect_with_two_fa(self) -> None:
        await self.client.connect()
        if not await self.client.is_user_authorized():
            await self.client.send_code_request(phone=settings.TELEGRAM_PHONE)
            code: str = input('Enter code: ')
            try:
                await self.client.sign_in(phone=settings.TELEGRAM_PHONE, code=code)
            except SessionPasswordNeededError:
                await self.client.sign_in(password=settings.TELEGRAM_PASSWORD)
            if not await self.client.is_user_authorized():
                raise RuntimeError('Failed to authorize in Telegram!')

        logger.info(f'Connected to Telegram, phone: {settings.TELEGRAM_PHONE}')

    async def disconnect_client(self) -> None:
        await self.client.disconnect()
        logger.info('Client disconnected from Telegram')

    @staticmethod
    def _get_name_or_username(message: Message) -> str:
        if not message.sender:
            return 'Unknown'
        try:
            last_name: str = message.sender.last_name
            first_name: str = message.sender.first_name
            username: str = message.sender.username
        except AttributeError:
            return message.sender.username
        return ', '.join(filter(None, [first_name, last_name, username]))

    def _save_message(self, file, msg: Message, first: bool) -> bool:
        if not msg.media and (text := msg.message):
            data: dict = TelegramMessage(
                message=text,
                name=self._get_name_or_username(msg),
                date=format_datetime(dt=msg.date)
            ).model_dump()
            if not first:
                file.write(',')
            file.write(dumps(obj=data, ensure_ascii=False, indent=2))
            return True
        return False

    async def get_group_channels(self) -> dict[int, str]:
        group_channels: dict[int, str] = {}
        async for dialog in self.client.iter_dialogs(limit=None):
            if dialog.is_channel and dialog.is_group:
                if 'u4u' not in dialog.name.lower():
                    continue
                group_channels[dialog.id] = dialog.name
                break
        return group_channels

    async def get_topics(self, channel_id: int):
        entity = await self.client.get_entity(entity=channel_id)
        if not isinstance(entity, Channel):
            logger.warning(f'ID {channel_id} is not a valid channel or supergroup.')
            return None

        await self.client(GetFullChannelRequest(channel=entity))
        try:
            topics_result = await self.client(
                GetForumTopicsRequest(
                    channel=entity,
                    q='',
                    offset_date=0,
                    offset_id=0,
                    offset_topic=0,
                    limit=100
                )
            )
            return topics_result
        except Exception as e:
            logger.error(f'Error fetching topics: {e}')
            return None

    async def parse_big_telegram_chats_by_topics(self) -> None:
        await self.connect_with_two_fa()
        logger.info('Extracting big chat data for multiple branches...')

        group_channels: dict[int, str] = await self.get_group_channels()
        for group_channel_id, group_channel_name in group_channels.items():
            channel_folder: Path = prepare_folder(
                folder_name=group_channel_name,
                parent_folder=self.export_path
            )

            topics = await self.get_topics(channel_id=group_channel_id)
            if not topics or not hasattr(topics, 'topics'):
                logger.info(f'No topics found for channel: {group_channel_name} (ID: {group_channel_id}).')
                continue

            for topic in topics.topics:
                topic_name: str = getattr(topic, 'title', 'UnknownTopic')
                topic_folder: Path = prepare_folder(
                    folder_name=topic_name,
                    parent_folder=channel_folder
                )

                logger.info(
                    f'Processing chat: {group_channel_name} '
                    f'- Topic: {topic_name} (Channel ID: {group_channel_id})'
                )

                output_file: Path = topic_folder / 'big_chat_data.json'
                with output_file.open(mode='w', encoding='utf-8') as file:
                    file.write('[')
                    first: bool = True

                    async for msg in self.client.iter_messages(
                            entity=group_channel_id,
                            limit=None,
                            reply_to=topic.id
                    ):
                        if self._save_message(file=file, msg=msg, first=first):
                            first = False

                    file.write(']')

        logger.info('Big chat data for all branches saved to JSON.')
