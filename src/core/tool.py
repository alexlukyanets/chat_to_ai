from pathlib import Path
from re import sub
from typing import Any
from datetime import datetime
from urllib.parse import unquote_plus

from unidecode import unidecode
from money_parser import price_str

from core.consts import HUMAN_DATE_FORMAT
from logger import logger


def clear_string(value: Any) -> str:
    if not isinstance(value, str):
        logger.error(f'{value} is not a string')
        return ''
    unquoted_value: str = unquote_plus(value)
    return ' '.join(unidecode(unquoted_value).split())


def convert_str_to_float_money(money_str: str) -> float | int | None:
    try:
        return price_str(money_str)
    except (ValueError, AttributeError) as exc:
        logger.error(f'Failed to convert money to float: {exc!r}')


async def get_unix_time() -> int:
    return int(datetime.now().timestamp())


def format_datetime(dt: datetime) -> str:
    return dt.strftime(HUMAN_DATE_FORMAT)


def sanitize_folder_name(name: str) -> str:
    return sub(pattern=r'[\\/*?:"<>|]', repl='_', string=name or 'Unknown')


def ensure_folder_exists(folder: Path) -> None:
    if not folder.is_dir():
        folder.mkdir(parents=True, exist_ok=True)


def prepare_folder(folder_name: str, parent_folder: Path) -> Path:
    safe_name: str = sanitize_folder_name(name=folder_name)
    folder: Path = parent_folder / safe_name
    ensure_folder_exists(folder=folder)
    return folder
