import asyncio
import os
from datetime import datetime, timedelta, timezone
from telethon import TelegramClient
from telethon.tl.types import InputMessagesFilterDocument
from telethon.errors import FloodWaitError
import logging
from tqdm.asyncio import tqdm
import aiofiles

# CRITICAL: cryptg must be installed for speed
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FastTelegramDownloader:
    def __init__(self, api_id, api_hash, phone, channel, download_dir='downloads', max_concurrent=8):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        self.channel = channel
        self.download_dir = download_dir
        self.max_concurrent = max_concurrent  # Telegram limit ~8-12
        self.client = TelegramClient('telegram_session', api_id, api_hash, 
                                   connection_retries=None, retry_delay=1)
        os.makedirs(download_dir, exist_ok=True)
    
    async def start_client(self):
        await self.client.start(phone=self.phone)
        logger.info("🚀 Fast client started (cryptg enabled)")
    
    async def get_channel_entity(self):
        entity = await self.client.get_entity(self.channel)
        logger.info(f"📺 Channel: {entity.title}")
        return entity
    
    async def download_file_semaphore(self, message, semaphore):
        """Download single file with semaphore control"""
        async with semaphore:
            try:
                if not message.media or not message.document:
                    return None
                
                filename = message.file.name or f"file_{message.id}"
                filepath = os.path.join(self.download_dir, filename)
                
                # Skip existing files
                if os.path.exists(filepath):
                    logger.info(f"⏭️  Skip: {filename}")
                    return None
                
                await message.download_media(file=filepath)
                return filename
            except FloodWaitError as e:
                logger.warning(f"⏳ Flood wait: {e.seconds}s")
                await asyncio.sleep(e.seconds)
                return None
            except Exception as e:
                logger.error(f"❌ {message.id}: {e}")
                return None
    
    async def download_concurrent(self, messages, desc="Downloading"):
        """Concurrent downloads with semaphore"""
        semaphore = asyncio.Semaphore(self.max_concurrent)
        tasks = [self.download_file_semaphore(msg, semaphore) for msg in messages]
        
        results = []
        for coro in tqdm.as_completed(tasks, desc=desc, total=len(tasks)):
            result = await coro
            if result:
                results.append(result)
        
        return results
    
    async def download_date_range_fast(
        self,
        from_date,
        to_date,
        per_day: bool = True,
        stop_on_missing: bool = False,
    ):
        """FAST version with concurrent downloads per-day.

        Behavior:
        - Iterate per-day in the provided date range and collect messages for each day
        - If there are no matching files for a given day, skip that day immediately (this can be toggled)
        - Optionally stop the whole loop the first time an empty day is encountered
        """
        entity = await self.get_channel_entity()

        logger.info(
            f"⚡ Downloading per-day {from_date.date()} → {to_date.date()} (Concurrent, max {self.max_concurrent})"
        )

        # Normalize to_date/from_date date boundaries
        start_date = from_date.date()
        end_date = to_date.date()
        total_days = (end_date - start_date).days + 1

        if not per_day:
            # Old behavior: collect across entire range at once
            messages = []
            logger.info("📥 Collecting messages across entire range (non-per-day)")
            async for message in self.client.iter_messages(
                entity,
                offset_date=to_date,
                filter=InputMessagesFilterDocument,
                limit=5000,
            ):
                if message.date > to_date or message.date < from_date or not message.document:
                    continue
                messages.append(message)

            logger.info(f"🎯 Found {len(messages)} files to download")
            downloaded = await self.download_concurrent(messages, f"🚀 {len(messages)} files")
            logger.info(f"✅ Complete! Downloaded {len(downloaded)} files")
            return

        for delta in range(total_days):
            day = start_date + timedelta(days=delta)
            day_start = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
            day_end = day_start + timedelta(days=1)

            logger.info(f"📥 Collecting messages for {day}")
            messages = []
            # Collect only messages from this day
            async for message in self.client.iter_messages(
                entity,
                offset_date=day_end,
                filter=InputMessagesFilterDocument,
                limit=5000,
            ):
                if not message.document:
                    continue
                # message.date is timezone-aware; filter by day start <= date < day_end
                if message.date < day_start or message.date >= day_end:
                    continue
                messages.append(message)

            if not messages:
                logger.info(f"⏭️  No files found on {day} - skipping")
                if stop_on_missing:
                    logger.info("⚠️  stop_on_missing enabled - stopping further dates")
                    break
                continue

            logger.info(f"🎯 Found {len(messages)} files to download for {day}")
            downloaded = await self.download_concurrent(messages, f"🚀 {len(messages)} files on {day}")
            logger.info(f"✅ Complete! Downloaded {len(downloaded)} files for {day}")
    
    async def download_current_day_fast(self):
        """Fast current day downloads"""
        today = datetime.now(timezone.utc).date()
        tomorrow = datetime.now(timezone.utc).date() + timedelta(days=1)
        await self.download_date_range_fast(
            datetime(today.year, today.month, today.day, tzinfo=timezone.utc),
            datetime(tomorrow.year, tomorrow.month, tomorrow.day, tzinfo=timezone.utc)
        )
    
    async def close(self):
        await self.client.disconnect()

# USAGE
async def main():
    API_ID = ''  # From https://my.telegram.org/apps
    API_HASH = ''
    PHONE = ''  # Your phone number with country code
    CHANNEL = '@nfo_data'  # Your channel
    DOWNLOAD_DIR = 'downloads'
    
    downloader = FastTelegramDownloader(API_ID, API_HASH, PHONE, CHANNEL, DOWNLOAD_DIR, max_concurrent=8)
    
    try:
        await downloader.start_client()
        
        # FAST DATE RANGE (your dates)
        start_dt = datetime(2025, 11, 30, tzinfo=timezone.utc)
        end_dt = datetime(2025, 12, 3, 23, 59, 59, tzinfo=timezone.utc)
        # per_day=True (default): iterate each day and skip immediately the days with no files
        await downloader.download_date_range_fast(start_dt, end_dt, per_day=True, stop_on_missing=False)
        # non-per-day behavior (collect across whole range) can be requested with per_day=False
        # await downloader.download_date_range_fast(start_dt, end_dt, per_day=False)
        
    finally:
        await downloader.close()

if __name__ == "__main__":
    asyncio.run(main())
