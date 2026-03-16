# Open Source Audio Processing, TTS, Speech Translation & Music Generation Tools

> Research date: 2026-03-15
> Focus: Programmatic tools for automated video production pipelines

---

## Table of Contents

1. [Text-to-Speech (TTS) for Narration](#1-text-to-speech-tts-for-narration)
2. [Speech-to-Speech Translation](#2-speech-to-speech-translation)
3. [Audio Processing & Manipulation](#3-audio-processing--manipulation)
4. [Music Generation (Background Music)](#4-music-generation-background-music)
5. [Comparison Tables](#5-comparison-tables)
6. [Practical Pipeline Recommendations](#6-practical-pipeline-recommendations)

---

## 1. Text-to-Speech (TTS) for Narration

### 1.1 Coqui TTS / XTTS v2

| Field | Details |
|-------|---------|
| **GitHub** | [coqui-ai/TTS](https://github.com/coqui-ai/TTS) (original, unmaintained) / [idiap/coqui-ai-TTS](https://github.com/idiap/coqui-ai-TTS) (active fork) |
| **Stars** | 44.8k (original) / 2.2k (Idiap fork) |
| **Language** | Python |
| **Last Updated** | Original: stale. Idiap fork: Dec 2024 (v0.27.0) |
| **License** | MPL-2.0 |
| **PyPI** | `pip install coqui-tts` (from Idiap fork) |

**Key Features:**
- XTTS v2: 16 languages, voice cloning from short reference audio, <200ms streaming latency
- Multiple model architectures: Tacotron2, VITS, Glow-TTS, XTTS, YourTTS
- Voice conversion and multi-speaker support
- ~1100 language support via Fairseq models
- Fine-tuning support for custom voices

**Quality Assessment:**
XTTS v2 produces natural-sounding speech with good prosody. Voice cloning quality is reasonable with 6-10 seconds of reference audio. The Idiap fork is the recommended installation path as the original Coqui company shut down and the repo is no longer actively maintained.

**Relevance:** HIGH — Mature, well-documented, broad language support. XTTS v2 is production-viable for narration with voice cloning. The Idiap fork ensures continued maintenance.

---

### 1.2 Bark (Suno)

| Field | Details |
|-------|---------|
| **GitHub** | [suno-ai/bark](https://github.com/suno-ai/bark) |
| **Stars** | 39k |
| **Language** | Python |
| **Last Updated** | May 2023 (no updates since) |
| **License** | MIT |

**Key Features:**
- Fully generative text-to-audio model (not just TTS)
- Generates speech, music, sound effects, laughter, sighing
- 100+ speaker presets, 12+ languages
- Can generate non-verbal sounds inline with speech (laughter, pauses)
- Automatic language detection from input text

**Quality Assessment:**
Produces highly realistic and expressive speech. However, being a generative model, outputs can deviate unpredictably from prompts. Best for ~13 seconds at a time. Requires 12GB VRAM (8GB for small model). CPU inference is very slow. **Project is effectively abandoned** — no updates in nearly 3 years.

**Relevance:** MEDIUM — Impressive expressiveness but unreliable for consistent narration. No active development. Not recommended as a primary narration engine, but useful for short expressive clips or sound effects.

---

### 1.3 Piper TTS

| Field | Details |
|-------|---------|
| **GitHub** | [rhasspy/piper](https://github.com/rhasspy/piper) (archived) / [OHF-Voice/piper1-gpl](https://github.com/OHF-Voice/piper1-gpl) (active fork) |
| **Stars** | 10.7k (original) / 3.2k (fork) |
| **Language** | C++ (92%), Python (7%) |
| **Last Updated** | Original archived Oct 2025. Fork: active |
| **License** | MIT (original) / GPL-3.0 (fork) |
| **PyPI** | `pip install piper-tts` |

**Key Features:**
- Extremely fast, lightweight neural TTS
- Designed for local/offline operation
- C++ engine with Python bindings
- Many pre-trained voice models available
- Runs efficiently on Raspberry Pi and embedded devices
- CLI, web server, Python API, and C/C++ API

**Quality Assessment:**
Good quality for a lightweight model — not as natural as XTTS or StyleTTS2, but dramatically faster and resource-efficient. Ideal for edge deployment or high-throughput scenarios. The GPL-3.0 license on the active fork is a consideration for commercial use.

**Relevance:** HIGH for speed-critical pipelines — Best-in-class speed/resource ratio. Good for draft narration, real-time applications, or when GPU resources are limited.

---

### 1.4 StyleTTS2

| Field | Details |
|-------|---------|
| **GitHub** | [yl4579/StyleTTS2](https://github.com/yl4579/StyleTTS2) |
| **Stars** | 6.2k |
| **Language** | Python (78%), Jupyter Notebook (22%) |
| **Last Updated** | March 2024 |
| **License** | MIT |

**Key Features:**
- Style diffusion + adversarial training with large speech language models
- Zero-shot speaker adaptation
- Single-speaker and multi-speaker models
- Claims to surpass human recordings on LJSpeech and match on VCTK
- Fine-tuning: ~4 hours on 4x A100s for 1 hour of speech data

**Quality Assessment:**
Among the highest quality open-source TTS engines. The claim of surpassing human recordings on LJSpeech is backed by listening tests. English-focused. Training requires significant compute. Inference is moderate speed. Less actively maintained than some alternatives.

**Relevance:** HIGH for quality — Top-tier English narration quality. The Kokoro model (see below) is actually based on StyleTTS2 architecture with optimized inference.

---

### 1.5 F5-TTS

| Field | Details |
|-------|---------|
| **GitHub** | [SWivid/F5-TTS](https://github.com/SWivid/F5-TTS) |
| **Stars** | 14.2k |
| **Language** | Python (97.5%) |
| **Last Updated** | March 2026 (v1.1.17) — actively maintained |
| **License** | MIT (code), CC-BY-NC (pretrained models) |

**Key Features:**
- Diffusion Transformer with ConvNeXt V2 architecture
- Voice cloning from reference audio + transcription
- Multi-speaker generation
- Sway Sampling for improved inference performance
- RTF 0.039 on L20 GPU, 253ms average latency
- Voice chat integration
- Custom language support

**Quality Assessment:**
Excellent quality with natural prosody. Very active development (latest release March 2026). Voice cloning is effective with short reference samples. The CC-BY-NC license on pretrained models restricts commercial use without retraining.

**Relevance:** VERY HIGH — Active development, excellent quality, fast inference. One of the best current options for voice cloning TTS. Note the NC license on pretrained weights.

---

### 1.6 MeloTTS

| Field | Details |
|-------|---------|
| **GitHub** | [myshell-ai/MeloTTS](https://github.com/myshell-ai/MeloTTS) |
| **Stars** | 7.3k |
| **Language** | Python (98%) |
| **Last Updated** | March 2024 (v0.1.2) |
| **License** | MIT |

**Key Features:**
- High-quality multilingual TTS
- Fast enough for CPU real-time inference
- Supported: English (US, UK, Indian, Australian), Spanish, French, Chinese (mixed EN), Japanese, Korean
- Built on VITS/VITS2/Bert-VITS2 architectures
- Easy installation and simple API
- Custom dataset training support

**Quality Assessment:**
Good quality across supported languages. The CPU real-time inference is a significant advantage for cost-sensitive pipelines. MIT license is commercially friendly. Development appears slowed since early 2024.

**Relevance:** HIGH for multilingual — Excellent for multi-language narration at low compute cost. MIT license is ideal for commercial use.

---

### 1.7 Fish Speech

| Field | Details |
|-------|---------|
| **GitHub** | [fishaudio/fish-speech](https://github.com/fishaudio/fish-speech) |
| **Stars** | 27.5k |
| **Language** | Python (95%) |
| **Last Updated** | Active development (2026) |
| **License** | Fish Audio Research License (restrictive) |

**Key Features:**
- Dual-Autoregressive architecture (Slow AR + Fast AR)
- Voice cloning from 10-30 second reference sample (no fine-tuning needed)
- ~50 languages supported
- Fine-grained control via natural language instructions
- RLHF alignment via GRPO
- RTF 0.195 on H200 GPU (streaming via SGLang)
- WER: 0.54% (Chinese), 0.99% (English) on Seed-TTS Eval
- 81.88% win rate on EmergentTTS-Eval

**Quality Assessment:**
State-of-the-art quality metrics. Excellent voice cloning with minimal reference audio. Strong multilingual support. The custom research license is restrictive for commercial use — must verify terms carefully.

**Relevance:** VERY HIGH — Top-tier quality and voice cloning. The license is the main concern. If license permits your use case, this is one of the best options available.

---

### 1.8 GPT-SoVITS

| Field | Details |
|-------|---------|
| **GitHub** | [RVC-Boss/GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS) |
| **Stars** | 55.8k |
| **Language** | Python |
| **Last Updated** | January 2025 |
| **License** | MIT (check specific model weights) |

**Key Features:**
- Zero-shot TTS from 5-second voice sample
- Few-shot fine-tuning with just 1 minute of training data
- Integrated voice separation, automatic dataset segmentation
- Chinese, Japanese, English, Korean, Cantonese
- WebUI for training and inference
- RTF 0.028 on RTX 4060Ti
- Multiple stable versions: v2/v3/v4/v2Pro

**Quality Assessment:**
The most popular open-source voice cloning TTS (55.8k stars). Extremely good timbre similarity and emotional expression. The 1-minute fine-tuning capability is remarkable. Primarily CJK-focused but English support is decent.

**Relevance:** VERY HIGH — Best-in-class voice cloning with minimal data. Ideal for creating consistent narrator voices. Particularly strong for CJK languages.

---

### 1.9 OpenVoice (MyShell)

| Field | Details |
|-------|---------|
| **GitHub** | [myshell-ai/OpenVoice](https://github.com/myshell-ai/OpenVoice) |
| **Stars** | 36.1k |
| **Language** | Python (86.5%), Jupyter Notebook (13.5%) |
| **Last Updated** | April 2023 (last commit to main) |
| **License** | MIT |

**Key Features:**
- Tone color cloning from reference audio
- Voice style control: emotion, accent, rhythm, pauses, intonation
- Zero-shot cross-lingual cloning
- V2: Native support for EN, ES, FR, ZH, JA, KO
- Built on VITS/VITS2 architectures
- Processes tens of millions of requests on MyShell platform

**Quality Assessment:**
Good voice cloning with strong style control. The MIT license is excellent for commercial use. However, development has stalled since April 2023. V2 improved quality significantly over V1. The architecture separates tone cloning from content generation, allowing flexible mixing.

**Relevance:** HIGH — MIT license, good quality, solid voice style control. But stale development is a concern. Consider as a voice style transfer module rather than primary TTS.

---

### 1.10 Kokoro TTS

| Field | Details |
|-------|---------|
| **GitHub** | [hexgrad/kokoro](https://github.com/hexgrad/kokoro) |
| **HuggingFace** | [hexgrad/Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M) |
| **Stars** | 6k (GitHub) / 5.8k likes (HF) |
| **Language** | JavaScript (51.5%), Python (47%) |
| **Last Updated** | January 2025 |
| **License** | Apache 2.0 |
| **Downloads** | 8.7M/month on HuggingFace |

**Key Features:**
- Only 82M parameters — extremely lightweight
- Based on StyleTTS2 + ISTFTNet vocoder (no diffusion)
- 8 languages, 54 voices (v1.0)
- Trained for ~$1,000 (1000 A100 hours)
- Under $1 per million characters / ~$0.06 per hour of audio
- 24kHz output
- Apache 2.0 license

**Quality Assessment:**
Remarkably good quality for its tiny size. Comparable to much larger models on naturalness. The Apache 2.0 license and 82M parameter count make it the most deployment-friendly option. Massive adoption (8.7M downloads/month). The efficiency is unmatched.

**Relevance:** VERY HIGH — Best cost/quality ratio. Apache 2.0 license. Ideal for high-volume production where cost and speed matter. The clear winner for lightweight deployment.

---

### 1.11 Additional Notable TTS Tools

#### ChatTTS
| Field | Details |
|-------|---------|
| **GitHub** | [2noise/ChatTTS](https://github.com/2noise/ChatTTS) |
| **Stars** | 38.9k |
| **Focus** | Conversational/dialogue speech with prosody control |
| **Languages** | Chinese (primary), English (experimental) |
| **License** | AGPL-3.0 (code), CC BY-NC 4.0 (models) |

Optimized for dialogue with fine-grained control over laughter, pauses, interjections. RTF ~0.3 on RTX 4090. Not ideal for long-form narration but excellent for conversational content.

#### Parler-TTS
| Field | Details |
|-------|---------|
| **GitHub** | [huggingface/parler-tts](https://github.com/huggingface/parler-tts) |
| **Stars** | 5.5k |
| **Focus** | Description-driven TTS — control voice via natural language |
| **Models** | Mini (880M) and Large (2.3B), trained on 45k hours |

Unique approach: describe the voice you want in text ("a woman with a clear, calm voice speaking slowly"). 34 named speakers. Interesting for variety but less control than reference-audio cloning.

#### WhisperSpeech
| Field | Details |
|-------|---------|
| **GitHub** | [collabora/WhisperSpeech](https://github.com/collabora/WhisperSpeech) |
| **Stars** | 4.6k |
| **Focus** | Inverted Whisper — commercially safe TTS |
| **Speed** | 12x faster-than-realtime on RTX 4090 |
| **License** | Apache-2.0/MIT, trained on licensed data only |

Good quality, voice cloning support, multilingual (EN, PL, FR). Fully commercially safe. Backed by Collabora and LAION.

#### EmotiVoice
| Field | Details |
|-------|---------|
| **GitHub** | [netease-youdao/EmotiVoice](https://github.com/netease-youdao/EmotiVoice) |
| **Stars** | 8.5k |
| **Focus** | Emotion-controlled TTS (happy, excited, sad, angry) |
| **Languages** | English, Chinese |
| **License** | Apache-2.0 |

2000+ voices with emotion control. Good for content needing emotional variety. OpenAI-compatible API.

#### VALL-E X
| Field | Details |
|-------|---------|
| **GitHub** | [Plachtaa/VALL-E-X](https://github.com/Plachtaa/VALL-E-X) |
| **Stars** | 8k |
| **Status** | Archived (Nov 2025) |
| **Focus** | Zero-shot voice cloning from 3-10 seconds, cross-lingual synthesis |

EN/ZH/JA support with accent control and emotion transfer. Archived but still usable.

---

## 2. Speech-to-Speech Translation

### 2.1 Meta SeamlessM4T / SeamlessStreaming

| Field | Details |
|-------|---------|
| **GitHub** | [facebookresearch/seamless_communication](https://github.com/facebookresearch/seamless_communication) |
| **Stars** | 11.8k |
| **Language** | Python |
| **Last Updated** | Active |
| **License** | CC-BY-NC 4.0 |

**Key Features:**
- **SeamlessM4T v2**: ~100 languages, speech-to-speech/speech-to-text/text-to-speech/text-to-text translation
  - Large (2.3B params), Medium (1.2B params)
- **SeamlessExpressive**: Preserves prosody, speech rate, pauses during translation
- **SeamlessStreaming**: Real-time simultaneous translation, 2.5B params
- **Seamless**: Unified model combining expressive + streaming
- Available via HuggingFace Transformers

**Quality Assessment:**
State-of-the-art multilingual translation. The expressive variant preserves vocal characteristics across languages. Streaming variant enables real-time translation. The NC license limits commercial use.

**Relevance:** VERY HIGH — The most comprehensive open-source speech translation system. Direct speech-to-speech without intermediate text is a major advantage for preserving prosody.

---

### 2.2 Meta MMS (Massively Multilingual Speech)

| Field | Details |
|-------|---------|
| **GitHub** | [facebookresearch/fairseq](https://github.com/facebookresearch/fairseq) (examples/mms) |
| **Stars** | Part of fairseq (30k+ stars) |
| **Language** | Python |
| **License** | CC-BY-NC 4.0 |

**Key Features:**
- ASR: 1,162 languages (MMS-1B-all)
- TTS: 1,100+ languages
- Language Identification: up to 4,017 languages
- Multiple model variants (FL102, L1107, all)
- Colab notebooks available

**Quality Assessment:**
Unparalleled language coverage — no other system covers even a fraction of these languages. Quality varies by language (well-resourced languages are better). TTS quality is functional but not state-of-the-art for major languages.

**Relevance:** HIGH for rare languages — If you need to reach languages that no other TTS supports, MMS is the only option. For major languages, other tools produce better quality.

---

### 2.3 NVIDIA NeMo (Canary)

| Field | Details |
|-------|---------|
| **GitHub** | [NVIDIA/NeMo](https://github.com/NVIDIA/NeMo) |
| **Stars** | 16.9k |
| **Language** | Python |
| **Last Updated** | Active (Dec 2024+) |
| **License** | Apache-2.0 |

**Key Features:**
- Canary model: Transcription + bidirectional translation (EN <-> ES, DE, FR)
- Full ASR + TTS framework
- Highly optimized inference (RTFx up to 6,000)
- Apache-2.0 license is commercially friendly

**Relevance:** MEDIUM — Good for EN/ES/DE/FR translation pipelines with commercial-friendly licensing, but limited language coverage compared to SeamlessM4T.

---

### 2.4 ESPnet

| Field | Details |
|-------|---------|
| **GitHub** | [espnet/espnet](https://github.com/espnet/espnet) |
| **Stars** | 9.8k |
| **Language** | Python |
| **Last Updated** | Active |

**Key Features:**
- End-to-end speech translation (comparable/superior to cascaded ASR+MT)
- TTS: Tacotron2, FastSpeech2, VITS, and more
- Multiple vocoders: HiFiGAN, ParallelWaveGAN
- Research-grade toolkit with many pre-trained recipes

**Relevance:** MEDIUM — Excellent research toolkit but requires more expertise to deploy in production compared to purpose-built tools.

---

### 2.5 Building a Speech Translation Pipeline

For automated video production, the practical approach to speech-to-speech translation is a **cascaded pipeline**:

```
Source Audio → Transcription → Translation → Target Language TTS
```

**Recommended Stack:**

| Stage | Tool | Why |
|-------|------|-----|
| Transcription | faster-whisper or WhisperX | Fast, accurate, word-level timestamps |
| Translation | SeamlessM4T (text-to-text mode) or external API | Best open-source quality |
| TTS | F5-TTS / Fish Speech / Kokoro | Voice cloning to match original speaker |
| Lip Sync (optional) | Wav2Lip | Match new audio to original video |

**Alternative: Direct Speech-to-Speech**

| Tool | Pros | Cons |
|------|------|------|
| SeamlessM4T S2S | Preserves prosody, single model | NC license, lower control over output |
| SeamlessExpressive | Best prosody preservation | NC license, large model |
| Cascaded pipeline | Full control, mix-and-match | More complex, potential quality loss at each stage |

**For production use**, the cascaded approach gives more control: you can review/edit transcripts and translations before synthesis, use different TTS voices, and handle errors at each stage independently.

---

## 3. Audio Processing & Manipulation

### 3.1 FFmpeg Audio Filters

| Field | Details |
|-------|---------|
| **Tool** | FFmpeg (ffmpeg.org) |
| **Type** | CLI tool / library |
| **License** | LGPL/GPL |

**Key Audio Filters for Video Production:**
- `loudnorm` — EBU R128 loudness normalization (essential for consistent volume)
- `anlmdn` — Non-local means denoising (noise reduction)
- `afftdn` — FFT-based noise reduction
- `acompressor` — Dynamic range compression
- `highpass` / `lowpass` — Frequency filtering
- `equalizer` — Parametric EQ
- `silenceremove` — Remove silence
- `crossfade` — Audio crossfading
- `amix` — Mix multiple audio streams
- `volume` — Volume adjustment

**Relevance:** ESSENTIAL — FFmpeg is the backbone of any audio/video pipeline. The `loudnorm` filter is critical for broadcast-standard audio normalization.

---

### 3.2 SoX (Sound eXchange)

| Field | Details |
|-------|---------|
| **Tool** | SoX (sox.sourceforge.net) |
| **Type** | CLI tool |
| **License** | GPL |

**Key Features:**
- Format conversion (supports 20+ audio formats)
- Effects: reverb, echo, flanger, chorus, speed, pitch, tempo
- Noise reduction via noise profile
- Silence trimming, padding
- Statistical analysis
- Batch processing via shell scripts

**Relevance:** MEDIUM — Largely superseded by FFmpeg and Pedalboard for modern pipelines, but still useful for specific effects and batch operations.

---

### 3.3 Pedalboard (Spotify)

| Field | Details |
|-------|---------|
| **GitHub** | [spotify/pedalboard](https://github.com/spotify/pedalboard) |
| **Stars** | 6k+ |
| **Language** | C++ with Python bindings |
| **Last Updated** | December 2024 |
| **License** | GPL-3.0 |

**Key Features:**
- Studio-quality audio effects: Compressor, Gain, Limiter, Reverb, Delay, Chorus, Distortion, PitchShift
- VST3/Audio Unit plugin support (load any professional audio plugin)
- 300x faster than pySoX for single transforms
- 4x faster than librosa.load for file reading
- O(1) memory resampling
- Releases Python GIL for multi-core processing
- Supports AIFF, FLAC, MP3, OGG, WAV
- Real-time streaming via AudioStream
- TensorFlow tf.data pipeline integration

**Quality Assessment:**
Production-tested at Spotify. The ability to load VST3 plugins means you can use any professional audio effect. Excellent Python API. The GPL-3.0 license requires consideration for proprietary software.

**Relevance:** VERY HIGH — Best Python library for audio effects processing. The VST3 support is uniquely powerful. Ideal for post-processing TTS output to sound professional.

---

### 3.4 Demucs (Meta) — Source Separation

| Field | Details |
|-------|---------|
| **GitHub** | [facebookresearch/demucs](https://github.com/facebookresearch/demucs) (archived) / [adefossez/demucs](https://github.com/adefossez/demucs) (community fork) |
| **Stars** | 9.8k |
| **Language** | Python |
| **Last Updated** | January 2025 (archived) |
| **License** | MIT |

**Key Features:**
- Hybrid Transformer-based source separation
- Separates: vocals, drums, bass, other (4 stems)
- Experimental 6-source: adds guitar and piano
- Best model (htdemucs_ft): 9.0 dB SDR on MUSDB HQ
- GPU/CPU processing
- Batch processing, karaoke mode (isolate single stem)
- Python API available

**Quality Assessment:**
State-of-the-art source separation quality. Essential for isolating vocals from background music/noise. The archived status is concerning but the MIT license and existing quality make it still very usable. Community fork provides limited maintenance.

**Relevance:** HIGH — Critical for cleaning audio, isolating vocals, removing background noise from source material. No better open-source alternative exists.

---

### 3.5 Whisper & faster-whisper (Transcription)

#### OpenAI Whisper

| Field | Details |
|-------|---------|
| **GitHub** | [openai/whisper](https://github.com/openai/whisper) |
| **Stars** | 96k |
| **Language** | Python |
| **Last Updated** | June 2025 (v20250625) |
| **License** | MIT |

- 99+ languages, multiple model sizes (39M to 1.55B params)
- Turbo model: 809M params, 8x speed with minimal accuracy loss
- Word-level timestamps

#### faster-whisper

| Field | Details |
|-------|---------|
| **GitHub** | [SYSTRAN/faster-whisper](https://github.com/SYSTRAN/faster-whisper) |
| **Stars** | 21.5k |
| **Language** | Python |
| **Last Updated** | Active |
| **License** | MIT |

- 4x faster than OpenAI Whisper, same accuracy, less memory
- INT8 quantization on CPU and GPU
- Batched transcription
- Integrated Silero VAD filtering
- Compatible with Distil-Whisper models

#### WhisperX

| Field | Details |
|-------|---------|
| **GitHub** | [m-bain/whisperX](https://github.com/m-bain/whisperX) |
| **Stars** | 20.7k |
| **Features** | 70x realtime, word-level timestamps via wav2vec2, speaker diarization |

#### stable-ts

| Field | Details |
|-------|---------|
| **GitHub** | [jianfch/stable-ts](https://github.com/jianfch/stable-ts) |
| **Stars** | 2.2k |
| **Features** | Stabilized timestamps, SRT/VTT/ASS export, works with faster-whisper |

**Relevance:** ESSENTIAL — Transcription is foundational. Use **faster-whisper** for speed, **WhisperX** for word-level timestamps + diarization, **stable-ts** for subtitle generation.

---

### 3.6 Silero VAD

| Field | Details |
|-------|---------|
| **GitHub** | [snakers4/silero-vad](https://github.com/snakers4/silero-vad) |
| **Stars** | 8.5k |
| **Language** | Python (89%) |
| **Last Updated** | February 2026 (v6.2.1) — actively maintained |
| **License** | MIT |

**Key Features:**
- <1ms per audio chunk on CPU
- ~2MB model size
- Trained on 6,000+ languages
- 8kHz and 16kHz support
- Implementations: Python, C++, Rust, Go, Java, C#, browser (ONNX Web)
- PyTorch and ONNX runtimes

**Relevance:** HIGH — Essential preprocessing step for transcription and TTS. Detecting speech segments reduces Whisper hallucinations and enables intelligent audio segmentation. Tiny, fast, reliable.

---

### 3.7 pyannote-audio (Speaker Diarization)

| Field | Details |
|-------|---------|
| **GitHub** | [pyannote/pyannote-audio](https://github.com/pyannote/pyannote-audio) |
| **Stars** | 9.3k |
| **Language** | Python |
| **Last Updated** | February 2026 (v4.0.4) — actively maintained |
| **License** | MIT |

**Key Features:**
- State-of-the-art speaker diarization
- Voice activity detection, speaker segmentation
- Overlapped speech detection
- Speaker embedding generation
- ~11.7% DER on AISHELL-4 benchmark
- Multi-GPU training via PyTorch Lightning
- HuggingFace model hosting

**Relevance:** HIGH — Essential for multi-speaker content (interviews, podcasts). Identifies who speaks when. Integrates with WhisperX for transcription + diarization in one pipeline.

---

### 3.8 Resemblyzer

| Field | Details |
|-------|---------|
| **GitHub** | [resemble-ai/Resemblyzer](https://github.com/resemble-ai/Resemblyzer) |
| **Stars** | 3.2k |
| **Language** | Python |
| **Last Updated** | August 2019 (stale) |
| **License** | Apache-2.0 |

**Key Features:**
- 256-dimensional voice embeddings
- Speaker verification from 5-30 second samples
- Speaker diarization
- Fake speech detection
- ~1000x real-time on GTX 1080

**Relevance:** LOW-MEDIUM — Useful for speaker verification/matching but largely superseded by pyannote-audio for diarization. Very old codebase but still functional.

---

### 3.9 Audio Normalization Tools

#### ffmpeg-normalize

| Field | Details |
|-------|---------|
| **PyPI** | [ffmpeg-normalize](https://pypi.org/project/ffmpeg-normalize/) |
| **Version** | 1.37.3 (Feb 2026) |
| **License** | MIT |

- EBU R128 loudness normalization (two-pass and one-pass)
- RMS-based normalization
- Peak normalization
- Batch/album normalization (maintain relative loudness)
- Python API for programmatic use
- Video file support (preserves video streams)

#### pydub

| Field | Details |
|-------|---------|
| **GitHub** | [jianfch/pydub](https://github.com/jiaaro/pydub) |
| **Stars** | 9.7k |
| **License** | MIT |

- Simple audio manipulation (slice, concatenate, volume, crossfade, fade)
- Format conversion via FFmpeg backend
- Used by 108k+ dependent repos
- Good for simple operations, not for heavy processing

**Relevance:** HIGH — ffmpeg-normalize is essential for ensuring consistent audio levels across all produced videos. EBU R128 is the broadcast standard. pydub is useful for quick audio manipulation tasks.

---

## 4. Music Generation (Background Music)

### 4.1 MusicGen / AudioCraft (Meta)

| Field | Details |
|-------|---------|
| **GitHub** | [facebookresearch/audiocraft](https://github.com/facebookresearch/audiocraft) |
| **Stars** | 23.1k |
| **Language** | Python (with Jupyter notebooks) |
| **Last Updated** | Active |
| **License** | MIT (code), CC-BY-NC 4.0 (model weights) |

**Key Features:**
- **MusicGen**: Text-to-music with textual and melodic conditioning
- **AudioGen**: Text-to-sound effects
- **MAGNeT**: Non-autoregressive generation (faster)
- **EnCodec**: Neural audio codec
- **AudioSeal**: Audio watermarking
- Style-based music generation

**Quality Assessment:**
MusicGen produces surprisingly good music from text prompts. Melodic conditioning allows humming a melody and getting a full arrangement. AudioGen handles sound effects well. The NC license on model weights limits commercial use.

**Relevance:** VERY HIGH — Best open-source music generation. MusicGen for background music, AudioGen for sound effects. Essential for automated video production. The NC license is the main limitation.

---

### 4.2 Stable Audio Open

| Field | Details |
|-------|---------|
| **GitHub** | [Stability-AI/stable-audio-tools](https://github.com/Stability-AI/stable-audio-tools) |
| **Stars** | 3.6k |
| **Language** | Python |
| **Last Updated** | December 2024 |
| **License** | MIT |

**Key Features:**
- Training and inference for audio generation models
- Diffusion-based and autoencoder architectures
- Supports mono and stereo, various sample rates
- Fine-tuning pre-trained models
- Gradio interface for testing
- Distributed training (multi-GPU/multi-node)
- Weights & Biases integration

**Quality Assessment:**
Good quality audio generation. The MIT license on code is good, but model weights availability and licensing vary. Less community adoption than AudioCraft. Good for custom-trained music generation.

**Relevance:** MEDIUM — Good alternative to AudioCraft, especially if you need to train custom models. Less out-of-the-box ready.

---

### 4.3 Riffusion

| Field | Details |
|-------|---------|
| **GitHub** | [riffusion/riffusion](https://github.com/riffusion/riffusion) |
| **Stars** | 3.9k |
| **Language** | Python |
| **Last Updated** | December 2022 (abandoned) |
| **License** | MIT |

**Key Features:**
- Generates music via Stable Diffusion applied to spectrograms
- Prompt interpolation for smooth transitions between styles
- Real-time generation on capable GPUs

**Quality Assessment:**
Innovative spectrogram approach but quality is below MusicGen. Project is abandoned since late 2022. Historical interest only.

**Relevance:** LOW — Abandoned, lower quality than AudioCraft/MusicGen. Not recommended for production use.

---

### 4.4 Tango / TangoFlux

| Field | Details |
|-------|---------|
| **GitHub** | [declare-lab/tango](https://github.com/declare-lab/tango) |
| **Stars** | 1.2k |
| **License** | Available |

**Key Features:**
- Latent diffusion model for text-to-audio
- Tango 2: DPO-aligned, strong quality metrics (FAD 2.69, IS 9.09)
- **TangoFlux**: 30 seconds of audio in <3 seconds
- **Mustango**: Music-specialized variant
- **Jamify**: Lyrics-to-song generator

**Relevance:** MEDIUM-HIGH — TangoFlux is very fast. Mustango is specifically good for music. Worth evaluating alongside AudioCraft.

---

### 4.5 AudioLDM2

| Field | Details |
|-------|---------|
| **GitHub** | [haoheliu/AudioLDM2](https://github.com/haoheliu/AudioLDM2) |
| **Stars** | 2.6k |
| **Last Updated** | August 2023 |

**Key Features:**
- Text-to-audio and music generation
- 48kHz high-fidelity checkpoint
- Integrates with HuggingFace Diffusers (3x faster)
- Super resolution inpainting

**Relevance:** MEDIUM — Good quality, HuggingFace integration is convenient. Less active than AudioCraft.

---

## 5. Comparison Tables

### 5.1 TTS Quality & Practicality Comparison

| Tool | Quality (1-10) | Speed | Voice Cloning | Languages | License | Active Dev | Best For |
|------|:---:|:---:|:---:|:---:|:---:|:---:|------|
| **Kokoro** | 8 | Fastest | No | 8 | Apache-2.0 | Yes | High-volume production, cost-sensitive |
| **F5-TTS** | 9 | Fast | Yes (ref audio) | Custom | MIT/CC-BY-NC | Yes (2026) | Quality narration with voice cloning |
| **Fish Speech** | 9.5 | Fast | Yes (10-30s) | ~50 | Restrictive | Yes | Top quality, multilingual |
| **GPT-SoVITS** | 9 | Fast (RTF 0.028) | Yes (5s zero-shot, 1min fine-tune) | 5 (CJK+EN) | MIT | Yes | Voice cloning, CJK content |
| **Coqui XTTS v2** | 8 | Moderate | Yes (6-10s) | 16 | MPL-2.0 | Fork only | Mature, well-documented |
| **StyleTTS2** | 9.5 | Moderate | Zero-shot adapt | EN-focused | MIT | Slow | Highest English quality |
| **OpenVoice** | 7.5 | Fast | Yes (style transfer) | 6 | MIT | No | Voice style control |
| **MeloTTS** | 7.5 | CPU real-time | No | 6 | MIT | Slow | CPU deployment, multilingual |
| **Piper** | 6.5 | Fastest | No | Many | GPL-3.0 | Fork | Edge/embedded, real-time |
| **Bark** | 8 | Slow | No | 12+ | MIT | No | Expressive clips, sound effects |
| **ChatTTS** | 8 | Moderate | No | 2 (ZH, EN) | AGPL/CC-BY-NC | Yes | Conversational content |
| **Parler-TTS** | 7.5 | Moderate | Description-based | EN | Apache-2.0 | Slow | Voice variety via text descriptions |
| **WhisperSpeech** | 7 | 12x RT | Yes | 3 | Apache-2.0 | Moderate | Commercially safe pipeline |
| **EmotiVoice** | 7 | Moderate | No | 2 (EN, ZH) | Apache-2.0 | Moderate | Emotion-controlled narration |

### 5.2 Speech Translation Quality Comparison

| Tool | S2S Direct | Languages | Quality (1-10) | Speed | License | Best For |
|------|:---:|:---:|:---:|:---:|:---:|------|
| **SeamlessM4T v2** | Yes | ~100 | 9 | Moderate | CC-BY-NC | Best quality, most languages |
| **SeamlessExpressive** | Yes | ~100 | 9.5 (prosody) | Moderate | CC-BY-NC | Preserving speaker style |
| **SeamlessStreaming** | Yes | ~100 | 8.5 | Real-time | CC-BY-NC | Live/streaming translation |
| **Meta MMS** | No (ASR+TTS) | 1,100+ | 7 | Moderate | CC-BY-NC | Rare/low-resource languages |
| **NeMo Canary** | No (cascaded) | 4 | 8 | Very fast | Apache-2.0 | Commercial EN/ES/DE/FR |
| **ESPnet** | Yes (E2E) | Multiple | 8 | Moderate | Apache-2.0 | Research, customization |
| **Cascaded Pipeline** | N/A | Any | 8-9 | Varies | Varies | Full control, production |

### 5.3 Audio Processing Tool Comparison

| Tool | Task | Speed | Quality | Ease of Use | License |
|------|------|:---:|:---:|:---:|:---:|
| **FFmpeg** | General processing | Fast | High | CLI-moderate | LGPL/GPL |
| **Pedalboard** | Effects/processing | 300x pySoX | Studio-grade | Python-easy | GPL-3.0 |
| **Demucs** | Source separation | GPU-fast | SOTA (9.0 dB SDR) | Easy | MIT |
| **faster-whisper** | Transcription | 4x Whisper | Same as Whisper | Easy | MIT |
| **WhisperX** | Transcription+diarization | 70x RT | High | Easy | BSD |
| **Silero VAD** | Voice detection | <1ms/chunk | High | Very easy | MIT |
| **pyannote** | Speaker diarization | Moderate | SOTA | Moderate | MIT |
| **ffmpeg-normalize** | Loudness normalization | Fast | Broadcast-standard | Very easy | MIT |
| **pydub** | Simple manipulation | Fast | Good | Very easy | MIT |
| **SoX** | CLI processing | Fast | Good | CLI-moderate | GPL |

### 5.4 Music Generation Comparison

| Tool | Quality (1-10) | Speed | Control | License (weights) | Active |
|------|:---:|:---:|:---:|:---:|:---:|
| **MusicGen (AudioCraft)** | 8.5 | Moderate | Text + melody | CC-BY-NC | Yes |
| **AudioGen (AudioCraft)** | 8 | Moderate | Text | CC-BY-NC | Yes |
| **Stable Audio Open** | 7.5 | Moderate | Text | Varies | Yes |
| **TangoFlux** | 7.5 | Very fast (3s/30s) | Text | Check | Moderate |
| **Mustango** | 7 | Moderate | Text (music-specific) | Check | Moderate |
| **AudioLDM2** | 7.5 | Moderate | Text | Check | No |
| **Riffusion** | 6 | Moderate | Text | MIT | No |

---

## 6. Practical Pipeline Recommendations

### 6.1 Recommended Video Production Audio Pipeline

```
┌─────────────────────────────────────────────────────────┐
│                   INPUT PROCESSING                       │
├─────────────────────────────────────────────────────────┤
│  Source Audio → Silero VAD → faster-whisper → Transcript │
│  Source Audio → Demucs → Isolated Vocals + Music         │
│  Multi-speaker → WhisperX + pyannote → Who said what     │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   NARRATION GENERATION                   │
├─────────────────────────────────────────────────────────┤
│  Script → Kokoro TTS (high volume, Apache-2.0)          │
│  Script → F5-TTS (voice cloning needed)                  │
│  Script → GPT-SoVITS (best voice cloning, CJK)          │
│  Script → Fish Speech (top quality, check license)       │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  TRANSLATION (if needed)                  │
├─────────────────────────────────────────────────────────┤
│  Option A: SeamlessM4T (direct S2S, best quality)        │
│  Option B: faster-whisper → translate → F5-TTS           │
│  Option C: NeMo Canary (commercial, EN/ES/DE/FR)         │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   POST-PROCESSING                        │
├─────────────────────────────────────────────────────────┤
│  TTS Output → Pedalboard (EQ, compression, reverb)       │
│  → ffmpeg-normalize (EBU R128 loudness)                  │
│  → FFmpeg (mix narration + background music + SFX)       │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   BACKGROUND MUSIC                       │
├─────────────────────────────────────────────────────────┤
│  MusicGen → Background music from text description       │
│  AudioGen → Sound effects from text description          │
│  FFmpeg amix → Layer music under narration               │
└─────────────────────────────────────────────────────────┘
```

### 6.2 Tier 1: Commercial-Safe Pipeline (Apache-2.0 / MIT only)

For projects requiring fully commercial-safe licensing:

| Stage | Tool | License |
|-------|------|---------|
| Transcription | faster-whisper | MIT |
| VAD | Silero VAD | MIT |
| Diarization | pyannote-audio | MIT |
| TTS (primary) | **Kokoro** | Apache-2.0 |
| TTS (alternative) | WhisperSpeech | Apache-2.0 |
| TTS (emotional) | EmotiVoice | Apache-2.0 |
| Voice cloning | GPT-SoVITS | MIT |
| Source separation | Demucs | MIT |
| Audio effects | pydub + FFmpeg | MIT / LGPL |
| Normalization | ffmpeg-normalize | MIT |
| Translation | NeMo Canary | Apache-2.0 |

**Note:** Pedalboard (GPL-3.0) is excluded here. Use FFmpeg filters as replacement for audio effects if GPL is unacceptable.

### 6.3 Tier 2: Maximum Quality Pipeline (NC-licensed tools OK for research/personal)

| Stage | Tool | Why |
|-------|------|-----|
| Transcription | faster-whisper (large-v3) | Best accuracy |
| TTS | Fish Speech or F5-TTS | Highest quality + voice cloning |
| Translation | SeamlessM4T v2 (Expressive) | Best prosody preservation |
| Music | MusicGen (AudioCraft) | Best music generation |
| SFX | AudioGen (AudioCraft) | Best sound effects |
| Audio FX | Pedalboard | Studio-quality processing |
| Normalization | ffmpeg-normalize | Broadcast standard |

### 6.4 Tier 3: Lightweight / Edge Pipeline (CPU-only, low resource)

| Stage | Tool | Why |
|-------|------|-----|
| Transcription | faster-whisper (small/base) | Fast on CPU |
| VAD | Silero VAD | <1ms, 2MB model |
| TTS | Kokoro (82M params) | Tiny, fast, good quality |
| TTS (alternative) | Piper | C++ speed, minimal resources |
| TTS (multilingual) | MeloTTS | CPU real-time |
| Audio processing | FFmpeg | Universal, fast |

### 6.5 Key Decision Matrix

**"Which TTS should I use?"**

- Need **Apache-2.0 license + good quality** → **Kokoro**
- Need **voice cloning + high quality** → **F5-TTS** or **GPT-SoVITS**
- Need **best absolute quality** → **Fish Speech** (check license)
- Need **50+ languages** → **Fish Speech** or **Coqui XTTS v2**
- Need **CPU-only deployment** → **Kokoro** or **MeloTTS** or **Piper**
- Need **emotional/expressive speech** → **EmotiVoice** or **ChatTTS**
- Need **CJK focus** → **GPT-SoVITS**

**"Which transcription tool?"**

- General use → **faster-whisper**
- Need word timestamps + diarization → **WhisperX**
- Need subtitle generation → **stable-ts**
- Edge deployment → **sherpa-onnx** (10.8k stars, mobile/embedded support)

**"Which music generator?"**

- Best quality → **MusicGen** (AudioCraft)
- Need sound effects → **AudioGen** (AudioCraft)
- Need speed → **TangoFlux** (30s audio in 3s)
- Need to train custom → **Stable Audio Tools**

---

## Appendix: Quick Reference — GitHub Stars Ranking

| Rank | Tool | Stars | Category |
|------|------|------:|----------|
| 1 | OpenAI Whisper | 96k | Transcription |
| 2 | GPT-SoVITS | 55.8k | TTS / Voice Cloning |
| 3 | Coqui TTS | 44.8k | TTS |
| 4 | Bark | 39k | TTS / Audio Gen |
| 5 | ChatTTS | 38.9k | TTS (Conversational) |
| 6 | OpenVoice | 36.1k | Voice Cloning |
| 7 | Fish Speech | 27.5k | TTS / Voice Cloning |
| 8 | AudioCraft | 23.1k | Music / Audio Gen |
| 9 | faster-whisper | 21.5k | Transcription |
| 10 | WhisperX | 20.7k | Transcription + Diarization |
| 11 | NVIDIA NeMo | 16.9k | ASR / TTS Framework |
| 12 | F5-TTS | 14.2k | TTS / Voice Cloning |
| 13 | Wav2Lip | 12.9k | Lip Sync |
| 14 | SeamlessM4T | 11.8k | Speech Translation |
| 15 | Sherpa-ONNX | 10.8k | Edge ASR/TTS |
| 16 | Piper (original) | 10.7k | Lightweight TTS |
| 17 | Mozilla TTS | 10.1k | TTS (legacy) |
| 18 | ESPnet | 9.8k | Speech Toolkit |
| 19 | Demucs | 9.8k | Source Separation |
| 20 | pydub | 9.7k | Audio Manipulation |
| 21 | Amphion | 9.7k | Audio/Speech Toolkit |
| 22 | pyannote-audio | 9.3k | Speaker Diarization |
| 23 | Bert-VITS2 | 8.7k | TTS (CJK) |
| 24 | Silero VAD | 8.5k | Voice Activity Detection |
| 25 | EmotiVoice | 8.5k | Emotional TTS |
| 26 | VALL-E X | 8k | Voice Cloning TTS |
| 27 | MeloTTS | 7.3k | Multilingual TTS |
| 28 | StyleTTS2 | 6.2k | High-Quality TTS |
| 29 | Kokoro | 6k | Lightweight TTS |
| 30 | Pedalboard | 6k | Audio Effects |
| 31 | Parler-TTS | 5.5k | Description-based TTS |
| 32 | WhisperSpeech | 4.6k | Commercially-safe TTS |
| 33 | EnCodec | 3.9k | Audio Codec |
| 34 | Riffusion | 3.9k | Music Gen (abandoned) |
| 35 | Stable Audio Tools | 3.6k | Music Gen |
| 36 | Resemblyzer | 3.2k | Speaker Embedding |
| 37 | Piper (OHF fork) | 3.2k | Lightweight TTS |
| 38 | AudioLDM2 | 2.6k | Audio Gen |
| 39 | stable-ts | 2.2k | Timestamp Stabilization |
| 40 | Idiap Coqui fork | 2.2k | TTS (maintained fork) |
| 41 | Tango | 1.2k | Audio Gen |
