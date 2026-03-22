import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import type { BeeProject, BeeSegment, ProductionState } from '../../shared/types.js';
import { parseStoryboardMarkdown } from '../../shared/storyboard-parser.js';

// ---------- Error helper ----------

function httpError(status: number, message: string): Error {
  const err = new Error(message) as Error & { status: number };
  err.status = status;
  return err;
}

// ---------- ProjectStore ----------

class ProjectStore {
  private project: BeeProject | null = null;
  private projectDir: string | null = null;
  private jsonPath: string | null = null;

  // ---------- Load ----------

  loadFromMarkdown(mdPath: string, projectDir: string): BeeProject {
    const resolvedPath = path.isAbsolute(mdPath) ? mdPath : path.resolve(projectDir, mdPath);
    const markdown = fs.readFileSync(resolvedPath, 'utf-8');
    const project = parseStoryboardMarkdown(markdown);
    this.project = project;
    this.projectDir = projectDir;
    this.jsonPath = path.join(projectDir, '.bee-project.json');
    fs.writeFileSync(this.jsonPath, JSON.stringify(project, null, 2), 'utf-8');
    this.writeSessionFiles();
    return project;
  }

  loadFromJson(jsonPath: string): BeeProject {
    const raw = fs.readFileSync(jsonPath, 'utf-8');
    const project = JSON.parse(raw) as BeeProject;
    this.project = project;
    this.jsonPath = jsonPath;
    this.projectDir = path.dirname(jsonPath);
    return project;
  }

  // ---------- Accessors ----------

  get(): BeeProject {
    if (!this.project) throw httpError(404, 'No project loaded');
    return this.project;
  }

  getProjectDir(): string {
    if (!this.projectDir) throw httpError(404, 'No project loaded');
    return this.projectDir;
  }

  // ---------- Persistence ----------

  save(): void {
    if (!this.project || !this.jsonPath) throw httpError(404, 'No project loaded');
    this.project.updatedAt = new Date().toISOString();
    fs.writeFileSync(this.jsonPath, JSON.stringify(this.project, null, 2), 'utf-8');
  }

  // ---------- Mutations ----------

  assignMedia(segId: string, layer: string, index: number, filePath: string): BeeProject {
    const project = this.get();
    const seg = this.findSegment(project, segId);

    if (layer === 'visual') {
      if (!seg.visual[index]) throw httpError(400, `visual[${index}] does not exist`);
      seg.visual[index].src = filePath;
    } else if (layer === 'audio') {
      if (!seg.audio[index]) throw httpError(400, `audio[${index}] does not exist`);
      seg.audio[index].src = filePath;
    } else if (layer === 'music') {
      if (!seg.music[index]) throw httpError(400, `music[${index}] does not exist`);
      seg.music[index].src = filePath;
    } else {
      throw httpError(400, `Unknown layer: ${layer}`);
    }

    this.save();
    return project;
  }

  updateSegment(segId: string, updates: Record<string, any>): BeeProject {
    const project = this.get();
    const seg = this.findSegment(project, segId);

    // visual_updates: [{index, color?, kenBurns?, trim?, src?}]
    if (Array.isArray(updates.visual_updates)) {
      for (const u of updates.visual_updates as Array<Record<string, any>>) {
        const { index, ...rest } = u;
        if (typeof index === 'number' && seg.visual[index]) {
          Object.assign(seg.visual[index], rest);
        }
      }
    }

    // audio_updates: [{index, volume?}]
    if (Array.isArray(updates.audio_updates)) {
      for (const u of updates.audio_updates as Array<Record<string, any>>) {
        const { index, ...rest } = u;
        if (typeof index === 'number' && seg.audio[index]) {
          Object.assign(seg.audio[index], rest);
        }
      }
    }

    // transition_in: {type, duration} | null
    if ('transition_in' in updates) {
      const t = updates.transition_in;
      seg.transition = t
        ? { type: String(t.type), duration: Number(t.duration) }
        : null;
    }

    this.save();
    return project;
  }

  reorderSegments(order: string[]): void {
    const project = this.get();
    const segMap = new Map<string, BeeSegment>(project.segments.map(s => [s.id, s]));
    const reordered: BeeSegment[] = [];
    for (const id of order) {
      const seg = segMap.get(id);
      if (seg) reordered.push(seg);
    }
    // Append any segments not mentioned in the order array
    for (const seg of project.segments) {
      if (!order.includes(seg.id)) reordered.push(seg);
    }
    // Recalculate start times
    let cumulativeStart = 0;
    for (const seg of reordered) {
      seg.start = cumulativeStart;
      cumulativeStart += seg.duration;
    }
    project.segments = reordered;
    this.save();
  }

  updateProduction(updates: Partial<ProductionState>): void {
    const project = this.get();
    Object.assign(project.production, updates);
    this.save();
  }

  // ---------- Session restore ----------

  tryRestoreSession(): boolean {
    const lastSessionPath = path.join(os.homedir(), '.bee-video', 'last-session.json');
    if (!fs.existsSync(lastSessionPath)) return false;
    try {
      const session = JSON.parse(fs.readFileSync(lastSessionPath, 'utf-8')) as {
        project_dir?: string;
      };
      if (!session.project_dir) return false;
      const jsonPath = path.join(session.project_dir, '.bee-project.json');
      if (!fs.existsSync(jsonPath)) return false;
      this.loadFromJson(jsonPath);
      return true;
    } catch {
      return false;
    }
  }

  // ---------- Private helpers ----------

  private findSegment(project: BeeProject, segId: string): BeeSegment {
    const seg = project.segments.find(s => s.id === segId);
    if (!seg) throw httpError(404, `Segment not found: ${segId}`);
    return seg;
  }

  private writeSessionFiles(): void {
    if (!this.projectDir || !this.jsonPath) return;

    const storyboardPath = this.jsonPath; // closest we have; md path not stored separately
    const sessionData = JSON.stringify(
      { storyboard_path: storyboardPath, project_dir: this.projectDir },
      null,
      2
    );

    // Project-local session file
    const localBeeVideoDir = path.join(this.projectDir, '.bee-video');
    fs.mkdirSync(localBeeVideoDir, { recursive: true });
    fs.writeFileSync(path.join(localBeeVideoDir, 'session.json'), sessionData, 'utf-8');

    // Global last-session file
    const globalBeeVideoDir = path.join(os.homedir(), '.bee-video');
    fs.mkdirSync(globalBeeVideoDir, { recursive: true });
    fs.writeFileSync(path.join(globalBeeVideoDir, 'last-session.json'), sessionData, 'utf-8');
  }
}

// ---------- Singleton ----------

export const store = new ProjectStore();
