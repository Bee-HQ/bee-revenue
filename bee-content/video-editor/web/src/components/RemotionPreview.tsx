import { useCallback, useRef, useState, useEffect, useMemo } from 'react';
import { Player } from '@remotion/player';
import type { PlayerRef } from '@remotion/player';
import { useProjectStore } from '../stores/project';
import { BeeComposition } from './BeeComposition';
import { formatTimecode, framesToTime, timeToFrames } from '../adapters/time-utils';

const FPS = 30;

export function RemotionPreview() {
  const storyboard = useProjectStore((s) => s.storyboard);
  const mediaFiles = useProjectStore((s) => s.mediaFiles);
  const currentTimeMs = useProjectStore((s) => s.currentTimeMs);
  const setPlayerRef = useProjectStore((s) => s.setPlayerRef);

  // Build list of known media file paths for the composition
  const mediaFilePaths = useMemo(
    () => mediaFiles.map((f) => f.relative_path || f.path),
    [mediaFiles],
  );
  const loopIn = useProjectStore((s) => s.loopIn);
  const loopOut = useProjectStore((s) => s.loopOut);
  const setLoopIn = useProjectStore((s) => s.setLoopIn);
  const setLoopOut = useProjectStore((s) => s.setLoopOut);
  const playerRef = useRef<PlayerRef>(null);
  const playingRef = useRef(false);
  const loopInRef = useRef<number | null>(null);
  const loopOutRef = useRef<number | null>(null);
  const [currentTime, setCurrentTime] = useState(0);
  const [showCaptions, setShowCaptions] = useState(false);
  const [playing, setPlaying] = useState(false);
  const [playbackRate, setPlaybackRate] = useState(1);
  const [hoverTime, setHoverTime] = useState<number | null>(null);

  // Keep refs in sync with store state for use in event handlers
  useEffect(() => { loopInRef.current = loopIn; }, [loopIn]);
  useEffect(() => { loopOutRef.current = loopOut; }, [loopOut]);

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

    // Guard: addEventListener may not be available in all Remotion/React versions
    if (typeof player.addEventListener !== 'function') {
      console.warn('[RemotionPreview] player.addEventListener not available, falling back to polling');
      const interval = setInterval(() => {
        try {
          const frame = player.getCurrentFrame() ?? 0;
          setCurrentTime(framesToTime(frame, FPS));
          if (playingRef.current) {
            useProjectStore.getState().setCurrentTimeMs(frame * (1000 / FPS));
            const li = loopInRef.current;
            const lo = loopOutRef.current;
            if (li !== null && lo !== null && frame >= lo) {
              playerRef.current?.seekTo(li);
            }
          }
        } catch {}
      }, 100);
      return () => clearInterval(interval);
    }

    try {
      const onFrameChange = (e: { detail: { frame: number } }) => {
        const frame = e?.detail?.frame ?? 0;
        const seconds = framesToTime(frame, FPS);
        setCurrentTime(seconds);
        // Only update the store while playing — avoids a seek->framechange->setCurrentTimeMs->seekTo loop
        // Use ref to avoid stale closure and prevent re-registering listeners on every play/pause
        if (playingRef.current) {
          useProjectStore.getState().setCurrentTimeMs(frame * (1000 / FPS));

          // Loop range enforcement: seek back to loopIn when playback reaches loopOut
          const li = loopInRef.current;
          const lo = loopOutRef.current;
          if (li !== null && lo !== null && frame >= lo) {
            playerRef.current?.seekTo(li);
          }
        }
      };
      const onPlay = () => { playingRef.current = true; setPlaying(true); };
      const onPause = () => { playingRef.current = false; setPlaying(false); };

      player.addEventListener('framechange' as any, onFrameChange as never);
      player.addEventListener('play', onPlay as never);
      player.addEventListener('pause', onPause as never);

      return () => {
        try {
          player.removeEventListener('framechange' as any, onFrameChange as never);
          player.removeEventListener('play', onPlay as never);
          player.removeEventListener('pause', onPause as never);
        } catch {}
      };
    } catch (err) {
      console.error('[RemotionPreview] event listener setup failed:', err);
    }
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

  const getCurrentFrame = () => playerRef.current?.getCurrentFrame() ?? 0;

  if (!storyboard) return null;

  return (
    <div className="flex-1 flex flex-col bg-black min-h-0">
      {/* Player area */}
      <div className="flex-1 flex items-center justify-center overflow-hidden">
        <Player
          ref={playerRef}
          component={BeeComposition}
          inputProps={{ storyboard, mediaFiles: mediaFilePaths, showCaptions }}
          durationInFrames={totalFrames}
          fps={FPS}
          compositionWidth={1920}
          compositionHeight={1080}
          style={{ width: '100%', height: '100%' }}
          controls
          autoPlay={false}
          playbackRate={playbackRate}
          acknowledgeRemotionLicense
        />
      </div>

      {/* Minimal controls bar — speed + captions (transport handled by Remotion's built-in controls) */}
      <div className="bg-editor-surface border-t border-editor-border px-4 py-1 flex items-center justify-end gap-2 shrink-0">
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
        <button
          onClick={() => setShowCaptions(!showCaptions)}
          className={`text-[10px] px-1.5 py-0.5 rounded border ${
            showCaptions
              ? 'text-yellow-400 border-yellow-600/50 bg-yellow-600/10'
              : 'text-gray-500 border-editor-border'
          }`}
          title={showCaptions ? 'Hide captions' : 'Show captions'}
        >
          CC
        </button>
      </div>
    </div>
  );
}
