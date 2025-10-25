import os
import json

from dotenv import load_dotenv
load_dotenv()

USERCACHE_PATH = os.path.expanduser(os.getenv("USERCACHE_PATH", "usercache.json"))
USERCACHE = {}
UUID_CACHE = {}

def load_usercache(path: str | None = None):
    global USERCACHE
    p = path or USERCACHE_PATH
    print(f"🔍 Loading usercache from: {p}")  # DEBUG
    USERCACHE.clear()
    if not os.path.isfile(p):
        print("⚠️ Usercache file not found!")
        return
    try:
        with open(p, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        for entry in data:
            uuid = entry.get("uuid")
            name = entry.get("name")
            if uuid and name:
                USERCACHE[uuid] = name
        print(f"✅ Loaded {len(USERCACHE)} entries from usercache")
    except Exception as e:
        print(f"⚠️ Failed to load usercache: {e}")
        return


async def fetch_name(uuid):
    if uuid in UUID_CACHE:
        return UUID_CACHE[uuid]

    # Prüfe zuerst den lokalen Usercache direkt
    name = USERCACHE.get(uuid)
    if name:
        UUID_CACHE[uuid] = name
        return name

    # Bedrock-Fallback: Bedrock-UUID erkennen und Namen generieren
    if uuid.startswith("00000000-0000-0000-0009-"):
        name = f"Bedrock-{uuid[-4:]}"

    # Wenn nichts gefunden, Fallback auf "Unknown"
    else:
        name = "Unknown"

    UUID_CACHE[uuid] = name
    return name



