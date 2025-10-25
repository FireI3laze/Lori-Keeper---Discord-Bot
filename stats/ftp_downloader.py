import os
import json
import asyncio
import datetime
import ftputil
from dotenv import load_dotenv

import stats.usercache as usercache

# === FTP / Local Mode Config ===
STATS_DIR = os.path.join("libs", "stats")
load_dotenv()

FTP_ADDRESS = os.getenv("FTP_ADDRESS_DISABLE", "").strip()
FTP_PORT = os.getenv("FTP_PORT", "").strip()
FTP_USERNAME = os.getenv("FTP_USERNAME", "").strip()
FTP_PASS = os.getenv("FTP_PASS", "").strip()
LOCAL_STATS_PATH = os.getenv("LOCAL_STATS_PATH", "").strip() or STATS_DIR

# === FTP Download ===
def download_stats_via_ftp_sync():
    """Download all stats JSONs from FTP server, or load locally if FTP is disabled."""
    os.makedirs(STATS_DIR, exist_ok=True)

    if not FTP_ADDRESS:
        print(f"📁 Using local stats directory: {LOCAL_STATS_PATH}")
        if not os.path.isdir(LOCAL_STATS_PATH):
            print(f"⚠️ Local stats path not found: {LOCAL_STATS_PATH}")
            return

        # Copy local stats into STATS_DIR
        if os.path.abspath(LOCAL_STATS_PATH) != os.path.abspath(STATS_DIR):
            for filename in os.listdir(LOCAL_STATS_PATH):
                if filename.endswith(".json"):
                    src = os.path.join(LOCAL_STATS_PATH, filename)
                    dst = os.path.join(STATS_DIR, filename)
                    if os.path.exists(dst):
                        os.remove(dst)
                    with open(src, "rb") as src_f, open(dst, "wb") as dst_f:
                        dst_f.write(src_f.read())
            print("✅ Local stats synchronized.")
        else:
            print("✅ Using existing local stats directory.")
        refresh_dynamic_stats()
        return

    print(f"🌐 Connecting to FTP: {FTP_ADDRESS}")
    with ftputil.FTPHost(FTP_ADDRESS, FTP_USERNAME, FTP_PASS) as host:
        ftp_stats_path = os.getenv("FTP_STATS_PATH", "/profile_lnreo/Horizon Hollow/stats")
        host.chdir(ftp_stats_path)
        for filename in host.listdir(host.curdir):
            if filename.endswith(".json"):
                local_path = os.path.join(STATS_DIR, filename)
                if os.path.exists(local_path):
                    os.remove(local_path)
                host.download(filename, local_path)
                print(f"⬇️ Downloaded {filename}")
    refresh_dynamic_stats()


# === Daily FTP Task ===
async def daily_ftp_task(bot):
    """Downloads stats daily at a specific time."""
    await bot.wait_until_ready()
    TARGET_HOUR, TARGET_MINUTE = 0, 0
    mode = "FTP" if FTP_ADDRESS else "Local"

    while not bot.is_closed():
        now = datetime.datetime.now()
        next_run = datetime.datetime.combine(
            now.date(), datetime.time(hour=TARGET_HOUR, minute=TARGET_MINUTE)
        )
        #next_run = now + datetime.timedelta(minutes=1) #testing only

        if next_run <= now:
            next_run += datetime.timedelta(days=1)

        seconds_until_run = (next_run - now).total_seconds()
        print(f"⏳ Waiting {int(seconds_until_run)}s until next {mode} update at {TARGET_HOUR:02d}:{TARGET_MINUTE:02d}")
        await asyncio.sleep(seconds_until_run)

        print(f"⬇️ Starting scheduled {mode} update...")
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, download_stats_via_ftp_sync)
        await loop.run_in_executor(None, usercache.load_usercache)
        print(f"✅ {mode} update completed!")

DYNAMIC_STATS = {}

def refresh_dynamic_stats():
    """Scan all local stat JSON files and rebuild DYNAMIC_STATS by category."""
    global DYNAMIC_STATS
    DYNAMIC_STATS.clear()
    os.makedirs(STATS_DIR, exist_ok=True)

    print("🔍 Scanning local stats for dynamic autocomplete...")
    for filename in os.listdir(STATS_DIR):
        if not filename.endswith(".json"):
            continue
        try:
            with open(os.path.join(STATS_DIR, filename), "r", encoding="utf-8") as f:
                data = json.load(f)
            stats_data = data.get("stats", {})
            for category, entries in stats_data.items():
                cat_name = category.split(":")[-1]
                if cat_name not in DYNAMIC_STATS:
                    DYNAMIC_STATS[cat_name] = set()
                for key, value in entries.items():
                    if isinstance(value, int) and value > 0:
                        DYNAMIC_STATS[cat_name].add(key.split(":")[-1])
        except Exception as e:
            print(f"⚠️ Failed to read {filename}: {e}")

    for cat in DYNAMIC_STATS:
        DYNAMIC_STATS[cat] = sorted(DYNAMIC_STATS[cat])

    print(f"✅ Loaded dynamic stats for {len(DYNAMIC_STATS)} categories.")