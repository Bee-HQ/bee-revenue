"""Tests for graphics generation (Pillow-based, no FFmpeg needed)."""

import tempfile
from pathlib import Path

import pytest
from PIL import Image

from bee_video_editor.processors.graphics import (
    black_frame,
    financial_card,
    lower_third,
    mugshot_card,
    quote_card,
    text_overlay,
    timeline_marker,
)


@pytest.fixture
def tmp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


class TestLowerThird:
    def test_creates_file(self, tmp_dir):
        out = lower_third("Alex Murdaugh", "Defendant", tmp_dir / "lt.png")
        assert out.exists()

    def test_correct_dimensions(self, tmp_dir):
        out = lower_third("Alex Murdaugh", "Defendant", tmp_dir / "lt.png")
        img = Image.open(out)
        assert img.size == (1920, 1080)

    def test_rgba_mode(self, tmp_dir):
        out = lower_third("Alex Murdaugh", "Defendant", tmp_dir / "lt.png")
        img = Image.open(out)
        assert img.mode == "RGBA"

    def test_has_transparency(self, tmp_dir):
        out = lower_third("Alex Murdaugh", "Defendant", tmp_dir / "lt.png")
        img = Image.open(out)
        # Top-left corner should be transparent
        pixel = img.getpixel((0, 0))
        assert pixel[3] == 0  # alpha = 0

    def test_bar_area_opaque(self, tmp_dir):
        out = lower_third("Alex Murdaugh", "Defendant", tmp_dir / "lt.png")
        img = Image.open(out)
        # Bottom-left should have the bar
        pixel = img.getpixel((30, 950))
        assert pixel[3] > 0  # not fully transparent


class TestTimelineMarker:
    def test_creates_file(self, tmp_dir):
        out = timeline_marker("June 7, 2021", "The Night of the Murders", tmp_dir / "tm.png")
        assert out.exists()

    def test_correct_dimensions(self, tmp_dir):
        out = timeline_marker("June 7, 2021", "Description", tmp_dir / "tm.png")
        img = Image.open(out)
        assert img.size == (1920, 1080)

    def test_rgb_mode(self, tmp_dir):
        out = timeline_marker("June 7, 2021", "Description", tmp_dir / "tm.png")
        img = Image.open(out)
        assert img.mode == "RGB"


class TestQuoteCard:
    def test_creates_file(self, tmp_dir):
        out = quote_card(
            "I did him so bad.",
            "Alex Murdaugh",
            tmp_dir / "quote.png",
        )
        assert out.exists()

    def test_long_quote_wraps(self, tmp_dir):
        long_quote = "This is a very long quote that should wrap across multiple lines " * 3
        out = quote_card(long_quote, "Speaker", tmp_dir / "quote.png")
        assert out.exists()
        img = Image.open(out)
        assert img.size == (1920, 1080)


class TestFinancialCard:
    def test_creates_file(self, tmp_dir):
        out = financial_card("$8,800,000+", "Stolen from clients", tmp_dir / "fin.png")
        assert out.exists()


class TestTextOverlay:
    def test_creates_file(self, tmp_dir):
        out = text_overlay("Test Text", tmp_dir / "text.png")
        assert out.exists()

    def test_transparent_background(self, tmp_dir):
        out = text_overlay("Test", tmp_dir / "text.png")
        img = Image.open(out)
        assert img.mode == "RGBA"

    def test_positions(self, tmp_dir):
        for pos in ["center", "top", "bottom"]:
            out = text_overlay("Test", tmp_dir / f"text_{pos}.png", position=pos)
            assert out.exists()


class TestMugshotCard:
    def test_mugshot_card(self, tmp_dir):
        photo = tmp_dir / "mugshot.png"
        Image.new("RGB", (400, 500), (128, 128, 128)).save(str(photo))

        out = tmp_dir / "mugshot-card.png"
        result = mugshot_card(
            photo_path=photo,
            charges=["First-degree murder", "Tampering with evidence"],
            sentence="Life without parole",
            output_path=out,
        )
        assert result.exists()
        img = Image.open(str(result))
        assert img.size == (1920, 1080)

    def test_mugshot_card_missing_photo(self, tmp_dir):
        out = tmp_dir / "mugshot-no-photo.png"
        result = mugshot_card(
            photo_path=tmp_dir / "nonexistent.png",
            charges=["Grand larceny"],
            sentence="5 years",
            output_path=out,
        )
        assert result.exists()
        img = Image.open(str(result))
        assert img.size == (1920, 1080)


