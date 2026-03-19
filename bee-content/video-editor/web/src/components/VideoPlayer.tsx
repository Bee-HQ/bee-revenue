import { useRef, useState, useEffect, useCallback } from 'react';
import { useProjectStore } from '../stores/project';
import { api } from '../api/client';

function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, '0')}`;
}

export function VideoPlayer() {
  const selectedSegmentIds = useProjectStore(s => s.selectedSegmentIds);
  const storyboard = useProjectStore(s => s.storyboard);

  const segment = storyboard?.segments.find(s => s.id === selectedSegmentIds[0]);

  // Find media assigned to this segment — prefer visual:0 for the primary video track
  const assignedEntries = segment ? Object.entries(segment.assigned_media) : [];
  const visual0Path = segment?.assigned_media['visual:0'] ?? null;
  const videoEntry = (() => {
    // First: check visual:0 explicitly
    if (visual0Path) {
      const ext = visual0Path.split('.').pop()?.toLowerCase() || '';
      if (['mp4', 'mkv', 'webm', 'mov', 'avi'].includes(ext)) return ['visual:0', visual0Path] as [string, string];
    }
    // Fallback: any assigned path that looks like a video
    return assignedEntries.find(([, path]) => {
      const ext = path.split('.').pop()?.toLowerCase() || '';
      return ['mp4', 'mkv', 'webm', 'mov', 'avi'].includes(ext);
    }) ?? null;
  })();
  const audioEntry = assignedEntries.find(([key, path]) => {
    const ext = path.split('.').pop()?.toLowerCase() || '';
    return ['mp3', 'wav', 'm4a', 'aac', 'ogg'].includes(ext) || key.startsWith('audio');
  });
  const imageEntry = (() => {
    // If visual:0 is an image, use it
    if (visual0Path && !videoEntry) {
      const ext = visual0Path.split('.').pop()?.toLowerCase() || '';
      if (['png', 'jpg', 'jpeg', 'webp', 'gif', 'bmp'].includes(ext)) return ['visual:0', visual0Path] as [string, string];
    }
    return assignedEntries.find(([, path]) => {
      const ext = path.split('.').pop()?.toLowerCase() || '';
      return ['png', 'jpg', 'jpeg', 'webp', 'gif', 'bmp'].includes(ext);
    }) ?? null;
  })();

  const videoRef = useRef<HTMLVideoElement>(null);
  const audioRef = useRef<HTMLAudioElement>(null);
  const [playing, setPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(0.8);
  const [muted, setMuted] = useState(false);

  // Also support previewing a media file directly (from store)
  const previewMedia = useProjectStore(s => s.previewMedia);

  // Determine what to show
  let videoSrc: string | null = null;
  let audioSrc: string | null = null;
  let imageSrc: string | null = null;

  if (previewMedia) {
    const ext = previewMedia.extension.toLowerCase();
    const url = api.mediaFileUrl(previewMedia.path);
    if (['.mp4', '.mkv', '.webm', '.mov', '.avi'].includes(ext)) videoSrc = url;
    else if (['.mp3', '.wav', '.m4a', '.aac', '.ogg'].includes(ext)) audioSrc = url;
    else if (['.png', '.jpg', '.jpeg', '.webp', '.gif', '.bmp'].includes(ext)) imageSrc = url;
  } else if (segment) {
    if (videoEntry) videoSrc = api.mediaFileUrl(videoEntry[1]);
    if (audioEntry) audioSrc = api.mediaFileUrl(audioEntry[1]);
    if (imageEntry && !videoEntry) imageSrc = api.mediaFileUrl(imageEntry[1]);
  }

  const hasMedia = videoSrc || audioSrc || imageSrc;

  // Reset when source changes
  useEffect(() => {
    setPlaying(false);
    setCurrentTime(0);
    setDuration(0);
  }, [videoSrc, audioSrc, imageSrc]);

  // Sync volume to elements
  useEffect(() => {
    const el = videoRef.current || audioRef.current;
    if (el) {
      el.volume = volume;
      el.muted = muted;
    }
  }, [volume, muted, videoSrc, audioSrc]);

  const togglePlay = useCallback(() => {
    const el = videoRef.current || audioRef.current;
    if (!el) return;
    if (playing) {
      el.pause();
    } else {
      el.play();
    }
    setPlaying(!playing);
  }, [playing]);

  const handleTimeUpdate = () => {
    const el = videoRef.current || audioRef.current;
    if (el) setCurrentTime(el.currentTime);
  };

  const handleLoadedMetadata = () => {
    const el = videoRef.current || audioRef.current;
    if (el) setDuration(el.duration);
  };

  const handleEnded = () => {
    setPlaying(false);
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const t = parseFloat(e.target.value);
    const el = videoRef.current || audioRef.current;
    if (el) el.currentTime = t;
    setCurrentTime(t);
  };

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const v = parseFloat(e.target.value);
    setVolume(v);
    const el = videoRef.current || audioRef.current;
    if (el) el.volume = v;
  };

  const toggleMute = () => {
    const el = videoRef.current || audioRef.current;
    if (el) el.muted = !muted;
    setMuted(!muted);
  };

  const skipBack = () => {
    const el = videoRef.current || audioRef.current;
    if (el) { el.currentTime = Math.max(0, el.currentTime - 5); setCurrentTime(el.currentTime); }
  };

  const skipForward = () => {
    const el = videoRef.current || audioRef.current;
    if (el) { el.currentTime = Math.min(el.duration || 0, el.currentTime + 5); setCurrentTime(el.currentTime); }
  };

  // Keyboard shortcuts
  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;
      if (e.code === 'Space') { e.preventDefault(); togglePlay(); }
      if (e.code === 'ArrowLeft') { e.preventDefault(); skipBack(); }
      if (e.code === 'ArrowRight') { e.preventDefault(); skipForward(); }
      if (e.code === 'KeyM') { e.preventDefault(); toggleMute(); }
    };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [togglePlay]);

  const progress = duration > 0 ? (currentTime / duration) * 100 : 0;

  return (
    <div className="bg-black flex flex-col">
      {/* Viewport */}
      <div className="relative w-full flex items-center justify-center bg-black"
           style={{ height: '320px' }}>
        {videoSrc && (
          <video
            ref={videoRef}
            src={videoSrc}
            className="max-w-full max-h-full object-contain"
            onTimeUpdate={handleTimeUpdate}
            onLoadedMetadata={handleLoadedMetadata}
            onEnded={handleEnded}
            onClick={togglePlay}
          />
        )}
        {imageSrc && !videoSrc && (
          <img src={imageSrc} alt="" className="max-w-full max-h-full object-contain" />
        )}
        {audioSrc && !videoSrc && !imageSrc && (
          <div className="flex flex-col items-center gap-3">
            <div className="text-4xl">🔊</div>
            <div className="text-xs text-gray-400">
              {audioEntry ? audioEntry[1].split('/').pop() : previewMedia?.name}
            </div>
          </div>
        )}
        {!hasMedia && !segment && !previewMedia && (
          <div className="text-center px-4">
            <div className="text-3xl mb-2 opacity-30">🎬</div>
            <div className="text-xs text-gray-600">Select a segment with media to preview</div>
          </div>
        )}
        {!hasMedia && segment && (
          <div className="text-center px-4">
            <div className="text-sm text-gray-500 mb-1">{segment.title}</div>
            <div className="text-xs text-gray-600">
              Select a segment with media to preview
            </div>
          </div>
        )}

        {/* Hidden audio element for audio-only playback */}
        {audioSrc && (
          <audio
            ref={!videoSrc ? audioRef : undefined}
            src={audioSrc}
            onTimeUpdate={!videoSrc ? handleTimeUpdate : undefined}
            onLoadedMetadata={!videoSrc ? handleLoadedMetadata : undefined}
            onEnded={!videoSrc ? handleEnded : undefined}
          />
        )}

        {/* Play overlay on pause */}
        {hasMedia && (videoSrc || audioSrc) && !playing && (
          <button
            onClick={togglePlay}
            className="absolute inset-0 flex items-center justify-center bg-black/30
                       hover:bg-black/40 transition-colors cursor-pointer"
          >
            <div className="w-14 h-14 rounded-full bg-white/20 backdrop-blur-sm
                            flex items-center justify-center">
              <span className="text-white text-xl ml-1">▶</span>
            </div>
          </button>
        )}
      </div>

      {/* Now-playing filename bar */}
      {hasMedia && (
        <div className="bg-editor-surface border-t border-editor-border px-3 py-1 flex items-center gap-2">
          <span className="text-[10px] text-gray-500 truncate">
            {previewMedia
              ? previewMedia.name
              : videoEntry
                ? videoEntry[1].split('/').pop()
                : audioEntry
                  ? audioEntry[1].split('/').pop()
                  : imageEntry
                    ? imageEntry[1].split('/').pop()
                    : ''}
          </span>
        </div>
      )}

      {/* Transport controls */}
      {hasMedia && (videoSrc || audioSrc) && (
        <div className="bg-editor-surface border-t border-editor-border px-3 py-1.5">
          {/* Seek bar */}
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[10px] text-gray-500 font-mono w-10 text-right">
              {formatTime(currentTime)}
            </span>
            <div className="flex-1 relative h-1 group">
              <div className="absolute inset-0 bg-editor-border rounded-full" />
              <div
                className="absolute inset-y-0 left-0 bg-editor-accent rounded-full"
                style={{ width: `${progress}%` }}
              />
              <input
                type="range"
                min={0}
                max={duration || 0}
                step={0.1}
                value={currentTime}
                onChange={handleSeek}
                className="absolute inset-0 w-full opacity-0 cursor-pointer"
              />
            </div>
            <span className="text-[10px] text-gray-500 font-mono w-10">
              {formatTime(duration)}
            </span>
          </div>

          {/* Buttons */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1">
              <button onClick={skipBack} className="p-1 text-gray-400 hover:text-white text-xs" title="Back 5s">
                ⏪
              </button>
              <button onClick={togglePlay} className="p-1 text-gray-300 hover:text-white text-sm" title={playing ? 'Pause' : 'Play'}>
                {playing ? '⏸' : '▶️'}
              </button>
              <button onClick={skipForward} className="p-1 text-gray-400 hover:text-white text-xs" title="Forward 5s">
                ⏩
              </button>
            </div>
            <div className="flex items-center gap-1.5">
              <button onClick={toggleMute} className="text-gray-400 hover:text-white text-xs" title="Mute">
                {muted ? '🔇' : '🔊'}
              </button>
              <input
                type="range"
                min={0}
                max={1}
                step={0.05}
                value={muted ? 0 : volume}
                onChange={handleVolumeChange}
                className="w-16 h-1 accent-editor-accent cursor-pointer"
              />
            </div>
            {segment && (
              <div className="text-[10px] text-gray-600">
                {segment.start} - {segment.end}
              </div>
            )}
          </div>
        </div>
      )}

    </div>
  );
}
