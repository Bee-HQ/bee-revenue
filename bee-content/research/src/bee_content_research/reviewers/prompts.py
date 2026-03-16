"""Pillar-specific prompts for anime/manga/manhwa script review.

Each prompt is designed for a focused, single-pillar analysis pass.
Prompts reference known archetypes from the anime YouTube space:
- Editorial Essay (Living Deadman/OniMaru): provocative takes, personal connection
- Power Fantasy Recap (Tobs Manhwa): "When..." hooks, isekai premises, power scaling
- Explainer/Analysis (arikendo/Sock Sensei): educational, comprehensive breakdowns
"""

SYSTEM_PROMPT = """You are a YouTube script analyst specializing in anime, manga, and manhwa content.
You score scripts on specific quality dimensions and provide actionable feedback.
You always respond with valid JSON only — no markdown, no commentary outside the JSON."""

# Weights for each pillar (must sum to 1.0)
PILLAR_WEIGHTS = {
    "hook": 0.20,
    "pacing": 0.20,
    "storytelling": 0.15,
    "engagement": 0.15,
    "narration": 0.10,
    "seo": 0.10,
    "niche_fit": 0.10,
}

HOOK_ANALYSIS_PROMPT = """Analyze the HOOK (first ~30 seconds / first 3-5 sentences) of this anime/manga/manhwa YouTube script.

SCORING RUBRIC (0-100):
- 90-100: Instantly gripping. Creates irresistible curiosity. Uses a provocative claim, shocking fact, or bold question that makes clicking away feel like a loss. Example: "One Piece has been lying to you for 25 years."
- 70-89: Strong opening. Clear curiosity gap or emotional pull. Viewer knows what they'll get and wants it.
- 50-69: Functional but generic. Opens with context/background instead of a hook. "Today we're going to talk about..."
- 30-49: Weak. Buries the lead. Long intros, disclaimers, or channel plugs before the content.
- 0-29: No hook. Starts with unrelated content, confusing context, or dead air.

KEY CRITERIA:
1. Cold open effectiveness — does it drop you into something compelling immediately?
2. Curiosity gap — does it open a loop the viewer NEEDS closed?
3. Emotional trigger — does it provoke curiosity, outrage, excitement, or nostalgia?
4. Promise clarity — does the viewer know what value they'll get from watching?
5. Archetype alignment:
   - Editorial Essay hooks use provocative takes: "Why [series] is actually about [unexpected theme]"
   - Power Fantasy Recap hooks use scenario framing: "When [protagonist] gained [power], nobody expected..."
   - Explainer hooks use knowledge gaps: "There's a detail in [series] that 99% of fans missed"

SCRIPT TO ANALYZE:
---
{script_text}
---

{metadata_section}

Respond with ONLY this JSON structure:
{{
    "pillar": "hook",
    "score": <0-100>,
    "justification": "<2-3 sentence explanation of the score>",
    "issues": [
        {{
            "description": "<specific problem>",
            "location": "<quote the problematic text>",
            "fix": "<rewritten version that fixes the issue>"
        }}
    ],
    "strengths": ["<strength 1>", "<strength 2>"]
}}"""

PACING_RETENTION_PROMPT = """Analyze the PACING & RETENTION of this anime/manga/manhwa YouTube script.

SCORING RUBRIC (0-100):
- 90-100: Perfect rhythm. Alternates between high-energy reveals and breathing room. Pattern interrupts every 60-90 seconds. No dead spots. Viewer never has a reason to click away.
- 70-89: Good flow. Some variation in pacing. Minor dead spots but generally holds attention.
- 50-69: Uneven. Extended sections of monotone delivery or info-dumping. Needs more pattern interrupts.
- 30-49: Flat. Long stretches without hooks, reveals, or energy shifts. Feels like a lecture.
- 0-29: Monotonous. No variation. Reader/viewer checks out within the first minute.

KEY CRITERIA:
1. Segment timing — are sections appropriately sized (60-120 seconds each)?
2. Pattern interrupts — moments that break the rhythm: questions, shocking reveals, tone shifts, humor
3. Dead spots — sections where nothing new is introduced, energy drops, or the script repeats itself
4. Escalation — does intensity build toward a payoff? Or does it plateau?
5. Re-hooks — after each major point, is there a reason to keep watching? ("But it gets worse..." / "And that's not even the craziest part")
6. Info density — is information spread evenly or front/back-loaded?

ANIME-SPECIFIC PACING:
- Power scaling discussions need periodic "benchmark moments" (compare to known characters)
- Story recaps need tension/release cycles, not just chronological retelling
- Analysis pieces need "insight density" — at least one non-obvious observation per 90 seconds

SCRIPT TO ANALYZE:
---
{script_text}
---

{metadata_section}

Respond with ONLY this JSON structure:
{{
    "pillar": "pacing",
    "score": <0-100>,
    "justification": "<2-3 sentence explanation of the score>",
    "issues": [
        {{
            "description": "<specific pacing problem>",
            "location": "<quote the problematic section or describe its position>",
            "fix": "<suggestion for fixing the pacing issue>"
        }}
    ],
    "strengths": ["<strength 1>", "<strength 2>"]
}}"""

