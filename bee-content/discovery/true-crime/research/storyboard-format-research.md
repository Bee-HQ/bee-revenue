# Research: Open-Source Video Production Formats, Standards, and Tools

> Deep research on existing protocols that could replace or inform the custom visual storyboard bible for automated video assembly.
>
> **Date:** 2026-03-17
> **Context:** We have a custom markdown-based storyboard system defining ~30 visual element codes ([BROLL-DARK], [COURTROOM], [PIP-SINGLE], [LOWER-THIRD], [QUOTE-CARD], etc.) with per-element specs (colors, sizes, durations, layer ordering). A parser reads markdown, processors generate assets via Pillow, and FFmpeg assembles the final 50-minute video.

---

## 1. Video Description / Storyboard Formats

### EDL (Edit Decision List) — CMX3600

**What it models:** A flat, sequential list of edit events. Each event specifies source reel, timecode in/out, and a basic transition (cut, dissolve, wipe). Developed in the 1970s for linear tape editing.

**What it covers:**
- Source reel ID + timecode
- Record in/out points
- One transition type per event (cut, dissolve, wipe with pattern code)
- Single video track (V) or audio tracks (A, A2)

**Limitations:** Single video track only. No multiple simultaneous layers. No effects parameters beyond basic wipe codes. No text, overlays, generators, or metadata. No nested compositions. Fixed at 30fps timecode (or drop-frame). Pure editorial cuts — nothing about what the clips *look like*.

**Python SDK:** No official library. Parsers exist (opentimelineio can read CMX3600).

**Verdict for us:** Almost completely irrelevant. EDL can describe *which clips play when* but nothing about our visual codes, overlays, color grades, or graphics. It solves maybe 5% of our problem (basic cut list).

---

### AAF (Advanced Authoring Format)

**What it models:** A binary interchange format carrying timeline structure, effects, transitions, metadata, and optionally embedded media. Developed by the broadcast industry (Avid, Microsoft, others) in the late 1990s.

**What it covers:**
- Multi-track timelines
- Effects with parameters
- Transitions
- Nested compositions
- Rich metadata
- Embedded or referenced media

**Limitations:** Binary format — not human-readable or hand-editable. Complex specification. Limited open-source tooling. Primarily an Avid ecosystem format. No standard Python library for authoring (opentimelineio can read/write AAF via adapter, but with limitations).

**Verdict for us:** Overkill and wrong direction. AAF is for NLE interchange, not for declarative authoring. We don't need to send our project to Premiere — we need to describe what to *build*.

---

### FCP XML (Final Cut Pro XML)

**What it models:** Apple's XML interchange format for Final Cut Pro projects.

**What it covers:**
- Multi-track timelines with compound clips
- Effects, transitions, titles, generators
- Audio mixing and roles
- Keyframe animation parameters
- Text/title specifications with font, size, position
- Color correction parameters
- Metadata (keywords, notes, ratings)
- Currently at FCPXML v1.11+

**Limitations:** Apple-centric. The schema is complex and verbose. Many elements are FCP-specific (generator IDs, effect UUIDs). Not designed for authoring — designed for round-tripping within the Apple ecosystem. Generators/titles reference FCP's built-in plugin system.

**Python SDK:** No official SDK. OTIO can partially read/write it. `fcpxml` PyPI package exists but limited.

**Verdict for us:** The richest NLE format and closest to what we need conceptually — it actually describes titles, generators, and effects with parameters. But it's tightly coupled to FCP's plugin ecosystem. Our [LOWER-THIRD] with specific hex colors doesn't map to an FCP generator UUID. More useful as *inspiration for our schema* than as a direct adoption target.

---

### OpenTimelineIO (OTIO) — Pixar / ASWF

**What it models:** An open-source interchange format and API for editorial timeline information. Self-described as "a modern EDL." Part of the Academy Software Foundation.

**Core concepts:**
- `Timeline` → `Stack` → `Track` (video/audio) → `Clip` / `Gap` / `Transition`
- `MediaReference` (external URL or path to media)
- `Marker` (labeled points on timeline)
- `Effect` (named effect with metadata dict)
- `metadata` dict on every object (arbitrary key-value, deeply nested)

**Maturity:** v0.19.0.dev1 (pre-1.0). 1.8k GitHub stars. Python SDK: `pip install opentimelineio`. Python 3.9-3.12. Actively maintained by ASWF (Pixar, Netflix, etc.). Natively supported in most major NLEs now.

