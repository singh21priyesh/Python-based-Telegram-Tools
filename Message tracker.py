##================USAGE
#input mmobile number (memeber of group):91xxxxxxx
#input otp recieved on telegram associated with this numebr
#input password of your account abcd123
#once .session is establiesh and a flie is .sesion is placed in folder, no need to input passowrd again


from telethon import TelegramClient
import re
from datetime import datetime
from collections import defaultdict
from datetime import datetime, timedelta, timezone

now = datetime.now(timezone.utc)
first_day_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

if first_day_this_month.month == 1:
    first_day_last_month = first_day_this_month.replace(year=first_day_this_month.year - 1, month=12)
else:
    first_day_last_month = first_day_this_month.replace(month=first_day_this_month.month - 1)

start_time = first_day_last_month
end_time = now

# Replace with your Telegram API credentials
api_id = ''
api_hash = ''
channel_username = -1ffffff0  # e.g., 'mychannel' or channel ID ceq_ali_members, algo_temp_usrs 

# This regex should match your login message format
pattern = re.compile(
    r'(?P<name>.+?) with telegram_id (?P<teleid>\d+) and (?P<procid>[a-f0-9]+) Logged in',
    re.IGNORECASE
)


# Storage
teleid_map = defaultdict(list)

async def analyze_logins():
    client = TelegramClient('session_analysis', api_id, api_hash)
    await client.start()

    async for msg in client.iter_messages(channel_username, limit=500):
        if not msg.text or msg.date < start_time or msg.date > end_time:
            continue
        elif not msg.text:
            continue
        else:
            pass

        match = pattern.search(msg.text)
        if match:
            teleid = match.group("teleid")
            procid = match.group("procid")
            timestamp = msg.date.strftime('%Y-%m-%d %H:%M:%S')  # Use actual message time
            teleid_map[teleid].append((procid, timestamp))
        else:
            print("No match:", msg.text)

    await client.disconnect()

    for teleid, entries in teleid_map.items():
        unique_procids = set(procid for procid, _ in entries)

        # Alert if multiple processor IDs are found
        if len(unique_procids) > 1:
            print(f"\n❌️ ALERT: Telegram ID {teleid} has {len(unique_procids)} different processor IDs!")


        print("\n📋 Unique Processor IDs per Telegram ID:")


        for procid in unique_procids:
            print(f"👤 Telegram ID: {teleid} | 💻 Processor ID: {procid}")


##    print("\n📋 Unique Processor IDs per Telegram ID:")
##    for teleid, entries in teleid_map.items():
##        seen_procids = set()
##        for procid, timestamp in entries:
##            if procid not in seen_procids:
##                print(f"👤 Telegram ID: {teleid} | 💻 Processor ID: {procid}")
##                seen_procids.add(procid)
##
##    for teleid, entries in teleid_map.items():
##        unique_proc_ids = {entry[0] for entry in entries}
##        print(f"\n👤 Telegram ID: {teleid}")
##        print(f"🔢 Total logins: {len(entries)}")
##        print(f"🔁 Unique processor IDs: {len(unique_proc_ids)}")
##        for procid, timestamp in entries:
##            print(f"    🕒 {timestamp} | 💻 {procid}")

##pattern = re.compile(
##    r'(?P<name>.+?) with telegram_id (?P<teleid>\d+) and (?P<procid>[a-f0-9]+) Logged in on (?P<timestamp>[\d\-:\. ]+)',
##    re.IGNORECASE
##)

##async def analyze_logins():
##    client = TelegramClient('session_analysis', api_id, api_hash)
##    await client.start()
##
##    async for msg in client.iter_messages(channel_username, limit=500):
##        if not msg.text:
##            continue
##
##        match = pattern.search(msg.text)
##        if match:
##            teleid = match.group("teleid")
##            procid = match.group("procid")
##            timestamp = match.group("timestamp").strip()
##            teleid_map[teleid].append((procid, timestamp))
##
##    await client.disconnect()
##
##    print("\n📋 Summary of Logins:")
##    for teleid, entries in teleid_map.items():
##        unique_proc_ids = {entry[0] for entry in entries}
##        print(f"\n👤 Telegram ID: {teleid}")
##        print(f"🔢 Total logins: {len(entries)}")
##        print(f"🔁 Unique processor IDs: {len(unique_proc_ids)}")
##        for procid, timestamp in entries:
##            print(f"    🕒 {timestamp} | 💻 {procid}")

# Run it
if __name__ == "__main__":
    import asyncio
    asyncio.run(analyze_logins())