STORYTELLING_STRUCTURE_PROMPT = """Analyze the STORYTELLING STRUCTURE of this anime/manga/manhwa YouTube script.

SCORING RUBRIC (0-100):
- 90-100: Masterful narrative arc. Clear setup-confrontation-resolution. Emotional range covers at least 3 distinct beats. The viewer feels something at the end.
- 70-89: Solid structure. Has a beginning/middle/end. Some emotional variation. Lands its conclusion.
- 50-69: Basic structure present but predictable. Linear without surprises. Conclusion feels rushed or tacked on.
- 30-49: Weak structure. Information dump without narrative thread. No emotional journey.
- 0-29: No discernible structure. Random points strung together.

KEY CRITERIA:
1. Narrative arc — setup, rising action, climax, resolution present?
2. Beat sheet alignment — does it follow a recognizable story structure?
   - For recaps: Inciting incident → escalation → twist → climax → aftermath
   - For analysis: Thesis → evidence → counterpoint → synthesis → revelation
   - For essays: Hook → personal connection → deep dive → paradigm shift → call to action
3. Emotional range — does it hit multiple emotional notes? (curiosity → shock → admiration → nostalgia)
4. Transitions — are section changes smooth or jarring?
5. Conclusion strength — does it land? Callbacks to the opening? Satisfying resolution?
6. Thematic coherence — does every section serve the central thesis/story?

SCRIPT TO ANALYZE:
---
{script_text}
---

{metadata_section}

Respond with ONLY this JSON structure:
{{
    "pillar": "storytelling",
    "score": <0-100>,
    "justification": "<2-3 sentence explanation of the score>",
    "issues": [
        {{
            "description": "<specific structural problem>",
            "location": "<quote or describe the section>",
            "fix": "<how to restructure or improve>"
        }}
    ],
    "strengths": ["<strength 1>", "<strength 2>"]
}}"""

ENGAGEMENT_TRIGGERS_PROMPT = """Analyze the ENGAGEMENT TRIGGERS in this anime/manga/manhwa YouTube script.

SCORING RUBRIC (0-100):
- 90-100: Loaded with engagement bait. Multiple open loops, curiosity gaps, and comment-worthy moments. Viewers will pause to comment, share timestamps, and debate.
- 70-89: Good trigger density. Several moments that provoke reaction. At least one strong comment-bait moment.
- 50-69: Some triggers present but not strategic. Relies on the topic itself rather than scripted engagement moments.
- 30-49: Few triggers. Passive content that viewers consume but don't interact with.
- 0-29: No engagement triggers. Pure information delivery with no hooks for interaction.

KEY CRITERIA:
1. Open loops — questions or mysteries introduced that get resolved later
   Example: "There's one character who breaks this entire power system... we'll get to them."
2. Curiosity gaps — information teased but withheld
   Example: "The creator actually revealed the REAL reason behind this scene... and it changes everything."
3. Comment-bait moments — statements designed to spark debate
   Example: "Gojo is NOT the strongest character in Jujutsu Kaisen. Here's why."
   Example: "Hot take: this arc is the worst in the entire series."
4. Community references — "let me know in the comments", polls, questions to viewers
5. Shareability hooks — moments worth clipping or screenshot-ing
6. Controversy/debate fuel — takes that split the audience (increases engagement)
7. Easter egg reveals — hidden details that make viewers feel smart for catching

SCRIPT TO ANALYZE:
---
{script_text}
---

{metadata_section}

Respond with ONLY this JSON structure:
{{
    "pillar": "engagement",
    "score": <0-100>,
    "justification": "<2-3 sentence explanation of the score>",
    "issues": [
        {{
            "description": "<missing engagement opportunity>",
            "location": "<where in the script this could be added>",
            "fix": "<specific engagement trigger to add>"
        }}
    ],
    "strengths": ["<strength 1>", "<strength 2>"]
}}"""