**Format adapters:** Can read/write FCP XML, AAF, CMX3600 EDL, and its native `.otio` (JSON), `.otioz` (zip bundle), `.otiod` (directory bundle).

**What it CANNOT describe:**
- Visual overlay specifications (no [LOWER-THIRD] with hex colors and font sizes)
- Motion graphics or generator parameters
- Text overlay content and styling
- Color grading parameters
- Composite layer ordering rules
- Asset generation instructions

**What it CAN do for us:**
- The `metadata` dict on every object is fully extensible — we could attach our visual codes as metadata on clips/markers
- Timeline structure (tracks, clips, gaps, transitions) maps to our segment model
- Effects list per clip could carry our effect parameters as metadata
- It would let us export our timeline to any NLE for manual refinement

**Verdict for us:** OTIO is the strongest candidate for the **timeline/editorial layer** of our system. It models *when things happen* well but not *what they look like*. The strategy would be: use OTIO as our timeline backbone, attach our custom visual codes as OTIO metadata, and keep our own schema for the visual/graphics specifications. This gives us NLE interop for free while keeping our domain-specific layer.

**What we'd gain:** NLE interchange (export to Premiere/Resolve/FCP for manual polish), a well-tested timeline data model, industry backing.
**What we'd lose:** Nothing significant — we'd be adding a layer on top, not replacing our visual code system.

---

### MLT XML — MLT Framework (Shotcut / Kdenlive)

**What it models:** The serialization format for the MLT multimedia framework. Powers Shotcut and Kdenlive editors.

**Core concepts:**
- `<producer>` — a source (file, color, text via pango, image)
- `<playlist>` — sequential arrangement of producers with in/out points and blanks
- `<tractor>` — a multitrack container with filters and transitions
- `<multitrack>` — parallel tracks within a tractor
- `<filter>` — applied to track or output (brightness, text overlay, chroma key, etc.)
- `<transition>` — blend between tracks (composite, luma, mix)

**Maturity:** v7.36.0 (December 2025). Very active — monthly releases. Powers two major open-source NLEs. Python bindings exist via SWIG (`import mlt7`).

**What it can express:**
- Full multi-track timelines with arbitrary nesting
- Text overlays via pango producer (font, size, color, position)
- Image overlays and compositing (region transitions)
- Filter chains (brightness, contrast, color balance — our [COLOR-GRADE])
- Transitions between tracks (dissolve, luma wipe, composite)
- Chroma key, affine transforms, opacity

**Limitations:** XML is verbose. Tightly coupled to MLT's filter/transition naming. Not designed for human authoring. Filter parameters use MLT-specific property names that aren't self-documenting.

**Verdict for us:** MLT XML is the most *complete* open format for describing everything we do — timelines, text overlays, color grading, compositing, transitions. It can express our entire pipeline. The problem is ergonomics: nobody wants to hand-author MLT XML, and our storyboard bible is fundamentally a *human-authored* document. However, MLT XML is an excellent **compilation target**. Our markdown storyboard could compile down to MLT XML, which `melt` (the MLT CLI) renders to video. This would replace our bespoke FFmpeg command construction with a well-tested rendering engine.

**What we'd gain:** Proven rendering engine (melt), no more hand-crafting FFmpeg filter chains, compositing/transitions built in, Python bindings.
**What we'd lose:** Some control over exact FFmpeg parameters, dependency on MLT framework installation.

---

### Other Notable Formats

**Premiere Pro XML (FCP7 XML):** Legacy XML format. Less capable than FCPXML. Widely supported as interchange but dated.

**DaVinci Resolve .drp:** Proprietary project format. No open spec. OTIO can partially export to it.

**Kdenlive .kdenlive:** MLT XML with Kdenlive-specific extensions. Same capabilities as MLT XML.

**SMIL (Synchronized Multimedia Integration Language):** W3C standard for multimedia presentations. Dead in practice — no modern tools use it.

---

## 2. Motion Graphics / Overlay Description

### Lottie / Bodymovin

**What it is:** A JSON-based vector animation format, originally exported from After Effects via the Bodymovin plugin. Now an independent ecosystem.

