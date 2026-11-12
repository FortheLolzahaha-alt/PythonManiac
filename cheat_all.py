import json
import os
import shutil
import time
from pathlib import Path

APPDATA = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
SAVE_DIR = APPDATA / "Godot" / "app_userdata" / "Love Maniac" / "save"

META_FILE = SAVE_DIR / "meta.json"
SLOT_FILE = SAVE_DIR / "slot_1.json"   # change to slot_0.json / slot_2.json if needed

TARGET_GOLD = 999999999
CHECK_INTERVAL = 0.5                   # seconds between gold checks

# Booleans listed here are left untouched (gameplay modifier, not an unlock)
EXCLUDE = {"no_hit_enabled"}

ALL_COSTUMES = ["pale_chara", "butcher", "solver", "zukafu"]


# ---------- Part 1: unlock everything (runs once) ----------

def set_all_true(node):
    if isinstance(node, dict):
        for key, value in node.items():
            if isinstance(value, bool):
                if key not in EXCLUDE:
                    node[key] = True
            else:
                set_all_true(value)
    elif isinstance(node, list):
        for item in node:
            set_all_true(item)


def unlock_everything():
    if not META_FILE.exists():
        print(f"meta.json not found: {META_FILE}")
        return

    backup = META_FILE.with_suffix(".json.bak")
    shutil.copy2(META_FILE, backup)
    print(f"Backup saved to: {backup}")

    with open(META_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    set_all_true(data)

    costumes = data.get("unlocked_costumes", [])
    for name in ALL_COSTUMES:
        if name not in costumes:
            costumes.append(name)
    data["unlocked_costumes"] = costumes

    with open(META_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent="\t", ensure_ascii=False)

    print("Unlocked all scenes, settings and costumes.")


# ---------- Part 2: gold lock (keeps running) ----------

def read_save():
    try:
        with open(SLOT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def write_save(data):
    tmp = SLOT_FILE.with_suffix(".json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent="\t", ensure_ascii=False)
    os.replace(tmp, SLOT_FILE)


def gold_lock():
    print(f"Watching: {SLOT_FILE}")
    print(f"Gold will be reset to {TARGET_GOLD} whenever it drops below that. Ctrl+C to stop.")

    while True:
        data = read_save()
        if data is not None:
            gold = data.get("gold")
            if isinstance(gold, (int, float)) and gold < TARGET_GOLD:
                data["gold"] = TARGET_GOLD
                try:
                    write_save(data)
                    print(f"Gold was {gold}, reset to {TARGET_GOLD}")
                except OSError as e:
                    print(f"Could not write save: {e}")
        time.sleep(CHECK_INTERVAL)


def main():
    unlock_everything()
    print()
    gold_lock()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.")
