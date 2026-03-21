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
  const [showCaptions, setShowCaptions] = useState(true);
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
          controls={false}
          autoPlay={false}
          playbackRate={playbackRate}
          acknowledgeRemotionLicense
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
              const frame = getCurrentFrame();
              playerRef.current?.pause();
              playerRef.current?.seekTo(Math.max(0, frame - 1));
            }}
            title="Step back 1 frame"
          >
            &#9664;
          </button>
          <button
            className="text-sm text-white hover:text-blue-400 px-1.5"
            onClick={togglePlay}
            title={playing ? 'Pause (Space)' : 'Play (Space)'}
          >
            {playing ? '||' : '\u25B6'}
          </button>
          <button
            className="text-xs text-gray-400 hover:text-white px-1"
            onClick={() => {
              const frame = getCurrentFrame();
              playerRef.current?.pause();
              playerRef.current?.seekTo(Math.min(totalFrames - 1, frame + 1));
            }}
            title="Step forward 1 frame"
          >
            &#9654;
          </button>
          <button
            className="text-xs text-gray-400 hover:text-white px-1"
            onClick={() => playerRef.current?.seekTo(totalFrames - 1)}
            title="Go to end"
          >
            {'>|'}
          </button>
        </div>

        {/* Loop controls */}
        <div className="flex items-center gap-0.5 border-l border-editor-border pl-2 ml-1">
          <button
            onClick={() => setLoopIn(getCurrentFrame())}
            title="Set loop in (I)"
            className={`text-[9px] px-1 py-0.5 rounded ${loopIn !== null ? 'text-yellow-400' : 'text-gray-500 hover:text-yellow-400'}`}
          >
            {loopIn !== null ? `I:${formatTimecode(framesToTime(loopIn, FPS))}` : '['}
          </button>
          <button
            onClick={() => setLoopOut(getCurrentFrame())}
            title="Set loop out (O)"
            className={`text-[9px] px-1 py-0.5 rounded ${loopOut !== null ? 'text-yellow-400' : 'text-gray-500 hover:text-yellow-400'}`}
          >
            {loopOut !== null ? `O:${formatTimecode(framesToTime(loopOut, FPS))}` : ']'}
          </button>
          {(loopIn !== null || loopOut !== null) && (
            <button
              onClick={() => { setLoopIn(null); setLoopOut(null); }}
              title="Clear loop"
              className="text-[9px] text-gray-600 hover:text-gray-400 px-0.5"
            >
              ×
            </button>
          )}
        </div>

        {/* Timecode */}
        <span className="text-[10px] font-mono text-gray-400">
          {formatTimecode(currentTime)}
          <span className="text-gray-600 mx-1">/</span>
          {formatTimecode(totalDuration)}
        </span>

        {/* Seek bar with hover tooltip */}
        <div
          className="flex-1 h-1.5 bg-editor-border rounded cursor-pointer mx-2 relative"
          onMouseMove={(e) => {
            const rect = e.currentTarget.getBoundingClientRect();
            const pct = (e.clientX - rect.left) / rect.width;
            setHoverTime(pct * totalDuration);
          }}
          onMouseLeave={() => setHoverTime(null)}
          onClick={(e) => {
            const rect = e.currentTarget.getBoundingClientRect();
            const pct = (e.clientX - rect.left) / rect.width;
            const frame = Math.round(pct * totalFrames);
            playerRef.current?.seekTo(Math.max(0, Math.min(totalFrames - 1, frame)));
          }}
        >
          {/* Loop range indicator */}
          {loopIn !== null && loopOut !== null && totalFrames > 1 && (
            <div
              className="absolute h-full bg-yellow-500/20 rounded"
              style={{
                left: `${(loopIn / totalFrames) * 100}%`,
                width: `${((loopOut - loopIn) / totalFrames) * 100}%`,
              }}
            />
          )}
          <div
            className="h-full bg-blue-500 rounded relative z-10"
            style={{ width: `${totalDuration > 0 ? (currentTime / totalDuration) * 100 : 0}%` }}
          />
          {/* Hover tooltip */}
          {hoverTime !== null && (
            <div
              className="absolute -top-6 bg-editor-surface border border-editor-border rounded px-1.5 py-0.5 text-[9px] text-gray-300 font-mono pointer-events-none z-20"
              style={{ left: `${(hoverTime / totalDuration) * 100}%`, transform: 'translateX(-50%)' }}
            >
              {formatTimecode(hoverTime)}
            </div>
          )}
        </div>

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