**What it describes:**
- Layers: shape, text, image, precomposition, solid, null
- Shapes: rectangles, ellipses, paths, fills, strokes, gradients
- Animations: keyframed transforms (position, scale, rotation, opacity), shape morphing
- Text: styled text with per-character animation
- Effects: drop shadow, gaussian blur, and more
- Compositions with nested timelines

**Could it replace our Pillow-generated PNGs?**
Yes, emphatically. Instead of generating static 1920x1080 PNGs for [LOWER-THIRD], [QUOTE-CARD], [FINANCIAL-CARD], [TIMELINE-MARKER], we could define them as Lottie animations:
- [LOWER-THIRD]: The red line draws in, name slides from left, role fades in — all described in JSON, rendered to video frames
- [QUOTE-CARD]: Quote mark scales in, text fades in word-by-word, attribution appears
- [TIMELINE-SEQUENCE]: Nodes illuminate as cursor sweeps — natural Lottie territory
- [MAP-PULSE]: Concentric circles expanding with decreasing opacity — trivial in Lottie

**Python SDK:** `lottie` package on PyPI (v0.7.2, May 2025, beta, AGPLv3+). Can create Lottie animations programmatically in Python. Also `pysubs2` for subtitle integration.

**Rendering to video:** Lottie renders natively in browsers. For our pipeline, we'd render Lottie to image sequences (via headless browser or `rlottie` C library) then composite with FFmpeg. Or use Remotion (React) to render Lottie directly into video frames.

**Maturity:** Massive ecosystem. LottieFiles.com hosts 100K+ animations. Every major platform supports playback (iOS, Android, Web, React Native). The format itself is stable and well-documented.

**Verdict for us:** High-value adoption target for animated overlays. Our static PNGs are the weakest part of the current pipeline — they look amateurish compared to animated lower-thirds. Lottie templates per visual code + Python generation would significantly improve output quality.

**What we'd gain:** Animated overlays (huge quality improvement), reusable templates, massive existing asset library.
**What we'd lose:** Simplicity of Pillow PNG generation, need a renderer in the pipeline (headless browser or rlottie).

---

### Remotion — React-Based Video

**What it is:** A framework for creating videos programmatically using React. Videos are React components rendered frame-by-frame.

**Key stats:** 39.7k GitHub stars, v4.0.436 (March 2026), 318 contributors, 31.4k commits. 900K monthly npm installs. Very mature.

**Core concept:** Each video element is a React component. You compose them like a web page. `<Sequence>` for timing, `<AbsoluteFill>` for positioning, CSS for styling, `useCurrentFrame()` for animation. Renders via headless Chromium.

**How it maps to our visual codes:**
```tsx
// [LOWER-THIRD] as a Remotion component
const LowerThird = ({ name, role }) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 15], [0, 1]);
  const slideX = interpolate(frame, [0, 15], [-200, 0]);
  return (
    <AbsoluteFill style={{ bottom: 80, left: 40 }}>
      <div style={{ transform: `translateX(${slideX}px)`, opacity }}>
        <div style={{ background: 'rgba(0,0,0,0.7)', borderTop: '3px solid #C81E1E' }}>
          <h2 style={{ color: '#fff', fontSize: 42 }}>{name}</h2>
          <p style={{ color: '#B4B4B4', fontSize: 28 }}>{role}</p>
        </div>
      </div>
    </AbsoluteFill>
  );
};
```

Each of our 30 visual codes could be a Remotion component. The storyboard parser outputs a Remotion composition spec. Remotion renders the entire video.

**Rendering:** Local (Chromium), server-side, or serverless (Remotion Lambda on AWS). Can produce MP4, WebM, GIF.

**Python integration:** None native. You'd need a Node.js subprocess or a bridge service. Our Python pipeline would generate a JSON spec, pass it to a Node process that renders via Remotion.

**Limitations:** JavaScript-only. Rendering is CPU-intensive (headless Chromium). Commercial license required for companies (free for individuals/small companies under $10K). Video rendering can be slow compared to native FFmpeg.

**Verdict for us:** The most architecturally elegant solution. Our entire visual storyboard bible becomes a component library. The storyboard markdown compiles to a Remotion composition. Every visual code, every animation, every overlay — all React. The tradeoff is adding Node.js to our Python stack and slower rendering.

**What we'd gain:** Full programmatic control over every pixel, CSS/SVG/Canvas for graphics (infinitely more capable than Pillow), animated everything, web preview.
**What we'd lose:** Python-only simplicity, fast FFmpeg rendering speed, need to maintain a JS codebase alongside Python.