class TestQuoteCardAccents:
    def test_quote_card_accents(self, tmp_dir):
        for accent in ["red", "teal", "gold"]:
            out = tmp_dir / f"quote-{accent}.png"
            result = quote_card(
                quote="Test quote",
                speaker="Speaker",
                output_path=out,
                accent=accent,
            )
            assert result.exists()
            img = Image.open(str(result))
            assert img.size == (1920, 1080)

    def test_quote_card_default_accent(self, tmp_dir):
        out = tmp_dir / "quote-default.png"
        result = quote_card("Test", "Speaker", out)
        assert result.exists()

    def test_quote_card_unknown_accent_falls_back(self, tmp_dir):
        out = tmp_dir / "quote-unknown.png"
        result = quote_card("Test", "Speaker", out, accent="purple")
        assert result.exists()


class TestBlackFrame:
    def test_creates_file(self, tmp_dir):
        out = black_frame(tmp_dir / "black.png")
        assert out.exists()

    def test_is_black(self, tmp_dir):
        out = black_frame(tmp_dir / "black.png")
        img = Image.open(out)
        pixel = img.getpixel((960, 540))
        assert pixel == (0, 0, 0)


class TestTextChat:
    def test_basic_imessage(self, tmp_path):
        from bee_video_editor.processors.graphics import text_chat, ChatMessage
        msgs = [
            ChatMessage("Hey, are you there?", sender=False),
            ChatMessage("Yeah, what's up?", sender=True),
        ]
        out = tmp_path / "chat.png"
        result = text_chat(msgs, out)
        assert result.exists()
        img = Image.open(str(result))
        assert img.size == (1920, 1080)

    def test_sms_platform(self, tmp_path):
        from bee_video_editor.processors.graphics import text_chat, ChatMessage
        msgs = [ChatMessage("Test", sender=True)]
        out = tmp_path / "sms.png"
        result = text_chat(msgs, out, platform="sms")
        assert result.exists()

    def test_empty_messages(self, tmp_path):
        from bee_video_editor.processors.graphics import text_chat
        out = tmp_path / "empty.png"
        result = text_chat([], out)
        assert result.exists()


class TestSocialPost:
    def test_facebook_post(self, tmp_path):
        from bee_video_editor.processors.graphics import social_post, SocialPost
        post = SocialPost(username="John Doe", text="This is a test post", platform="facebook")
        out = tmp_path / "fb.png"
        result = social_post(post, out)
        assert result.exists()
        img = Image.open(str(result))
        assert img.size == (1920, 1080)

    def test_instagram_post(self, tmp_path):
        from bee_video_editor.processors.graphics import social_post, SocialPost
        post = SocialPost(username="user", text="Content", platform="instagram")
        out = tmp_path / "ig.png"
        result = social_post(post, out)
        assert result.exists()

    def test_with_highlight(self, tmp_path):
        from bee_video_editor.processors.graphics import social_post, SocialPost
        post = SocialPost(username="user", text="I did it", platform="twitter", highlight_text="did it")
        out = tmp_path / "tw.png"
        result = social_post(post, out)
        assert result.exists()


class TestNewsMontage:
    def test_basic_headlines(self, tmp_path):
        from bee_video_editor.processors.graphics import news_montage
        headlines = ["Murder Suspect Arrested", "Trial Date Set for January", "Key Evidence Found"]
        out = tmp_path / "news.png"
        result = news_montage(headlines, out)
        assert result.exists()
        img = Image.open(str(result))
        assert img.size == (1920, 1080)

    def test_single_headline(self, tmp_path):
        from bee_video_editor.processors.graphics import news_montage
        out = tmp_path / "single.png"
        result = news_montage(["Breaking News"], out)
        assert result.exists()

    def test_empty_headlines(self, tmp_path):
        from bee_video_editor.processors.graphics import news_montage
        out = tmp_path / "empty.png"
        result = news_montage([], out)
        assert result.exists()


