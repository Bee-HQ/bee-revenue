"""Niche group management service."""

from ..storage.db import Database


def create(db: Database, name: str, channel_ids: list[str]) -> int:
    """Create a new niche group with the given channels."""
    return db.create_group(name, channel_ids)


def list_all(db: Database) -> list[dict]:
    """List all niche groups with channel counts."""
    return db.list_groups()


def show(db: Database, name: str) -> list[dict]:
    """Show channels in a niche group."""
    return db.get_group_channels(name)


def add_channels(db: Database, name: str, channel_ids: list[str]):
    """Add channels to an existing niche group."""
    db.add_to_group(name, channel_ids)


def remove_channels(db: Database, name: str, channel_ids: list[str]):
    """Remove channels from a niche group."""
    db.remove_from_group(name, channel_ids)
