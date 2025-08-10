import asyncio
import os
from typing import Optional, Tuple

from colorama import Fore, init
from telethon import TelegramClient
from telethon.tl.types import (
    Message,
    MessageMediaDocument,
    MessageMediaPhoto,
    User,
)
from tqdm import tqdm

from db import (
    add_discussion,
    add_post,
    get_existing_post,
    get_last_post_id,
    init_db,
    save_user,
)
from dialog import get_user_data, logo

logo()
API_ID, API_HASH, CHANNEL_NAME, PATH, session_exists = get_user_data()

MEDIA_DIR = os.path.join(os.path.abspath(PATH), "GhostlyGrabber_media")
MAX_CONCURRENT_DOWNLOADS = 10000

channel_media_dir = os.path.join(MEDIA_DIR, CHANNEL_NAME)
os.makedirs(channel_media_dir, exist_ok=True)

engine, Session, TelegramUser, PostModel, Discussion = init_db(PATH, CHANNEL_NAME)

init(autoreset=True)

session_path = os.path.join(os.path.abspath(PATH), "anon_session.session")
client = TelegramClient(session_path, int(API_ID), API_HASH)


def get_media_info(message: Message) -> Tuple[Optional[str], Optional[str]]:
    """
    Determines the media type and file extension for a given Telegram message.
    Args:
        message (Message): The Telegram message object.
    Returns:
        tuple: (media_type, extension) or (None, None) if not found.
    """
    if isinstance(message.media, MessageMediaPhoto):
        return "photo", "jpg"
    elif isinstance(message.media, MessageMediaDocument):
        mime_type = message.media.document.mime_type
        if mime_type.startswith("video/"):
            return "video", mime_type.split("/")[-1]
        elif mime_type.startswith("audio/"):
            return "audio", mime_type.split("/")[-1]
        else:
            return "document", mime_type.split("/")[-1]
    return None, None


async def download_media_file(
    client: TelegramClient, message: Message, media_type: str, ext: str, media_dir: str
) -> Optional[str]:
    """
    Downloads a media file from a Telegram message if it does not already exist.
    Args:
        client (TelegramClient): The Telethon client.
        message (Message): The Telegram message object.
        media_type (str): The type of media (photo, video, etc.).
        ext (str): The file extension.
        media_dir (str): Directory to save the media file.
    Returns:
        str or None: Path to the downloaded media file or None if failed.
    """
    media_path = os.path.join(media_dir, f"{message.id}.{ext}")
    if not os.path.exists(media_path):
        try:
            await client.download_media(message.media, file=media_path)
        except Exception as e:
            print(
                Fore.RED + f"Error loading {media_type} for a message {message.id}: {e}"
            )
            return None
    return media_path


async def download_media_with_semaphore(
    message: Message,
    client: TelegramClient,
    media_dir: str,
    semaphore: asyncio.Semaphore,
) -> Optional[str]:
    """
    Downloads media using a semaphore to limit concurrent downloads.
    Args:
        message (Message): The Telegram message object.
        client (TelegramClient): The Telethon client.
        media_dir (str): Directory to save the media file.
        semaphore (asyncio.Semaphore): Semaphore to limit concurrency.
    Returns:
        str or None: Path to the downloaded media file or None if failed.
    """
    async with semaphore:
        media_type, ext = get_media_info(message)
        if media_type:
            return await download_media_file(
                client, message, media_type, ext, media_dir
            )
    return None


async def download_discussion(
    client: TelegramClient,
    message: Message,
    discussion_dir: str,
    semaphore: asyncio.Semaphore,
) -> Optional[str]:
    """
    Downloads media from a discussion message using a semaphore.
    Args:
        client (TelegramClient): The Telethon client.
        message (Message): The Telegram message object.
        discussion_dir (str): Directory to save the discussion media.
        semaphore (asyncio.Semaphore): Semaphore to limit concurrency.
    Returns:
        str or None: Path to the downloaded media file or None if failed.
    """
    async with semaphore:
        media_type, ext = get_media_info(message)
        if media_type:
            return await download_media_file(
                client, message, media_type, ext, discussion_dir
            )
    return None


async def process_discussion_replies(
    client, 
    session, 
    message, 
    channel_media_dir, 
    semaphore,
    entity
):
    if not (message.replies and message.replies.replies > 0):
        return

    discussion_dir = os.path.join(channel_media_dir, f"discussion_{message.id}")
    os.makedirs(discussion_dir, exist_ok=True)

    try:
        async for reply in client.iter_messages(entity, reply_to=message.id):
            reply_media_path = await download_discussion(
                client, reply, discussion_dir, semaphore
            )

            reply_username = None
            if reply.sender_id:
                try:
                    reply_sender = await client.get_entity(reply.sender_id)
                    if isinstance(reply_sender, User):
                        reply_username = await save_user(session, TelegramUser, reply_sender)
                except (ValueError, TypeError) as e:
                    print(Fore.YELLOW + f"Error getting sender for reply {reply.id}: {e}")

            add_discussion(
                session,
                Discussion,
                message_id=reply.id,
                post_id=message.id,
                text=reply.text,
                date=reply.date,
                username=reply_username,
                media_path=reply_media_path,
            )
    except Exception as e:
        print(Fore.RED + f"Error processing replies for message {message.id}: {e}")

async def process_message(client, session, message, channel_media_dir, semaphore, entity):
    media_path = await download_media_with_semaphore(
        message, client, channel_media_dir, semaphore
    )

    username = None
    if message.sender_id:
        sender = await client.get_entity(message.sender_id)
        if isinstance(sender, User):
            username = await save_user(session, TelegramUser, sender)

    existing_post = get_existing_post(session, PostModel, message.id)
    if existing_post:
        return

    add_post(
        session,
        PostModel,
        post_id=message.id,
        text=message.text,
        media_path=media_path,
        date=message.date,
        views=message.views,
        forwards=message.forwards,
        username=username,
    )

    await process_discussion_replies(
        client, session, message, channel_media_dir, semaphore, entity
    )


async def main():
    async with client:
        session = Session()
        try:
            channel = await client.get_entity(CHANNEL_NAME)
            total_messages = (await client.get_messages(channel, limit=0)).total

            pbar = tqdm(
                total=total_messages, desc="Downloading data", unit="msgs", ncols=100
            )

            last_post_id = get_last_post_id(session, PostModel)
            semaphore = asyncio.Semaphore(MAX_CONCURRENT_DOWNLOADS)

            async for message in client.iter_messages(channel, min_id=last_post_id):
                try:
                    await process_message(
                        client, 
                        session, 
                        message, 
                        channel_media_dir, 
                        semaphore,
                        channel
                    )
                except Exception as e:
                    print(Fore.RED + f"Error {message.id}: {e}")
                finally:
                    pbar.update(1)

            pbar.close()
            print(Fore.GREEN + "Download completed")

        except Exception as e:
            print(Fore.RED + f"Error: {e}")
        finally:
            session.close()


if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())