---

### Motion Canvas

**What it is:** TypeScript library for creating informative vector animations using generators, with a real-time editor.

**Key stats:** 18.3k stars, v3.17.2 (December 2024). Focused on "informative vector animations" — think YouTube explainer motion graphics.

**Relevance:** Excellent for our animated elements ([TIMELINE-SEQUENCE], [FLOW-DIAGRAM], [EVIDENCE-BOARD]). The generator-based API is elegant for sequential animations. However, it's designed for short explanatory clips, not full video assembly. No audio support. No video compositing.

**Fork — Revideo:** A fork of Motion Canvas focused on video production. 2k stars, Y Combinator backed. Adds video rendering to MP4, parameterized templates, audio support. More relevant than Motion Canvas itself for our use case, but younger and less stable.

**Verdict for us:** Useful as inspiration for our animated element generation, but not a replacement for the full pipeline. Could generate individual animated segments (timeline animations, flow diagrams) that feed into the main assembly.

---

### Manim — 3Blue1Brown's Animation Engine

**What it is:** Python animation engine for mathematical/explanatory videos. 85.3k stars, v1.7.2.

**Relevance:** Pure Python, which fits our stack. Excellent at programmatic animation. BUT it's optimized for mathematical visualization, not broadcast graphics. Creating a [LOWER-THIRD] in Manim is possible but awkward — you'd be fighting the API rather than leveraging it.

**Verdict for us:** Not relevant. Wrong tool for the job despite being Python.

---

### Programmatic Overlay Composition — The Gap

No single open standard exists for describing overlay compositions programmatically. This is the gap our visual storyboard bible fills. The closest things are:

1. **Lottie** — for individual animated overlays (lower-thirds, cards, titles)
2. **MLT XML filters** — for compositing overlays onto video tracks
3. **Remotion compositions** — for full declarative video including overlays
4. **Shotstack/Creatomate JSON schemas** — commercial but well-designed declarative video APIs
5. **ASS subtitles** — surprisingly capable for styled text overlays (see Section 4)

---

## 3. Asset Pipeline Standards

### OpenEXR / ACES

**OpenEXR:** High-dynamic-range image format for VFX. 1.8k stars, ASWF project. Stores multi-channel, multi-layer image data with floating-point precision.

**ACES (Academy Color Encoding System):** Industry-standard color pipeline for film production. Defines color spaces, transforms, and workflows for consistent color from capture through display.

**Relevance for our color grading:** Low to moderate. Our color grading is 12 FFmpeg `eq` and `colorbalance` presets. ACES matters when you're doing high-end color work across multiple cameras and display targets. For faceless YouTube at 1080p, FFmpeg's built-in color filters are sufficient.

**Python:** The `colour-science` package (2.5k stars) supports ACES transforms. Useful if we ever need scientifically accurate color pipelines, but that's not our current need.

**Verdict:** Not relevant for current scope. File away for if we ever do multi-camera high-end work.

---

### OpenFX

**What it is:** Cross-platform plugin standard for visual effects. Allows the same effect plugin to work in Resolve, Nuke, Natron, Vegas, etc.

**Relevance:** We're not building NLE plugins — we're building a pipeline. OpenFX is for extending existing editors, not for programmatic pipelines.

**Verdict:** Not relevant.

---

### FFmpeg Filter Graphs as Data

**Current state:** FFmpeg uses a string-based filter graph syntax: `[0:v]eq=brightness=-0.08:saturation=0.6[v1];[v1][1:v]overlay=x=10:y=10[out]`. There is no official JSON/XML/YAML representation.

**ffmpeg-python** (11k stars): Provides a fluent Python API that builds filter graphs as DAGs and serializes to FFmpeg command strings. Last updated 2022 — somewhat stale but widely used (82.8k dependents). Example:
```python
(ffmpeg
 .input('video.mp4')
 .filter('eq', brightness=-0.08, saturation=0.6)
 .overlay(ffmpeg.input('overlay.png'), x=10, y=10)
 .output('out.mp4')
 .run())
```

This is essentially what we need — filter graphs as Python data structures rather than hand-crafted strings. But ffmpeg-python is unmaintained. Alternatives: `ffmpeg-progress-yield`, `python-ffmpeg` (actively maintained forks).

