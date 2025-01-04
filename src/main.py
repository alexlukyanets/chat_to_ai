from asyncio import Runner

from core.telegram.parse_chat import TelegramChatParser


async def main() -> None:
    await TelegramChatParser().parse_big_telegram_chats_by_topics()


if __name__ == '__main__':
    with Runner() as runner:
        runner.run(main())