class TestEvidenceBoard:
    def test_basic_board(self, tmp_path):
        from bee_video_editor.processors.graphics import evidence_board, BoardPerson, BoardConnection
        people = [
            BoardPerson("Alex"),
            BoardPerson("Maggie"),
            BoardPerson("Paul"),
        ]
        connections = [
            BoardConnection("Alex", "Maggie", "married"),
            BoardConnection("Alex", "Paul", "father"),
        ]
        out = tmp_path / "board.png"
        result = evidence_board(people, connections, out)
        assert result.exists()
        img = Image.open(str(result))
        assert img.size == (1920, 1080)

    def test_with_photo(self, tmp_path):
        from bee_video_editor.processors.graphics import evidence_board, BoardPerson, BoardConnection
        photo = tmp_path / "photo.png"
        Image.new("RGB", (200, 250), (128, 128, 128)).save(str(photo))
        people = [BoardPerson("Alex", photo_path=photo), BoardPerson("Maggie")]
        connections = [BoardConnection("Alex", "Maggie", "married")]
        out = tmp_path / "board.png"
        result = evidence_board(people, connections, out)
        assert result.exists()

    def test_no_connections(self, tmp_path):
        from bee_video_editor.processors.graphics import evidence_board, BoardPerson
        people = [BoardPerson("Alex"), BoardPerson("Maggie")]
        out = tmp_path / "board.png"
        result = evidence_board(people, [], out)
        assert result.exists()


class TestFlowDiagram:
    def test_basic_flow(self, tmp_path):
        from bee_video_editor.processors.graphics import flow_diagram, FlowNode, FlowArrow
        nodes = [
            FlowNode("Alex Murdaugh"),
            FlowNode("Forge Account"),
            FlowNode("Satterfield Family"),
        ]
        arrows = [
            FlowArrow("Alex Murdaugh", "Forge Account", "$4.3M", color="red"),
            FlowArrow("Forge Account", "Satterfield Family", "$0", color="red"),
        ]
        out = tmp_path / "flow.png"
        result = flow_diagram(nodes, arrows, out)
        assert result.exists()
        img = Image.open(str(result))
        assert img.size == (1920, 1080)

    def test_circle_nodes(self, tmp_path):
        from bee_video_editor.processors.graphics import flow_diagram, FlowNode, FlowArrow
        nodes = [FlowNode("A", "circle"), FlowNode("B", "circle")]
        arrows = [FlowArrow("A", "B", "connection", color="teal")]
        out = tmp_path / "circles.png"
        result = flow_diagram(nodes, arrows, out)
        assert result.exists()

    def test_empty_diagram(self, tmp_path):
        from bee_video_editor.processors.graphics import flow_diagram
        out = tmp_path / "empty.png"
        result = flow_diagram([], [], out)
        assert result.exists()

    def test_no_arrows(self, tmp_path):
        from bee_video_editor.processors.graphics import flow_diagram, FlowNode
        nodes = [FlowNode("Standalone")]
        out = tmp_path / "no_arrows.png"
        result = flow_diagram(nodes, [], out)
        assert result.exists()


class TestTimelineSequence:
    def test_basic_timeline(self, tmp_path):
        from bee_video_editor.processors.graphics import timeline_sequence, TimelineEvent
        events = [
            TimelineEvent("Feb 2019", "Boat Crash", active=True),
            TimelineEvent("June 2021", "Double Murder", active=True, current=True),
            TimelineEvent("Jan 2023", "Trial Begins", active=False),
            TimelineEvent("March 2023", "Verdict", active=False),
        ]
        out = tmp_path / "timeline.png"
        result = timeline_sequence(events, out, title="Murdaugh Case Timeline")
        assert result.exists()
        img = Image.open(str(result))
        assert img.size == (1920, 1080)

    def test_single_event(self, tmp_path):
        from bee_video_editor.processors.graphics import timeline_sequence, TimelineEvent
        events = [TimelineEvent("2021", "Event", active=True, current=True)]
        out = tmp_path / "single.png"
        result = timeline_sequence(events, out)
        assert result.exists()

    def test_empty_timeline(self, tmp_path):
        from bee_video_editor.processors.graphics import timeline_sequence
        out = tmp_path / "empty.png"
        result = timeline_sequence([], out)
        assert result.exists()

    def test_all_future(self, tmp_path):
        from bee_video_editor.processors.graphics import timeline_sequence, TimelineEvent
        events = [
            TimelineEvent("2024", "Event A", active=False),
            TimelineEvent("2025", "Event B", active=False),
        ]
        out = tmp_path / "future.png"
        result = timeline_sequence(events, out)
        assert result.exists()

    def test_with_title(self, tmp_path):
        from bee_video_editor.processors.graphics import timeline_sequence, TimelineEvent
        events = [TimelineEvent("2021", "Test", active=True)]
        out = tmp_path / "titled.png"
        result = timeline_sequence(events, out, title="Case Timeline")
        assert result.exists()
