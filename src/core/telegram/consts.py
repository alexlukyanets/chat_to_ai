from typing import Final

from telethon.tl.types import InputMessagesFilterEmpty, InputMessagesFilterGif, InputMessagesFilterMusic, \
    InputMessagesFilterVideo, InputMessagesFilterPhotos, InputMessagesFilterDocument, InputMessagesFilterPhotoVideo, \
    InputMessagesFilterChatPhotos

LIMIT: Final[int] = 100

SESSION_PATH: Final[str] = 'session/telegram'

EXPORT_PATH: Final[str] = 'export/telegram'

FILTER_TO_USE: list[type] = [
    InputMessagesFilterEmpty,
    InputMessagesFilterGif,
    InputMessagesFilterMusic,
    InputMessagesFilterVideo,
    InputMessagesFilterPhotos,
    InputMessagesFilterDocument,
    InputMessagesFilterPhotoVideo,
    InputMessagesFilterChatPhotos
]
