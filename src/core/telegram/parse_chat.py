from pathlib import Path
from json import dumps

from telethon import TelegramClient
from telethon.tl.patched import Message
from telethon.sessions import SQLiteSession
from telethon.errors import SessionPasswordNeededError

from logger import logger

from config import settings

from core.tool import format_datetime

from core.telegram.consts import EXPORT_PATH, SESSION_PATH
from core.telegram.models import TelegramMessage


async def connect_with_two_fa() -> TelegramClient:
    folder: Path = Path(SESSION_PATH)
    folder.mkdir(parents=True, exist_ok=True)
    session_file: Path = folder / 'my_session'
    session: SQLiteSession = SQLiteSession(str(session_file))

    client: TelegramClient = TelegramClient(
        session=session,
        api_id=settings.TELEGRAM_API_ID,
        api_hash=settings.TELEGRAM_API_HASH
    )
    await client.connect()

    if not await client.is_user_authorized():
        await client.send_code_request(phone=settings.TELEGRAM_PHONE)
        code: str = input('Enter code: ')
        try:
            await client.sign_in(phone=settings.TELEGRAM_PHONE, code=code)
        except SessionPasswordNeededError:
            await client.sign_in(password=settings.TELEGRAM_PASSWORD)
        if not await client.is_user_authorized():
            raise RuntimeError('Failed to authorize in Telegram!')

    logger.info(f'Connected to Telegram as {settings.TELEGRAM_USERNAME}')
    return client


def get_name_or_username(message: Message) -> str:
    if not message.sender:
        return 'Unknown'
    last_name: str = message.sender.last_name or ''
    if first_name := (message.sender.first_name or last_name):
        return f'{first_name} {last_name}'.strip()
    return message.sender.username or 'Unknown'


async def parse_telegram_chat(*, limit: int | None = None) -> None:
    client: TelegramClient = await connect_with_two_fa()
    export_path: Path = Path(EXPORT_PATH) / settings.TELEGRAM_USERNAME
    export_path.mkdir(parents=True, exist_ok=True)
    output_file: Path = export_path / 'chat_data.json'

    logger.info('Extracting chat data...')
    with output_file.open(mode='w', encoding='utf-8') as file:
        file.write('[')
        first: bool = True
        async for msg in client.iter_messages(entity=settings.TELEGRAM_USERNAME, limit=limit):
            if not msg.media and (text := msg.message):
                data: dict = TelegramMessage(
                    message=text,
                    name=get_name_or_username(message=msg),
                    date=format_datetime(dt=msg.date)
                ).model_dump()
                if not first:
                    file.write(',')
                file.write(dumps(obj=data, ensure_ascii=False, indent=2))
                first = False
        file.write(']')

    await client.disconnect()
    logger.info('Chat data saved to JSON.')
