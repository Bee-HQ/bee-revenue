import { spawn } from 'node:child_process';
import type { ChildProcess } from 'node:child_process';

export interface DownloadTask {
  task_id: string;
  running: boolean;
  output_lines: string[];
  return_code: number | null;
  process?: ChildProcess;
  finished_at?: number;
}

const MAX_OUTPUT_LINES = 200;
const MAX_COMPLETED_TASKS = 20;

const tasks = new Map<string, DownloadTask>();

function pruneCompleted() {
  const completed = [...tasks.values()]
    .filter(t => !t.running && t.finished_at)
    .sort((a, b) => (a.finished_at ?? 0) - (b.finished_at ?? 0));
  while (completed.length > MAX_COMPLETED_TASKS) {
    const oldest = completed.shift()!;
    tasks.delete(oldest.task_id);
  }
}

function appendOutput(task: DownloadTask, data: string) {
  const lines = data.split('\n').filter(l => l.length > 0);
  task.output_lines.push(...lines);
  if (task.output_lines.length > MAX_OUTPUT_LINES) {
    task.output_lines = task.output_lines.slice(-MAX_OUTPUT_LINES);
  }
}

export function runSubprocess(
  taskId: string,
  command: string,
  args: string[],
  cwd: string,
): DownloadTask {
  const task: DownloadTask = {
    task_id: taskId,
    running: true,
    output_lines: [],
    return_code: null,
  };

  tasks.set(taskId, task);

  const proc = spawn(command, args, { cwd, shell: command.endsWith('.sh') });
  task.process = proc;

  proc.stdout?.on('data', (data: Buffer) => appendOutput(task, data.toString()));
  proc.stderr?.on('data', (data: Buffer) => appendOutput(task, data.toString()));

  proc.on('close', (code) => {
    task.running = false;
    task.return_code = code ?? 1;
    task.finished_at = Date.now();
    delete task.process;
    pruneCompleted();
  });

  proc.on('error', (err) => {
    task.running = false;
    task.return_code = 1;
    task.output_lines.push(`Error: ${err.message}`);
    task.finished_at = Date.now();
    delete task.process;
  });

  return task;
}

export function getAllTasks(): Array<Omit<DownloadTask, 'process' | 'finished_at'>> {
  return [...tasks.values()].map(({ task_id, running, output_lines, return_code }) => ({
    task_id,
    running,
    output_lines: output_lines.slice(-20),
    return_code,
  }));
}

export function resetTasks() {
  tasks.clear();
}
