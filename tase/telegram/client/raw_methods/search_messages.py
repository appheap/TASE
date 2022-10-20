import asyncio
from typing import List, Union

import pyrogram
from pyrogram import raw, types, utils


class Filters:
    EMPTY = raw.types.InputMessagesFilterEmpty()
    PHOTO = raw.types.InputMessagesFilterPhotos()
    VIDEO = raw.types.InputMessagesFilterVideo()
    PHOTO_VIDEO = raw.types.InputMessagesFilterPhotoVideo()
    DOCUMENT = raw.types.InputMessagesFilterDocument()
    URL = raw.types.InputMessagesFilterUrl()
    ANIMATION = raw.types.InputMessagesFilterGif()
    VOICE_NOTE = raw.types.InputMessagesFilterVoice()
    AUDIO = raw.types.InputMessagesFilterMusic()
    CHAT_PHOTO = raw.types.InputMessagesFilterChatPhotos()
    PHONE_CALL = raw.types.InputMessagesFilterPhoneCalls()
    AUDIO_VIDEO_NOTE = raw.types.InputMessagesFilterRoundVideo()
    VIDEO_NOTE = raw.types.InputMessagesFilterRoundVideo()
    MENTION = raw.types.InputMessagesFilterMyMentions()
    LOCATION = raw.types.InputMessagesFilterGeo()
    CONTACT = raw.types.InputMessagesFilterContacts()
    PINNED = raw.types.InputMessagesFilterPinned()


POSSIBLE_VALUES = list(
    map(
        lambda x: x.lower(),
        filter(lambda x: not x.startswith("__"), Filters.__dict__.keys()),
    )
)


# noinspection PyShadowingBuiltins
async def get_chunk(
    client: "pyrogram.Client",
    chat_id: Union[int, str],
    query: str = "",
    filter: str = "empty",
    offset: int = 0,
    offset_id: int = 0,
    limit: int = 100,
    from_user: Union[int, str] = None,
    only_newer_messages: bool = True,
    with_id: bool = True,
) -> List[types.Message]:
    try:
        filter = Filters.__dict__[filter.upper()]
    except KeyError:
        raise ValueError('Invalid filter "{}". Possible values are: {}'.format(filter, ", ".join(f'"{v}"' for v in POSSIBLE_VALUES))) from None

    if with_id:
        add_offset = -limit if only_newer_messages else 0
    else:
        add_offset = offset

    r = await client.invoke(
        raw.functions.messages.Search(
            peer=await client.resolve_peer(chat_id),
            q=query,
            filter=filter,
            min_date=0,
            max_date=0,
            offset_id=offset_id,
            add_offset=add_offset,
            limit=limit,
            min_id=0,
            max_id=0,
            from_id=(await client.resolve_peer(from_user) if from_user else None),
            hash=0,
        ),
        sleep_threshold=60,
    )

    return await utils.parse_messages(client, r)


def search_messages(
    client: pyrogram.Client,
    chat_id: Union[int, str],
    query: str = "",
    offset: int = 0,
    offset_id: int = 0,
    filter: str = "empty",
    limit: int = 0,
    from_user: Union[int, str] = None,
    only_newer_messages: bool = True,
):
    """Search for text and media messages inside a specific chat.
    If you want to get the messages count only, see :meth:`~pyrogram.Client.search_messages_count`.
    Parameters:
        chat_id (``int`` | ``str``):
            Unique identifier (int) or username (str) of the target chat.
            For your personal cloud (Saved Messages) you can simply use "me" or "self".
            For a contact that exists in your Telegram address book you can use his phone number (str).
        query (``str``, *optional*):
            Text query string.
            Required for text-only messages, optional for media messages (see the ``filter`` argument).
            When passed while searching for media messages, the query will be applied to captions.
            Defaults to "" (empty string).
        offset (``int``, *optional*):
            Sequential number of the first message to be returned.
            Defaults to 0.
        filter (``str``, *optional*):
            Pass a filter in order to search for specific kind of messages only:
            - ``"empty"``: Search for all kind of messages (default).
            - ``"photo"``: Search for photos.
            - ``"video"``: Search for video.
            - ``"photo_video"``: Search for either photo or video.
            - ``"document"``: Search for documents (generic files).
            - ``"url"``: Search for messages containing URLs (web links).
            - ``"animation"``: Search for animations (GIFs).
            - ``"voice_note"``: Search for voice notes.
            - ``"audio"``: Search for audio files (music).
            - ``"chat_photo"``: Search for chat photos.
            - ``"phone_call"``: Search for phone calls.
            - ``"audio_video_note"``: Search for either audio or video notes.
            - ``"video_note"``: Search for video notes.
            - ``"mention"``: Search for messages containing mentions to yourself.
            - ``"location"``: Search for location messages.
            - ``"contact"``: Search for contact messages.
            - ``"pinned"``: Search for pinned messages.
        limit (``int``, *optional*):
            Limits the number of messages to be retrieved.
            By default, no limit is applied and all messages are returned.
        from_user (``int`` | ``str``, *optional*):
            Unique identifier (int) or username (str) of the target user you want to search for messages from.
    Returns:
        ``Generator``: A generator yielding :obj:`~pyrogram.types.Message` objects.
    Example:
        .. code-block:: python
            # Search for text messages in chat. Get the last 120 results
            for message in app.search_messages(chat_id, query="hello", limit=120):
                print(message.text)
            # Search for pinned messages in chat
            for message in app.search_messages(chat_id, filter="pinned"):
                print(message.text)
            # Search for messages containing "hello" sent by yourself in chat
            for message in app.search_messages(chat, "hello", from_user="me"):
                print(message.text)
    """
    current = 0
    total = abs(limit) or (1 << 31) - 1
    limit = min(100, total)

    with_id = True if offset_id != 0 else False
    if not only_newer_messages:
        offset_id += 1

    last_offset_id = -1

    while True:
        messages = asyncio.run(
            get_chunk(
                client=client,
                chat_id=chat_id,
                query=query,
                filter=filter,
                offset=offset,
                offset_id=offset_id,
                limit=limit,
                from_user=from_user,
                only_newer_messages=only_newer_messages,
                with_id=with_id,
            )
        )

        if not messages:
            return

        offset += len(messages)
        if with_id:
            if only_newer_messages:
                offset_id = messages[0].id + 1
            else:
                offset_id = messages[-1].id

            if offset_id == last_offset_id:
                return

            last_offset_id = offset_id

        else:
            offset_id = 0

        for message in messages:
            yield message

            current += 1

            if current >= total:
                return
