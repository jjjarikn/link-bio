from flask import Flask, request, redirect, abort, send_file
import datetime, csv
from pathlib import Path

app = Flask(__name__)

LINKS = {
    "tg": "https://t.me/username",
    "vk": "https://vk.com/username",
}

LOG_FILE = Path("events.csv")
INDEX_FILE = Path("index.html")


def get_device(ua: str) -> str:
    ua = ua or ""
    if any(x in ua for x in ["iPhone", "iPad", "iPod"]):
        return "ios"
    if "Android" in ua:
        return "android"
    return "desktop"


def get_browser_type(ua: str, ref: str) -> str:
    text = (ua + " " + (ref or "")).lower()
    return "tiktok_inapp" if any(x in text for x in ["tiktok", "musical.ly", "bytedance", "trill"]) else "external_browser"


def append_row(data: dict):
    new_file = not LOG_FILE.exists()
    with LOG_FILE.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["timestamp", "target", "link_id", "device", "browser_type", "country", "ip", "user_agent", "referrer"],
        )
        if new_file:
            writer.writeheader()
        writer.writerow(data)


@app.get("/")
def index():
    return send_file(INDEX_FILE)


@app.get("/go/<target>")
def go(target):
    if target not in LINKS:
        abort(404)
    ua = request.headers.get("User-Agent", "")
    ref = request.headers.get("Referer", "")
    ip = request.headers.get("CF-Connecting-IP") or request.headers.get("X-Forwarded-For", "").split(",")[0].strip() or request.remote_addr or ""
    payload = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "target": target,
        "link_id": f"{target}_main",
        "device": get_device(ua),
        "browser_type": get_browser_type(ua, ref),
        "country": "",
        "ip": ip,
        "user_agent": ua[:1000],
        "referrer": ref[:1000],
    }
    append_row(payload)
    return redirect(LINKS[target], code=302)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
