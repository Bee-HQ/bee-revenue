import { useCallback, useRef, useState, useEffect } from 'react';
import { Player } from '@remotion/player';
import type { PlayerRef } from '@remotion/player';
import { useProjectStore } from '../stores/project';
import { BeeComposition } from './BeeComposition';
import { formatTimecode, framesToTime, timeToFrames } from '../adapters/time-utils';

const FPS = 30;

export function RemotionPreview() {
  const storyboard = useProjectStore((s) => s.storyboard);
  const currentTimeMs = useProjectStore((s) => s.currentTimeMs);
  const setPlayerRef = useProjectStore((s) => s.setPlayerRef);
  const playerRef = useRef<PlayerRef>(null);
  const playingRef = useRef(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [playbackRate, setPlaybackRate] = useState(1);

  const SPEEDS = [0.5, 1, 1.5, 2];

  const totalDuration = storyboard?.total_duration_seconds ?? 0;
  const totalFrames = Math.max(1, Math.round(totalDuration * FPS));

  // Register playerRef in the store on mount so other components can seek
  useEffect(() => {
    setPlayerRef(playerRef);
  }, [setPlayerRef]);

  // Listen to player frame updates
  useEffect(() => {
    const player = playerRef.current;
    if (!player) return;

    const onFrameChange = (e: { detail: { frame: number } }) => {
      const seconds = framesToTime(e.detail.frame, FPS);
      setCurrentTime(seconds);
      // Only update the store while playing — avoids a seek→framechange→setCurrentTimeMs→seekTo loop
      // Use ref to avoid stale closure and prevent re-registering listeners on every play/pause
      if (playingRef.current) {
        useProjectStore.getState().setCurrentTimeMs(e.detail.frame * (1000 / FPS));
      }
    };
    const onPlay = () => { playingRef.current = true; setPlaying(true); };
    const onPause = () => { playingRef.current = false; setPlaying(false); };

    player.addEventListener('framechange', onFrameChange as never);
    player.addEventListener('play', onPlay);
    player.addEventListener('pause', onPause);

    return () => {
      player.removeEventListener('framechange', onFrameChange as never);
      player.removeEventListener('play', onPlay);
      player.removeEventListener('pause', onPause);
    };
  }, [storyboard]);

  // When currentTimeMs changes externally (e.g. from segment click), seek the player
  useEffect(() => {
    if (playerRef.current && !playingRef.current) {
      const frame = timeToFrames(currentTimeMs / 1000, FPS);
      playerRef.current.seekTo(frame);
    }
  }, [currentTimeMs]);

  const togglePlay = useCallback(() => {
    if (playing) playerRef.current?.pause();
    else playerRef.current?.play();
  }, [playing]);

  if (!storyboard) return null;

  return (
    <div className="flex-1 flex flex-col bg-black min-h-0">
      {/* Player area */}
      <div className="flex-1 flex items-center justify-center overflow-hidden">
        <Player
          ref={playerRef}
          component={BeeComposition}
          inputProps={{ storyboard }}
          durationInFrames={totalFrames}
          fps={FPS}
          compositionWidth={1920}
          compositionHeight={1080}
          style={{ width: '100%', height: '100%' }}
          controls={false}
          autoPlay={false}
          playbackRate={playbackRate}
        />
      </div>

      {/* Playback controls bar */}
      <div className="bg-editor-surface border-t border-editor-border px-4 py-1.5 flex items-center gap-3 shrink-0">
        {/* Transport buttons */}
        <div className="flex items-center gap-1">
          <button
            className="text-xs text-gray-400 hover:text-white px-1"
            onClick={() => playerRef.current?.seekTo(0)}
            title="Go to start"
          >
            {'|<'}
          </button>
          <button
            className="text-xs text-gray-400 hover:text-white px-1"
            onClick={() => {
              const frame = playerRef.current?.getCurrentFrame() ?? 0;
              playerRef.current?.pause();
              playerRef.current?.seekTo(Math.max(0, frame - 1));
            }}
            title="Step back 1 frame"
          >
            ◀
          </button>
          <button
            className="text-sm text-white hover:text-blue-400 px-1.5"
            onClick={togglePlay}
            title={playing ? 'Pause (Space)' : 'Play (Space)'}
          >
            {playing ? '||' : '▶'}
          </button>
          <button
            className="text-xs text-gray-400 hover:text-white px-1"
            onClick={() => {
              const frame = playerRef.current?.getCurrentFrame() ?? 0;
              playerRef.current?.pause();
              playerRef.current?.seekTo(Math.min(totalFrames - 1, frame + 1));
            }}
            title="Step forward 1 frame"
          >
            ▶
          </button>
          <button
            className="text-xs text-gray-400 hover:text-white px-1"
            onClick={() => playerRef.current?.seekTo(totalFrames - 1)}
            title="Go to end"
          >
            {'>|'}
          </button>
        </div>

        {/* Timecode */}
        <span className="text-[10px] font-mono text-gray-400">
          {formatTimecode(currentTime)}
          <span className="text-gray-600 mx-1">/</span>
          {formatTimecode(totalDuration)}
        </span>

        <div className="flex-1" />

        {/* Speed selector */}
        <button
          onClick={() => {
            const currentIdx = SPEEDS.indexOf(playbackRate);
            const nextIdx = (currentIdx + 1) % SPEEDS.length;
            setPlaybackRate(SPEEDS[nextIdx]);
          }}
          className="text-[10px] text-gray-400 hover:text-white px-1.5 py-0.5 font-mono border border-editor-border rounded hover:border-gray-500"
          title="Playback speed"
        >
          {playbackRate}x
        </button>
      </div>
    </div>
  );
}