**Verdict for us:** We should use a filter graph builder library (ffmpeg-python or successor) rather than string-templating FFmpeg commands. This doesn't replace our storyboard format but improves the processor layer.

---

### Asset Manifest / Preflight Standards

No widely adopted open standard for video asset manifests or preflight checks. Commercial tools (Frame.io, Shotstack) have proprietary asset management. The closest open-source concept is OTIO's `MediaReference` which links timeline clips to media files.

Our `production_state.json` and `.bee-video/assignments.json` are essentially custom asset manifests. The visual storyboard bible's Section 11 ("Asset Checklist Per Video") is a manual preflight spec.

**Verdict:** This is an area where we'll continue with custom tooling. No standard to adopt.

---

## 4. Subtitle / Caption Standards

### ASS (Advanced SubStation Alpha)

**What it is:** Subtitle format with powerful styling, positioning, animation, and drawing capabilities. Used extensively in anime fansubs, but its capabilities extend far beyond basic subtitles.

**Styling capabilities:**
- **Fonts:** `\fn` (font name), `\fs` (size), `\b` (bold), `\i` (italic), `\u` (underline)
- **Colors:** `\c` (primary), `\1c-\4c` (fill, karaoke, border, shadow — all with alpha)
- **Positioning:** `\pos(x,y)` absolute, `\an1-9` alignment grid, `\move(x1,y1,x2,y2,t1,t2)` animated movement
- **Transform:** `\frx \fry \frz` (3D rotation), `\fax \fay` (shear), `\fscx \fscy` (scale)
- **Borders/shadows:** `\bord` (outline width), `\shad` (shadow distance), `\be` (blur edges), `\blur` (gaussian blur)
- **Animation:** `\t(t1,t2,\tag)` — animate ANY tag over time (color changes, scale, rotation, blur)
- **Clipping:** `\clip(x1,y1,x2,y2)` rectangular clip, `\clip(drawing)` vector clip
- **Drawing mode:** `\p1` activates vector drawing — arbitrary shapes via move/line/bezier commands
- **Fades:** `\fad(fadein,fadeout)` and `\fade(a1,a2,a3,t1,t2,t3,t4)` complex opacity

**Can it handle our [CAPTION-ANIMATED]?** Yes, and more. ASS can do:
- Word-by-word highlighting with color transitions via `\t` tags
- Karaoke-style progressive fill (`\k` tags)
- Positioned text anywhere on screen
- Animated movement of text elements
- Drawing shapes (could do simple graphics like bars, lines)
- Multiple simultaneous styled elements

**Can it handle [LOWER-THIRD]?** Partially. You could create a lower-third entirely in ASS using:
- A drawn rectangle with `\p1` for the bar
- Positioned text for name and role
- `\fad` for fade in/out
- `\t` for color animations
But the ergonomics are terrible — ASS was designed for subtitle timing, not motion graphics authoring.

**Python libraries:**
- `pysubs2` (PyPI, v1.8.0, Dec 2024, Production/Stable, MIT) — parse/create/modify ASS files. Supports all ASS features. Can insert override tags programmatically.
- `ass` (PyPI, v1.0.3, Oct 2025, Production/Stable, MIT) — parse/manipulate ASS files.

**Rendering:** libass (1.1k stars, v0.17.4) is the standard renderer. Integrated into FFmpeg via the `ass` and `subtitles` filters. VLC, mpv, and all major players use it.

**Verdict for us:** ASS is the **best standard for our [CAPTION-ANIMATED] system** and a surprisingly viable option for some overlay elements. For captions, it's the clear winner — word-by-word highlighting, per-phrase timing, styled text with borders/shadows, all rendered by FFmpeg's built-in `ass` filter. For lower-thirds and quote cards, ASS is *technically capable* but ergonomically worse than Lottie or Pillow. The sweet spot: use ASS for all timed text (captions, dialogue indicators) and Lottie/Pillow for graphic overlays.

**What we'd gain:** Industry-standard caption rendering, animation capabilities, FFmpeg-native compositing, no additional renderer needed.
**What we'd lose:** Nothing — ASS is strictly additive. It replaces our planned custom caption system with a standard one.

---

### WebVTT

**What it is:** W3C web standard for timed text tracks. Used in HTML5 `<track>` element.

**Styling:** Basic CSS via `::cue` pseudo-element. Supports positioning (line, position, size, align), basic formatting (bold, italic, voice tags), and regions. No animation, no drawing, no per-character effects.

