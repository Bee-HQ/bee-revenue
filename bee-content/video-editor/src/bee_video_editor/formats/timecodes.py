"""Timecode parsing and formatting utilities."""
from __future__ import annotations

def parse_header_tc(tc: str) -> float:
    parts = tc.strip().split(":")
    if len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    if len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    raise ValueError(f"Invalid header timecode: {tc!r}")

def format_header_tc(seconds: float) -> str:
    total = int(seconds)
    h, m, s = total // 3600, (total % 3600) // 60, total % 60
    return f"{h}:{m:02d}:{s:02d}" if h > 0 else f"{m}:{s:02d}"

def parse_precise_tc(tc: str) -> float:
    parts = tc.strip().split(":")
    if len(parts) != 3:
        raise ValueError(f"Invalid precise timecode: {tc!r}")
    return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])

def format_precise_tc(seconds: float) -> str:
    h = int(seconds) // 3600
    m = (int(seconds) % 3600) // 60
    s = seconds - h * 3600 - m * 60
    return f"{h:02d}:{m:02d}:{s:06.3f}"

def tc_to_seconds(tc: str) -> float:
    return parse_precise_tc(tc) if "." in tc else parse_header_tc(tc)
