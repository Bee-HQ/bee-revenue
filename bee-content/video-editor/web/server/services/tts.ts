import fs from 'node:fs';
import path from 'node:path';
import type { BeeSegment } from '../../shared/types.js';

// --- TTSEngine interface ---

interface TTSEngine {
  generate(text: string, voice: string, outputPath: string): Promise<void>;
}

export const VALID_ENGINES = ['edge', 'elevenlabs', 'openai'] as const;
type EngineName = (typeof VALID_ENGINES)[number];

export const DEFAULT_VOICES: Record<EngineName, string> = {
  edge: 'en-US-GuyNeural',
  elevenlabs: 'onwK4e9ZLuTAKqWV03F9', // "Daniel"
  openai: 'onyx',
};

// --- Engine implementations (lazy-loaded SDKs) ---

class EdgeTTSEngine implements TTSEngine {
  async generate(text: string, voice: string, outputPath: string): Promise<void> {
    const { EdgeTTS } = await import('node-edge-tts');
    const tts = new EdgeTTS({
      voice,
      rate: '-5%',
      outputFormat: 'audio-24khz-96kbitrate-mono-mp3',
    });
    await tts.ttsPromise(text, outputPath);
  }
}

class ElevenLabsEngine implements TTSEngine {
  async generate(text: string, voice: string, outputPath: string): Promise<void> {
    const { ElevenLabsClient } = await import('@elevenlabs/elevenlabs-js');
    const client = new ElevenLabsClient(); // uses ELEVENLABS_API_KEY env var
    const audio = await client.textToSpeech.convert(voice, {
      text,
      modelId: 'eleven_multilingual_v2',
      outputFormat: 'mp3_44100_128',
    });
    const chunks: Buffer[] = [];
    for await (const chunk of audio as AsyncIterable<Uint8Array>) {
      chunks.push(Buffer.from(chunk));
    }
    await fs.promises.writeFile(outputPath, Buffer.concat(chunks));
  }
}

class OpenAIEngine implements TTSEngine {
  async generate(text: string, voice: string, outputPath: string): Promise<void> {
    const { default: OpenAI } = await import('openai');
    const client = new OpenAI(); // uses OPENAI_API_KEY env var
    const response = await client.audio.speech.create({
      model: 'gpt-4o-mini-tts',
      voice: voice as 'alloy' | 'echo' | 'fable' | 'onyx' | 'nova' | 'shimmer',
      input: text,
    });
    const buffer = Buffer.from(await response.arrayBuffer());
    await fs.promises.writeFile(outputPath, buffer);
  }
}

// --- Factory ---

const engines: Record<EngineName, TTSEngine> = {
  edge: new EdgeTTSEngine(),
  elevenlabs: new ElevenLabsEngine(),
  openai: new OpenAIEngine(),
};

function getEngine(name: string): TTSEngine {
  const engine = engines[name as EngineName];
  if (!engine) {
    throw new Error(`Unknown TTS engine: ${name}. Available: ${VALID_ENGINES.join(', ')}`);
  }
  return engine;
}

// --- Text cleaning (matches Python _clean_text) ---

export function cleanNarrationText(raw: string): string {
  let text = raw.replace(/\s*\+\s*.*$/, ''); // Remove + notes
  text = text.trim().replace(/^["\u201c]+|["\u201d]+$/g, ''); // Strip quotes
  return text.trim();
}

// --- Narration generator ---

export interface NarrationResult {
  succeeded: string[];
  failed: Array<{ file: string; error: string }>;
}

export async function generateNarration(
  segments: BeeSegment[],
  engine: string,
  voice: string | undefined,
  outputDir: string,
  onProgress?: (done: number, total: number) => void,
): Promise<NarrationResult> {
  const ttsEngine = getEngine(engine);
  const resolvedVoice = voice || DEFAULT_VOICES[engine as EngineName] || DEFAULT_VOICES.edge;

  await fs.promises.mkdir(outputDir, { recursive: true });

  // Collect narration tasks
  const tasks: Array<{ segId: string; text: string; outputPath: string }> = [];
  for (const seg of segments) {
    const narEntry = seg.audio.find(a => a.type === 'NAR');
    if (!narEntry?.text) continue;
    const cleanText = cleanNarrationText(narEntry.text);
    if (!cleanText) continue;
    const outputPath = path.join(outputDir, `${seg.id}.mp3`);
    if (fs.existsSync(outputPath)) continue; // skip already generated
    tasks.push({ segId: seg.id, text: cleanText, outputPath });
  }

  const result: NarrationResult = { succeeded: [], failed: [] };
  const total = tasks.length;

  for (let i = 0; i < tasks.length; i++) {
    const task = tasks[i];
    try {
      await ttsEngine.generate(task.text, resolvedVoice, task.outputPath);
      result.succeeded.push(task.outputPath);
    } catch (err) {
      result.failed.push({ file: `${task.segId}.mp3`, error: String(err) });
    }
    onProgress?.(i + 1, total);
  }

  return result;
}

// --- Background narration task state ---

export interface NarrationTaskState {
  running: boolean;
  done: number;
  total: number;
  projectDir: string;
  status?: string;
  succeeded: string[];
  failed: Array<{ file: string; error: string }>;
}

let narrationTask: NarrationTaskState | null = null;

export function getNarrationTask(): NarrationTaskState | null {
  return narrationTask;
}

export function resetNarrationTask(): void {
  narrationTask = null;
}

function countPendingNarrations(segments: BeeSegment[], outputDir: string): number {
  let count = 0;
  for (const seg of segments) {
    const narEntry = seg.audio.find(a => a.type === 'NAR');
    if (!narEntry?.text) continue;
    const cleanText = cleanNarrationText(narEntry.text);
    if (!cleanText) continue;
    if (!fs.existsSync(path.join(outputDir, `${seg.id}.mp3`))) count++;
  }
  return count;
}

export function startNarrationTask(
  segments: BeeSegment[],
  engine: string,
  voice: string | undefined,
  outputDir: string,
  projectDir: string,
): { total: number } {
  if (narrationTask?.running) {
    throw new Error('Narration is already running');
  }

  const total = countPendingNarrations(segments, outputDir);

  if (total === 0) {
    // Don't clobber results from a previous completed run
    if (!narrationTask || narrationTask.projectDir !== projectDir) {
      narrationTask = {
        running: false,
        done: 0,
        total: 0,
        projectDir,
        status: 'ok',
        succeeded: [],
        failed: [],
      };
    }
    return { total: 0 };
  }

  narrationTask = { running: true, done: 0, total, projectDir, succeeded: [], failed: [] };

  // Fire-and-forget async — runs on the event loop
  generateNarration(segments, engine, voice, outputDir, (done) => {
    if (narrationTask) narrationTask.done = done;
  })
    .then((result) => {
      if (!narrationTask) return;
      narrationTask.running = false;
      narrationTask.succeeded = result.succeeded;
      narrationTask.failed = result.failed;
      narrationTask.status =
        result.failed.length === 0
          ? 'ok'
          : result.succeeded.length > 0
            ? 'partial'
            : 'error';
    })
    .catch((err) => {
      if (!narrationTask) return;
      narrationTask.running = false;
      narrationTask.status = 'error';
      narrationTask.failed = [{ file: '', error: String(err) }];
    });

  return { total };
}