**Verdict for us:** Too limited. Good for web preview of captions but nowhere near powerful enough for our production pipeline. Use ASS for production, potentially export WebVTT for web preview.

---

### TTML (Timed Text Markup Language)

**What it is:** W3C XML-based standard for timed text. Used in broadcast (EBU-TT), streaming (IMSC), and archival.

**Styling:** Extensive XML-based styling — fonts, colors, positioning, backgrounds, borders, shadows, regions, inline animations via `<animate>` and `<set>`. Ruby annotations for East Asian text. Audio styling attributes.

**Verdict for us:** More powerful than WebVTT but worse than ASS for our needs. TTML's XML verbosity makes it painful to author. Its animation model is simpler than ASS's `\t` tag. Better suited for broadcast compliance than creative production. `pysubs2` can read/write TTML if we need to export to broadcast format.

---

### Subtitle Generation Tools

For generating styled subtitles from transcript + timestamps:
- **Whisper** (OpenAI) — generates SRT/VTT with word-level timestamps
- **pysubs2** — convert between formats, add ASS styling programmatically
- **Aegisub** — GUI editor for ASS subtitles (manual refinement)
- **Subtitle Edit** — another GUI editor, supports ASS
- **ffsubsync** — auto-sync subtitles to audio

Pipeline for our [CAPTION-ANIMATED]:
1. Whisper transcribes audio → word-level SRT
2. pysubs2 loads SRT, converts to ASS, applies our styling template (bold white, dark outline, word-by-word highlight in red/teal)
3. FFmpeg burns ASS subtitles into video via `ass` filter

---

## 5. Relevant Open-Source Projects

### Editly — Declarative Video Editor

**What it is:** Node.js CLI tool that takes a JSON/JS spec and produces video via FFmpeg. 5.3k stars, 430 commits.

**DSL structure:**
```json
{
  "outPath": "output.mp4",
  "width": 1920, "height": 1080, "fps": 30,
  "defaults": { "duration": 5, "transition": { "name": "fade", "duration": 0.5 } },
  "clips": [
    {
      "duration": 10,
      "layers": [
        { "type": "video", "path": "bodycam.mp4", "cutFrom": 30, "cutTo": 40 },
        { "type": "image-overlay", "path": "lower-third.png", "position": "bottom-left" }
      ]
    },
    {
      "layers": [
        { "type": "fill-color", "color": "#0A0A0F" },
        { "type": "title", "text": "\"I'll kill him.\"", "textColor": "#FFFFFF" }
      ]
    }
  ],
  "audioTracks": [{ "path": "music.mp3", "mixVolume": "0.3" }]
}
```

**Layer types:** video, image, image-overlay, audio, detached-audio, title, subtitle, title-background, news-title, slide-in-text, fill-color, pause, radial-gradient, linear-gradient, rainbow-colors, canvas (JS function), fabric (Fabric.js), gl (GLSL shader).

**Transitions:** Entire gl-transitions library (100+ transitions) plus directional variants.

**Verdict for us:** Editly's architecture is remarkably close to what we need. Its JSON spec is essentially a simpler version of our storyboard format. The layer-based clip model maps well to our segments. Key differences from our needs:
- No complex graphics generation (lower-thirds are just text, not our styled bars)
- Limited text styling (color + font path only)
- Node.js, not Python
- No asset generation step — it assembles existing assets only

Editly is **strong validation** that our declarative approach is correct, and its JSON spec is worth studying as a reference for our schema design. But it can't replace our pipeline because it lacks the asset *generation* capabilities (Pillow graphics, TTS, etc.).

**What we'd gain from adopting Editly itself:** Nothing beyond what we already have. Our FFmpeg processor does more than Editly for our specific needs.
**What we'd gain from studying Editly:** Schema design patterns, the layers-in-clips model, transition handling.

---

### MoviePy — Python Video Editing

**What it is:** Python library for video editing. 14.4k stars, v2.2.1 (May 2025, but seeking maintainers).

**API:** Imperative, method-chaining. No declarative mode.
```python
clip = (VideoFileClip("video.mp4")
    .subclipped(10, 20)
    .with_volume_scaled(0.8))
composite = CompositeVideoClip([background, overlay.with_position(("left", "bottom"))])
```

