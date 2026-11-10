# -*- coding: utf-8 -*-
"""
Fetch X video cover images (posters) for every entry in data/videos.json.

Uses the public syndication endpoint (no auth) to resolve each status id to its
video poster, then downloads a resized WebP copy into assets/posters/<slug>.webp
and records it back into data/videos.json as "poster".

Idempotent: existing poster files are not re-downloaded.

Usage:  python tools/fetch_posters.py
"""

import io
import json
import math
import os
import time
import urllib.request

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIDEOS = os.path.join(ROOT, "data", "videos.json")
OUT_DIR = os.path.join(ROOT, "assets", "posters")
MAX_WIDTH = 720

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}


def token(tid):
    return str((int(tid) / 1e15) * math.pi).replace(".", "")


def fetch_json(url, retries=3):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.load(r)
        except Exception as e:
            if i == retries - 1:
                raise
            time.sleep(1.5 * (i + 1))


def fetch_bytes(url, retries=3):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read()
        except Exception:
            if i == retries - 1:
                raise
            time.sleep(1.5 * (i + 1))


def poster_url(tweet):
    v = tweet.get("video") or {}
    if v.get("poster"):
        return v["poster"]
    for m in tweet.get("mediaDetails") or []:
        if m.get("media_url_https"):
            return m["media_url_https"]
    for p in tweet.get("photos") or []:
        if p.get("url"):
            return p["url"]
    return None


def save_webp(raw, path):
    im = Image.open(io.BytesIO(raw))
    if im.mode not in ("RGB", "L"):
        im = im.convert("RGB")
    if im.width > MAX_WIDTH:
        im = im.resize((MAX_WIDTH, int(im.height * MAX_WIDTH / im.width)), Image.LANCZOS)
    im.save(path, "WEBP", quality=80, method=4)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(VIDEOS, encoding="utf-8") as f:
        videos = json.load(f)

    ok, failed = 0, []
    for v in videos:
        slug, tid = v["slug"], v["post_url"].rsplit("/", 1)[-1]
        out = os.path.join(OUT_DIR, slug + ".webp")
        rel = "assets/posters/%s.webp" % slug
        if os.path.exists(out) and v.get("poster") == rel:
            ok += 1
            continue
        try:
            tweet = fetch_json(
                "https://cdn.syndication.twimg.com/tweet-result?id=%s&token=%s&lang=en"
                % (tid, token(tid))
            )
            url = poster_url(tweet)
            if not url:
                raise RuntimeError("no poster in syndication payload")
            raw = fetch_bytes(url)
            save_webp(raw, out)
            v["poster"] = rel
            ok += 1
            print("ok   %-28s %s" % (slug, url[:80]))
        except Exception as e:
            v.pop("poster", None)
            failed.append((slug, str(e)[:60]))
            print("FAIL %-28s %s" % (slug, str(e)[:60]))
        time.sleep(0.25)

    with open(VIDEOS, "w", encoding="utf-8", newline="\n") as f:
        json.dump(videos, f, ensure_ascii=False, indent=1)
        f.write("\n")

    print("\n%d/%d posters saved" % (ok, len(videos)))
    if failed:
        print("failed:", ", ".join(s for s, _ in failed))


if __name__ == "__main__":
    main()
