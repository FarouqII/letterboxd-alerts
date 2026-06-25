import json
import time
from pathlib import Path

import feedparser
import requests

from config import FEED_URL, NTFY_TOPIC

STATE_FILE = Path("state.json")

def loadLastSeen():
    if not STATE_FILE.exists(): return None

    with open(STATE_FILE, "r") as f: data = json.load(f)

    return data.get("lastSeen")

def saveLastSeen(entryID):
    with open(STATE_FILE, "w") as f: json.dump({"lastSeen": entryID}, f)


def sendNotif(title, link):
    requests.post(
        f"https://ntfy.sh/{NTFY_TOPIC}",
        data=f"{title}\n{link}".encode("utf-8"),
        headers={
            "Title": "New Letterboxd Log"
        },
        timeout=10,
    )

def getLatest():
    feed = feedparser.parse(FEED_URL)
    
    if not feed.entries: return None

    return feed.entries[0]


def initialize():
    latest = getLatest()
    print(latest.keys())

    if latest is None: return

    saveLastSeen(latest.id)

    print("Initialized state.")
    print(f"Latest entry: {latest.title}")

def checkFeed():
    latest = getLatest()

    if latest is None: return

    lastSeen = loadLastSeen()

    if latest.id != lastSeen:
        print(f"New log detected: {latest.title}")
        sendNotif(latest.title, latest.link)
        saveLastSeen(latest.id)
    else:
        print("No new entries.")

if __name__ == "__main__":
    checkFeed()