**What it does:** Cuts, concatenation, compositing, text rendering (ImageMagick), effects, GIF creation. Converts media through numpy arrays.

**Limitations:** Slower than direct FFmpeg (numpy overhead). v2.0 broke backward compatibility. Project seeking maintainers. No declarative spec — purely programmatic.

**Verdict for us:** Not useful as a replacement. Our direct FFmpeg approach is faster and more capable. MoviePy would add a dependency and slow things down without giving us anything we don't have.

---

### VidPy — Python Video on MLT

**What it is:** Python wrapper around MLT framework. 133 stars, alpha status.

**What it does:** Load clips, apply effects, compose, render — all via MLT. Text overlays via MLT's pango producer. Position/resize clips. Chroma key, effects, transitions.

**Verdict for us:** Interesting concept (Python API over MLT) but too immature (alpha, low community). If we adopt MLT as a render target, we'd be better off generating MLT XML directly or using MLT's official Python bindings (`mlt7`).

---

### Auto-Editor — Automated Video Editing

**What it is:** CLI tool that automatically edits video by analyzing audio loudness and motion. 4k stars, v30.0.0 (March 2026). Primarily written in Nim.

**Relevant concepts:**
- Uses its own timeline format (.v1, .v2, .v3)
- Can export to Premiere, Resolve, FCP, Kdenlive, Shotcut
- Declarative `--edit` syntax: `--edit "(or audio:stream=0 audio:threshold=10%,stream=1)"`

**Verdict for us:** Not directly relevant — Auto-Editor solves a different problem (automatic silence removal). But its multi-format export is interesting as a pattern, and its declarative edit expression syntax is worth noting.

---

### Shotstack — Cloud Video API (Commercial)

**What it is:** REST API for video creation via JSON specs. Well-designed schema.

**JSON schema hierarchy:**
- `Edit` → `Timeline` → `Track[]` → `Clip[]` → `Asset`
- Asset types: VideoAsset, ImageAsset, AudioAsset, TextAsset, RichTextAsset, HtmlAsset, SvgAsset, ShapeAsset, LumaAsset, CaptionAsset, TextToImageAsset, ImageToVideoAsset
- Clip properties: start, length, transition (in/out), effect, filter, transform (rotate, skew, flip), opacity, crop, chroma key
- Templates with merge fields: `{{ PLACEHOLDER }}` syntax

**Relevance:** Shotstack's schema is the most complete declarative video spec I found. Its hierarchical model (timeline → tracks → clips → assets), combined with transforms, effects, and the template/merge-field system, is essentially what we'd want our storyboard format to compile to. Worth studying closely for schema design.

---

### Creatomate — Template-Based Video API (Commercial)

**What it is:** JSON-based video creation platform. "RenderScript" format.

**Schema:**
- Top level: format, dimensions, duration
- Elements: images, video, text, shapes, audio — each with position, size, timeline, animations
- Compositions: nested element groups with their own timelines
- Sensible defaults on all properties

**Relevance:** Creatomate's "sensible defaults" philosophy matches our storyboard bible well — each visual code has default colors, sizes, and durations that can be overridden. Their composition nesting (element groups with independent timelines) maps to our segment model.

---

### VapourSynth — Video Processing Framework

**What it is:** Script-based video processing framework. 2k stars, v73 (Nov 2025). AviSynth successor with Python bindings.

**Relevance:** Powerful for frame-level video processing and filtering. Python-scriptable. But designed for frame-by-frame processing tasks (denoising, scaling, format conversion) rather than editorial assembly.

**Verdict:** Not relevant for our storyboard format, but could be useful for specific processing tasks (noise reduction, scaling) in the asset pipeline.

---

## Summary & Recommendations

### Tier 1 — Adopt Now (High Value, Low Risk)

| Standard | Adopt For | Replaces | Effort |
|----------|-----------|----------|--------|
| **ASS subtitles** via pysubs2 | [CAPTION-ANIMATED] | Custom caption system (not yet built) | Low — pysubs2 + FFmpeg `ass` filter |
| **ffmpeg-python** (or successor) | FFmpeg processor internals | String-templated FFmpeg commands | Medium — refactor processors/ffmpeg.py |

**ASS for captions** is a no-brainer. We haven't built [CAPTION-ANIMATED] yet, and ASS is the industry standard with word-by-word animation, full styling, and native FFmpeg rendering. Use Whisper for transcription, pysubs2 to generate styled ASS, FFmpeg to burn in.

