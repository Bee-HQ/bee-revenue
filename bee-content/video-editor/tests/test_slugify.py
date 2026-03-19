from bee_video_editor.formats.slugify import slugify, unique_slug

def test_slugify_simple(): assert slugify("Cold Open") == "cold-open"
def test_slugify_special_chars(): assert slugify("The 911 Call — Emergency") == "the-911-call-emergency"
def test_slugify_collapses_hyphens(): assert slugify("Act 1: The Night Of") == "act-1-the-night-of"
def test_slugify_strips_edges(): assert slugify("  --Hello World--  ") == "hello-world"
def test_unique_slug_no_collision():
    seen = set()
    assert unique_slug("Cold Open", seen) == "cold-open"
    assert "cold-open" in seen
def test_unique_slug_with_collision():
    seen = {"establishing-shot"}
    assert unique_slug("Establishing Shot", seen) == "establishing-shot-2"
def test_unique_slug_multiple_collisions():
    seen = {"shot", "shot-2", "shot-3"}
    assert unique_slug("Shot", seen) == "shot-4"