NARRATION_QUALITY_PROMPT = """Analyze the NARRATION QUALITY of this anime/manga/manhwa YouTube script.

SCORING RUBRIC (0-100):
- 90-100: Reads beautifully. Natural, conversational cadence. Great sentence variety (short punchy + longer flowing). Active voice dominant. Feels like a knowledgeable friend talking, not a Wikipedia article. TTS-friendly.
- 70-89: Good narration. Mostly natural. Some passive voice or overly complex sentences. Generally pleasant to listen to.
- 50-69: Functional but stiff. Over-relies on one sentence length. Some awkward phrasing or jargon without context.
- 30-49: Robotic or academic. Long complex sentences. Heavy passive voice. Doesn't feel like spoken word.
- 0-29: Unlistenable. Run-on sentences, unclear pronouns, confusing structure. Would sound terrible as voiceover.

KEY CRITERIA:
1. Sentence variety — mix of short punchy sentences and longer explanatory ones
   Good: "He lost. Not just the fight — everything. His power, his friends, his entire reason to keep going."
   Bad: "He lost the fight and also lost his power and his friends and his reason to keep going."
2. Active voice — "Goku destroyed the arena" not "The arena was destroyed by Goku"
3. Conversational tone — sounds natural when read aloud, not like an essay
4. TTS-friendliness — no weird abbreviations, clear pronunciation cues, proper pauses (periods, not just commas)
5. Rhythm — does the text have a natural cadence? Read it aloud mentally.
6. Pronoun clarity — is it always clear who "he/she/they" refers to?
7. Jargon handling — are anime terms explained or assumed? (Context-dependent)
8. Show don't tell — uses vivid descriptions rather than bland summaries

SCRIPT TO ANALYZE:
---
{script_text}
---

{metadata_section}

Respond with ONLY this JSON structure:
{{
    "pillar": "narration",
    "score": <0-100>,
    "justification": "<2-3 sentence explanation of the score>",
    "issues": [
        {{
            "description": "<specific narration problem>",
            "location": "<quote the problematic text>",
            "fix": "<rewritten version>"
        }}
    ],
    "strengths": ["<strength 1>", "<strength 2>"]
}}"""

SEO_DISCOVERABILITY_PROMPT = """Analyze the SEO & DISCOVERABILITY of this anime/manga/manhwa YouTube script.

NOTE: This analysis focuses on the script's searchability. If title/description/tags metadata is provided, analyze those too. If not, focus on keyword density and topic clarity within the script itself.

SCORING RUBRIC (0-100):
- 90-100: Perfectly optimized. Title is click-worthy AND search-friendly. Description has key terms in first 2 lines. Tags cover broad and niche terms. Script naturally weaves in searchable terms.
- 70-89: Good optimization. Title works for both browse and search. Most key terms present. Minor gaps in tag strategy.
- 50-69: Partial optimization. Title is either click-worthy OR search-friendly but not both. Missing obvious keyword opportunities.
- 30-49: Poor optimization. Generic title, thin description, irrelevant or missing tags. Script doesn't mention key searchable terms.
- 0-29: No SEO awareness. Title doesn't match content. No relevant keywords anywhere.

KEY CRITERIA:
1. Title analysis (if provided):
   - Does it include the series/character name? (Required for anime content)
   - Is it under 60 characters? (YouTube truncates longer titles)
   - Does it create curiosity while including search terms?
   - Pattern check: "[Series Name] + [Hook/Angle]" is the gold standard
2. Description analysis (if provided):
   - First 2 lines contain the hook + key search terms?
   - Includes series name, character names, arc names?
3. Tag strategy (if provided):
   - Mix of broad ("anime", "manga") and specific ("[series name] explained")?
   - Includes common misspellings or alternate names?
4. Script keyword density:
   - Does the script mention the series/characters by name frequently enough for transcript-based search?
   - Natural keyword integration vs. keyword stuffing?

SCRIPT TO ANALYZE:
---
{script_text}
---

{metadata_section}

Respond with ONLY this JSON structure:
{{
    "pillar": "seo",
    "score": <0-100>,
    "justification": "<2-3 sentence explanation of the score>",
    "issues": [
        {{
            "description": "<specific SEO problem>",
            "location": "<relevant section or metadata field>",
            "fix": "<specific optimization suggestion>"
        }}
    ],
    "strengths": ["<strength 1>", "<strength 2>"]
}}"""