**ffmpeg-python** replaces our hand-crafted command strings with a typed, composable filter graph builder. Reduces bugs, makes complex graphs readable.

### Tier 2 — Adopt Strategically (High Value, Medium Effort)

| Standard | Adopt For | Replaces | Effort |
|----------|-----------|----------|--------|
| **Lottie** via python-lottie | Animated overlays ([LOWER-THIRD], [QUOTE-CARD], [TIMELINE-SEQUENCE], [FINANCIAL-CARD], etc.) | Static Pillow PNGs | Medium-High — need Lottie templates + renderer |
| **OTIO** as timeline backbone | Timeline data model + NLE export | Custom Storyboard dataclass (partially) | Medium — wrap existing model in OTIO |

**Lottie for animated overlays** is the highest-impact visual quality improvement available. Static PNGs for lower-thirds look amateur. Animated Lottie lower-thirds look professional. The investment is building Lottie templates for each visual code and adding a render step (headless browser or rlottie → image sequence → FFmpeg overlay).

**OTIO for timeline** gives us NLE interchange. After auto-assembly, export the OTIO timeline to Resolve/Premiere for a human editor to do final polish. This is valuable for quality control — automated assembly gets us 80%, a human does the final 20%.

### Tier 3 — Study but Don't Adopt (Informative, Not Actionable Now)

| Standard | Why Study It | Why Not Adopt |
|----------|-------------|---------------|
| **MLT XML** | Most complete open video description format. Excellent compilation target | Too verbose for authoring. Would need entire MLT framework. |
| **Remotion** | Architecturally elegant — each visual code as a React component | Adds Node.js to our Python stack. Slower rendering. Commercial license. |
| **Editly JSON** | Best declarative video schema to study for our own format design | Node.js only. Less capable than our current pipeline. |
| **Shotstack schema** | Most complete JSON video spec. Template/merge-field pattern. | Commercial API, not an open format. |
| **FCP XML** | Richest NLE format — titles, generators, effects with parameters | Apple-ecosystem coupled. |

### Tier 4 — Skip (Not Relevant)

| Standard | Why Skip |
|----------|----------|
| EDL (CMX3600) | Too primitive — single track, no effects, no overlays |
| AAF | Binary, NLE-centric, wrong direction |
| OpenEXR/ACES | Overkill for YouTube 1080p |
| OpenFX | For NLE plugins, not pipelines |
| Manim | Wrong domain (math animations) |
| MoviePy | Slower than direct FFmpeg, no declarative mode |
| VidPy | Alpha quality, low community |
| WebVTT | Too limited for styled captions |
| TTML | XML verbosity, less capable than ASS |
| VapourSynth | Frame processing, not editorial |

---

## The Strategic Architecture

Based on this research, the recommended evolution of our system:

```
Storyboard Markdown (human-authored)
    │
    ▼
Storyboard Parser (Python)
    │
    ├──► OTIO Timeline (editorial structure)
    │       ├── Clips with custom metadata (visual codes)
    │       ├── Markers for key moments
    │       └── Export → Resolve/Premiere for final polish
    │
    ├──► Lottie Templates (animated overlays)
    │       ├── [LOWER-THIRD] → lower_third.json
    │       ├── [QUOTE-CARD] → quote_card.json
    │       ├── [TIMELINE-SEQUENCE] → timeline.json
    │       └── Render → image sequences → FFmpeg overlay
    │
    ├──► ASS Subtitles (timed text)
    │       ├── [CAPTION-ANIMATED] → captions.ass
    │       └── FFmpeg ass filter burns in
    │
    └──► FFmpeg Filter Graphs (via ffmpeg-python)
            ├── [COLOR-GRADE] presets
            ├── Compositing layers
            ├── Transitions
            └── Final assembly
```

**Key insight from this research:** No single standard covers what our visual storyboard bible does. Our system sits at the intersection of editorial timing (OTIO), motion graphics (Lottie), styled captions (ASS), and video processing (FFmpeg). The right move is NOT to replace our custom format with a single standard, but to **use the best standard for each layer** while keeping our domain-specific storyboard bible as the human-authored source of truth.

Our storyboard markdown isn't "reinventing the wheel" — it's a domain-specific language that compiles to multiple industry standards. That's the right architecture.
