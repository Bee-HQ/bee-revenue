"""YouTube search and suggestions fetcher."""

import json
import urllib.request
import urllib.parse

import scrapetube


def search_channels(keyword: str, max_results: int = 20) -> list[dict]:
    """Search YouTube for channels matching keyword. Returns basic channel info."""
    try:
        videos = scrapetube.get_search(query=keyword, limit=max_results * 3)
        seen_channels = {}
        for v in videos:
            ch_id = v.get("channelId") or ""
            if not ch_id:
                # Try nested structure
                owner_text = v.get("ownerText", {})
                runs = owner_text.get("runs", [{}]) if isinstance(owner_text, dict) else [{}]
                if runs:
                    nav = runs[0].get("navigationEndpoint", {})
                    browse = nav.get("browseEndpoint", {})
                    ch_id = browse.get("browseId", "")

            ch_name = ""
            owner_text = v.get("ownerText", {})
            if isinstance(owner_text, dict):
                runs = owner_text.get("runs", [{}])
                if runs:
                    ch_name = runs[0].get("text", "")

            if ch_id and ch_id not in seen_channels:
                seen_channels[ch_id] = {"id": ch_id, "name": ch_name}
            if len(seen_channels) >= max_results:
                break
        return list(seen_channels.values())
    except Exception:
        return []


def fetch_youtube_suggestions(keyword: str) -> list[str]:
    """Fetch YouTube search autocomplete suggestions."""
    try:
        encoded = urllib.parse.quote(keyword)
        url = f"http://suggestqueries.google.com/complete/search?client=youtube&ds=yt&q={encoded}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read().decode("utf-8")
            # Response is JSONP: window.google.ac.h(...)
            json_str = raw[raw.index("(") + 1 : raw.rindex(")")]
            data = json.loads(json_str)
            return [item[0] for item in data[1]] if len(data) > 1 else []
    except Exception:
        return []