NICHE_FIT_PROMPT = """Analyze the ANIME/MANGA/MANHWA NICHE FIT of this YouTube script.

SCORING RUBRIC (0-100):
- 90-100: Perfect niche alignment. Clearly targets a specific anime/manga/manhwa audience. Uses community language naturally. References feel authentic, not forced. Matches one of the proven archetypes perfectly.
- 70-89: Good fit. Clearly anime/manga content. Some community references. Mostly aligns with a known archetype.
- 50-69: Generic content analysis that happens to be about anime. Could be any YouTube topic with the nouns swapped out.
- 30-49: Weak niche awareness. Uses anime topic but doesn't speak the language of the community. Feels like an outsider explaining.
- 0-29: Wrong niche entirely. Or so generic it could be about anything.

KEY CRITERIA:
1. Archetype alignment — does it fit one of these proven formats?
   - Editorial Essay (Living Deadman/OniMaru style):
     * Provocative thesis that challenges community consensus
     * Personal emotional connection to the material
     * Deep thematic analysis beyond surface plot
     * "This series changed how I think about [theme]"
   - Power Fantasy Recap (Tobs Manhwa style):
     * "When [protagonist] [did/gained X], [dramatic consequence]"
     * Focus on power scaling, transformation moments, and "badass" scenes
     * Hype-building language: "absolutely destroyed", "broke the system"
     * Clear isekai/manhwa/shonen conventions respected
   - Explainer/Analysis (arikendo/Sock Sensei style):
     * Educational framing: "explained", "breakdown", "everything you need to know"
     * Comprehensive coverage of a topic, character, or arc
     * Visual reference points and comparisons
     * Respects source material accuracy

2. Community language — does it use terms the audience uses?
   (arc, power level, MC, OP, nerf, buff, goated, peak fiction, mid, etc.)

3. Sub-genre conventions — is it aware of its sub-genre?
   - Shonen: power scaling, training arcs, rivalry dynamics
   - Seinen: thematic depth, moral ambiguity, mature themes
   - Manhwa/Webtoon: system mechanics, leveling, regression
   - Isekai: world mechanics, cheat skills, genre subversion

4. Fan service (content, not visual) — references, callbacks, comparisons that reward dedicated fans

SCRIPT TO ANALYZE:
---
{script_text}
---

{metadata_section}

Respond with ONLY this JSON structure:
{{
    "pillar": "niche_fit",
    "score": <0-100>,
    "justification": "<2-3 sentence explanation of the score>",
    "issues": [
        {{
            "description": "<specific niche fit problem>",
            "location": "<relevant section>",
            "fix": "<how to improve niche alignment>"
        }}
    ],
    "strengths": ["<strength 1>", "<strength 2>"]
}}"""


def build_metadata_section(metadata: dict | None) -> str:
    """Build the metadata context section for prompts."""
    if not metadata:
        return "No metadata provided (title, description, tags not available for SEO analysis)."

    parts = []
    if metadata.get("title"):
        parts.append(f"Title: {metadata['title']}")
    if metadata.get("description"):
        parts.append(f"Description: {metadata['description'][:500]}")
    if metadata.get("tags"):
        tags = metadata["tags"]
        if isinstance(tags, list):
            tags = ", ".join(tags)
        parts.append(f"Tags: {tags}")
    if metadata.get("series_name"):
        parts.append(f"Series: {metadata['series_name']}")
    if metadata.get("archetype"):
        parts.append(f"Content archetype: {metadata['archetype']}")

    if not parts:
        return "No metadata provided."

    return "METADATA:\n" + "\n".join(parts)


def get_pillar_prompt(pillar: str) -> str:
    """Get the prompt template for a specific pillar."""
    prompts = {
        "hook": HOOK_ANALYSIS_PROMPT,
        "pacing": PACING_RETENTION_PROMPT,
        "storytelling": STORYTELLING_STRUCTURE_PROMPT,
        "engagement": ENGAGEMENT_TRIGGERS_PROMPT,
        "narration": NARRATION_QUALITY_PROMPT,
        "seo": SEO_DISCOVERABILITY_PROMPT,
        "niche_fit": NICHE_FIT_PROMPT,
    }
    if pillar not in prompts:
        raise ValueError(f"Unknown pillar: {pillar}. Valid: {list(prompts.keys())}")
    return prompts[pillar]


PILLAR_NAMES = {
    "hook": "Hook Analysis",
    "pacing": "Pacing & Retention",
    "storytelling": "Storytelling Structure",
    "engagement": "Engagement Triggers",
    "narration": "Narration Quality",
    "seo": "SEO & Discoverability",
    "niche_fit": "Niche Fit",
}

ALL_PILLARS = list(PILLAR_WEIGHTS.keys())
