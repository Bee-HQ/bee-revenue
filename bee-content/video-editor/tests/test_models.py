"""Tests for data models (models_storyboard — kept for migration compatibility)."""

import pytest

from bee_video_editor.models_storyboard import ChecklistItem, Storyboard


class TestChecklistItem:
    def test_checklist_item(self):
        item = ChecklistItem(text="Generate TTS narration", checked=True, category="audio")
        assert item.text == "Generate TTS narration"
        assert item.checked is True
        assert item.category == "audio"

    def test_checklist_item_unchecked(self):
        item = ChecklistItem(text="Export final video", checked=False, category="post")
        assert item.checked is False


class TestStoryboardMetadata:
    def test_storyboard_metadata_defaults(self):
        sb = Storyboard(title="Test")
        assert sb.total_duration is None
        assert sb.resolution is None
        assert sb.format is None
        assert sb.pre_production == []
        assert sb.post_checklist == []

    def test_storyboard_with_metadata(self):
        sb = Storyboard(
            title="Alex Murdaugh",
            total_duration="55:00",
            resolution="1080p",
            format="MP4",
            pre_production=[
                ChecklistItem(text="Generate TTS", checked=True, category="audio"),
                ChecklistItem(text="Create lower thirds", checked=False, category="graphics"),
            ],
            post_checklist=[
                ChecklistItem(text="Color grade", checked=False, category="post"),
            ],
        )
        assert sb.total_duration == "55:00"
        assert sb.resolution == "1080p"
        assert sb.format == "MP4"
        assert len(sb.pre_production) == 2
        assert sb.pre_production[0].text == "Generate TTS"
        assert sb.pre_production[0].checked is True
        assert sb.pre_production[1].category == "graphics"
        assert len(sb.post_checklist) == 1
        assert sb.post_checklist[0].text == "Color grade"
