from asyncio import Runner

from core.telegram.parse_chat import parse_telegram_chat


async def main() -> None:
    await parse_telegram_chat()


if __name__ == '__main__':
    with Runner() as runner:
        runner.run(main())
