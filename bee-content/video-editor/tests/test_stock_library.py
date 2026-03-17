"""Tests for stock footage library — SQLite tracker for clip reuse."""

import tempfile
from pathlib import Path

import pytest

from bee_video_editor.services.stock_library import DEFAULT_DB_PATH, StockLibrary


class TestStockLibrary:
    def test_register_clip(self):
        with tempfile.TemporaryDirectory() as d:
            with StockLibrary(db_path=Path(d) / "test.db") as lib:
                lib.register_clip(
                    pexels_id=123,
                    query="aerial farm",
                    path="/proj/stock/aerial-farm-00-pexels-123.mp4",
                    project="my-project",
                )
                clips = lib.list_clips()
            assert len(clips) == 1
            assert clips[0]["pexels_id"] == 123
            assert clips[0]["query"] == "aerial farm"
            assert clips[0]["usage_count"] == 1

    def test_register_same_clip_twice_increments_usage(self):
        with tempfile.TemporaryDirectory() as d:
            with StockLibrary(db_path=Path(d) / "test.db") as lib:
                lib.register_clip(pexels_id=123, query="farm", path="/a.mp4", project="proj1")
                lib.register_clip(pexels_id=123, query="farm", path="/a.mp4", project="proj2")
                clips = lib.list_clips()
            assert len(clips) == 1
            assert clips[0]["usage_count"] == 2

    def test_list_usages(self):
        with tempfile.TemporaryDirectory() as d:
            with StockLibrary(db_path=Path(d) / "test.db") as lib:
                lib.register_clip(pexels_id=100, query="sunset", path="/a.mp4", project="proj-a")
                lib.register_clip(pexels_id=100, query="sunset", path="/a.mp4", project="proj-b")
                usages = lib.list_usages(pexels_id=100)
            assert len(usages) == 2
            projects = {u["project"] for u in usages}
            assert projects == {"proj-a", "proj-b"}

    def test_check_query_warns_on_reuse(self):
        with tempfile.TemporaryDirectory() as d:
            with StockLibrary(db_path=Path(d) / "test.db") as lib:
                lib.register_clip(pexels_id=100, query="aerial farm", path="/a.mp4", project="proj-a")
                matches = lib.check_query("aerial farm")
            assert len(matches) == 1
            assert matches[0]["pexels_id"] == 100

    def test_check_query_partial_match(self):
        with tempfile.TemporaryDirectory() as d:
            with StockLibrary(db_path=Path(d) / "test.db") as lib:
                lib.register_clip(pexels_id=100, query="aerial farm dusk", path="/a.mp4", project="p")
                lib.register_clip(pexels_id=200, query="courtroom interior", path="/b.mp4", project="p")
                matches = lib.check_query("farm")
            assert len(matches) == 1
            assert matches[0]["pexels_id"] == 100

    def test_check_query_no_matches(self):
        with tempfile.TemporaryDirectory() as d:
            with StockLibrary(db_path=Path(d) / "test.db") as lib:
                matches = lib.check_query("nonexistent")
            assert matches == []

    def test_list_clips_empty(self):
        with tempfile.TemporaryDirectory() as d:
            with StockLibrary(db_path=Path(d) / "test.db") as lib:
                assert lib.list_clips() == []

    def test_default_db_path(self):
        assert "stock-library.db" in str(DEFAULT_DB_PATH)

    def test_context_manager(self):
        with tempfile.TemporaryDirectory() as d:
            with StockLibrary(db_path=Path(d) / "test.db") as lib:
                lib.register_clip(pexels_id=1, query="test", path="/x.mp4", project="p")
            # Connection closed after with block — no error
