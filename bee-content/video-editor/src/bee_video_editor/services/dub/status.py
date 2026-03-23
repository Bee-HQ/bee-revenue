from __future__ import annotations
import json
from pathlib import Path
from bee_video_editor.services.dub.models import SegmentState


class StatusTracker:
    def __init__(self, path: Path):
        self.path = path
        if path.exists():
            self._data = json.loads(path.read_text())
        else:
            self._data = {}
            self._save()

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self._data, indent=2))

    def _key(self, segment_id: str, step: str) -> str:
        return f"{segment_id}:{step}"

    def set(self, segment_id: str, step: str, state: SegmentState, error: str | None = None) -> None:
        key = self._key(segment_id, step)
        self._data[key] = {"state": state.value, "error": error}
        self._save()

    def get(self, segment_id: str, step: str) -> SegmentState:
        key = self._key(segment_id, step)
        entry = self._data.get(key)
        if entry is None:
            return SegmentState.PENDING
        return SegmentState(entry["state"])

    def get_error(self, segment_id: str, step: str) -> str | None:
        key = self._key(segment_id, step)
        entry = self._data.get(key)
        return entry.get("error") if entry else None

    def incomplete(self, step: str, segment_ids: list[str]) -> list[str]:
        return [sid for sid in segment_ids if self.get(sid, step) != SegmentState.COMPLETED]

    def retry_failed(self, step: str) -> None:
        for key, entry in list(self._data.items()):
            if key.endswith(f":{step}") and entry["state"] == SegmentState.FAILED.value:
                entry["state"] = SegmentState.PENDING.value
                entry["error"] = None
        self._save()
