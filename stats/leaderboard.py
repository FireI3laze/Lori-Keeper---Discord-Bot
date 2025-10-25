# stats/leaderboard.py
import os
import json
import concurrent.futures
import asyncio
import aiohttp
from typing import List, Tuple

from stats import constants, usercache

# Pfad-Default (kann überschrieben werden von caller)
STATS_DIR = os.path.join("libs", "stats")

# Local cache for UUID -> name lookups (Mojang or local usercache)
UUID_CACHE = {}

# USERCACHE wird vom außen bereitgestellten loader befüllt (stats.usercache)
USERCACHE = {}

# distance alias mapping is expected to be imported by callers if needed
def get_stat_value(data: dict, stat: str) -> int:
    """Extract stat value from a JSON file. Expects stat like 'minecraft:mined:minecraft:stone' or aliases."""
    parts = stat.split(":")
    if len(parts) == 4:
        category, key = f"{parts[0]}:{parts[1]}", f"{parts[2]}:{parts[3]}"
    elif len(parts) == 3:
        category, key = f"{parts[0]}:{parts[1]}", parts[2]
        if not key.startswith("minecraft:"):
            key = f"minecraft:{key}"
    elif len(parts) == 2:
        category, key = f"minecraft:{parts[0]}", f"minecraft:{parts[1]}"
    else:
        return 0

    value = data.get("stats", {}).get(category, {}).get(key)
    if value is None:
        return 0
    # distances saved as cm in vanilla -> convert to blocks (~/100)
    if "_one_cm" in key:
        return round(value / 100)
    return value

async def build_leaderboard(stat: str, stats_dir: str | None = None) -> List[Tuple[str, int]]:
    """Return sorted list of (player_name, value) descending."""
    sd = stats_dir or STATS_DIR
    files = [os.path.join(sd, f) for f in os.listdir(sd) if f.endswith(".json")]
    results = []

    # use ThreadPool for json.load (IO)
    with concurrent.futures.ThreadPoolExecutor() as ex:
        def load_file(fp):
            with open(fp, "r", encoding="utf-8") as fh:
                return json.load(fh), os.path.basename(fp).replace(".json", "")
        loaded = list(ex.map(load_file, files))

    uuids = []
    values_by_uuid = {}
    for data, file_uuid in loaded:
        val = get_stat_value(data, stat)
        values_by_uuid[file_uuid] = val
        uuids.append(file_uuid)

    # resolve names async
    async with aiohttp.ClientSession() as session:
        names = await asyncio.gather(*(usercache.fetch_name(u) for u in uuids))

    final = [(n, values_by_uuid[u]) for u, n in zip(uuids, names)]
    final.sort(key=lambda x: x[1], reverse=True)
    return final

def escape_discord(text: str) -> str:
    return text.replace("_", "\\_")

def get_surrounding_leaderboard(leaderboard, target: str, before: int = 5, after: int = 5):
    try:
        rank_index = int(target) - 1
        if rank_index < 0 or rank_index >= len(leaderboard):
            return [], 0
        start, end = max(0, rank_index - before), min(len(leaderboard), rank_index + after + 1)
        return leaderboard[start:end], start + 1
    except ValueError:
        target_index = next((i for i, (n, _) in enumerate(leaderboard) if n.lower() == target.lower()), None)
        if target_index is None:
            return [], 0
        start, end = max(0, target_index - before), min(len(leaderboard), target_index + after + 1)
        return leaderboard[start:end], start + 1

def load_all_stat_keys(stats_dir: str) -> list:
    """Scan all jsons and return set of stat keys found (category:key)."""
    keys = set()
    for filename in os.listdir(stats_dir):
        if not filename.endswith(".json"):
            continue
        try:
            with open(os.path.join(stats_dir, filename), "r", encoding="utf-8") as fh:
                data = json.load(fh)
            for category, entries in data.get("stats", {}).items():
                for k in entries.keys():
                    keys.add(f"{category}:{k}")
        except Exception:
            continue
    return sorted(keys)

def format_leaderboard(stat_name: str, player_name: str, leaderboard: list[tuple[str, int]], start_rank: int = 1):
    parts = stat_name.split(":")
    category, key = ("unknown", stat_name)
    if len(parts) == 4:
        category, key = parts[1], parts[3]
    elif len(parts) == 3:
        category, key = parts[1], parts[2].replace("minecraft:", "")
    elif len(parts) == 2:
        category, key = parts[0], parts[1]

    # Check if this is a distance stat and map to friendly name
    stat_is_distance = key in constants.FRIENDLY_DISTANCE_NAMES
    if stat_is_distance:
        display_stat = constants.FRIENDLY_DISTANCE_NAMES[key] + " (in Blocks)"
    else:
        display_stat = f"{key.replace('_', ' ').title()}{'' if category.lower() == 'custom' else f' {category.title()}'}"

    emoji = constants.CATEGORY_EMOJIS.get(category, "🏆")

    medals = ["🥇", "🥈", "🥉"]
    around_display = f"#{player_name}" if player_name.isdigit() else player_name

    lines = [f"{emoji} **Leaderboard – {display_stat}**", f"Around: **{around_display}**", ""]
    for i, (name, value) in enumerate(leaderboard, start=start_rank):
        rank_emoji = medals[i - 1] if i <= len(medals) else (f"{i}\N{combining enclosing keycap}" if i < 10 else f"#{i}")
        lines.append(f"{rank_emoji} {escape_discord(name)} — **{value}**\n")
    return "\n".join(lines)