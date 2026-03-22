import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import type { OverlayProps } from './overlays';

interface PostData {
  author: string;
  handle?: string;
  text: string;
  timestamp?: string;
  likes?: string;
  image?: string;
}

export function parsePostData(content: string): PostData {
  try {
    const parsed = JSON.parse(content);
    if (parsed.author && parsed.text) return parsed;
  } catch {}
  // Fallback: treat as plain text post
  return { author: 'Unknown', text: content };
}

type PlatformKey = 'facebook' | 'instagram' | 'twitter';
type AnimationKey = 'slide' | 'reveal' | 'phone';

// --- Platform Styles ---

const PLATFORMS: Record<PlatformKey, {
  bg: string; headerBg: string; textColor: string; secondaryColor: string;
  authorColor: string; font: string; icon: string; brandColor: string;
}> = {
  facebook: {
    bg: '#ffffff', headerBg: '#f0f2f5', textColor: '#050505', secondaryColor: '#65676b',
    authorColor: '#050505', font: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    icon: 'f', brandColor: '#1877f2',
  },
  instagram: {
    bg: '#ffffff', headerBg: '#ffffff', textColor: '#262626', secondaryColor: '#8e8e8e',
    authorColor: '#262626', font: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    icon: '📷', brandColor: '#e1306c',
  },
  twitter: {
    bg: '#15202b', headerBg: '#15202b', textColor: '#e7e9ea', secondaryColor: '#71767b',
    authorColor: '#e7e9ea', font: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    icon: '𝕏', brandColor: '#1d9bf0',
  },
};

// --- Post Card ---

function PostCard({ post, platform }: { post: PostData; platform: PlatformKey }) {
  const style = PLATFORMS[platform];

  return (
    <div style={{
      background: style.bg, borderRadius: 12, overflow: 'hidden',
      boxShadow: '0 4px 20px rgba(0,0,0,0.3)', maxWidth: 500, width: '100%',
      fontFamily: style.font,
    }}>
      {/* Header */}
      <div style={{
        padding: '14px 16px', display: 'flex', alignItems: 'center', gap: 12,
        background: style.headerBg, borderBottom: platform === 'instagram' ? '1px solid #efefef' : 'none',
      }}>
        {/* Avatar */}
        <div style={{
          width: 40, height: 40, borderRadius: '50%',
          background: style.brandColor, display: 'flex', alignItems: 'center', justifyContent: 'center',
          color: '#fff', fontSize: 18, fontWeight: 700,
        }}>
          {post.author[0]?.toUpperCase()}
        </div>
        <div style={{ flex: 1 }}>
          <div style={{ color: style.authorColor, fontSize: 15, fontWeight: 700 }}>
            {post.author}
          </div>
          {post.handle && (
            <div style={{ color: style.secondaryColor, fontSize: 13 }}>
              {post.handle}
            </div>
          )}
          {post.timestamp && !post.handle && (
            <div style={{ color: style.secondaryColor, fontSize: 12 }}>
              {post.timestamp}
            </div>
          )}
        </div>
        {/* Platform icon */}
        <div style={{ color: style.brandColor, fontSize: 20, fontWeight: 700 }}>
          {style.icon}
        </div>
      </div>

      {/* Content */}
      <div style={{ padding: '12px 16px' }}>
        <div style={{ color: style.textColor, fontSize: 15, lineHeight: 1.5 }}>
          {post.text}
        </div>
      </div>

      {/* Footer */}
      <div style={{
        padding: '8px 16px 12px', display: 'flex', gap: 16,
        borderTop: platform !== 'twitter' ? '1px solid #efefef' : 'none',
      }}>
        {post.likes && (
          <span style={{ color: style.secondaryColor, fontSize: 13 }}>
            ❤️ {post.likes}
          </span>
        )}
        {post.timestamp && post.handle && (
          <span style={{ color: style.secondaryColor, fontSize: 13 }}>
            {post.timestamp}
          </span>
        )}
      </div>
    </div>
  );
}

// --- Phone Frame ---

function PhoneFrame({ children }: { children: React.ReactNode }) {
  return (
    <div style={{
      background: '#1a1a1a', borderRadius: 36, padding: '40px 12px 30px',
      boxShadow: '0 8px 40px rgba(0,0,0,0.6)', border: '3px solid #333',
      width: 380, position: 'relative',
    }}>
      {/* Notch */}
      <div style={{
        position: 'absolute', top: 12, left: '50%', transform: 'translateX(-50%)',
        width: 100, height: 6, borderRadius: 3, background: '#333',
      }} />
      {/* Screen */}
      <div style={{
        borderRadius: 24, overflow: 'hidden', background: '#fff',
      }}>
        {children}
      </div>
    </div>
  );
}

// --- Main Component ---

export const SocialPost: React.FC<SocialPostProps> = ({
  content, metadata, durationInFrames, mode = 'overlay',
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const post = parsePostData(content);
  const platform = ((metadata?.platform as PlatformKey) || 'twitter') as PlatformKey;
  const animation = ((metadata?.animation as AnimationKey) || 'slide') as AnimationKey;

  const exitOpacity = interpolate(frame, [durationInFrames - 15, durationInFrames], [1, 0], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });

  const card = <PostCard post={post} platform={platform} />;

  if (animation === 'phone') {
    // Phone frame slides up
    const slideUp = spring({ frame, fps, config: { stiffness: 150, damping: 20 } });
    const translateY = interpolate(slideUp, [0, 1], [120, 0]);

    return (
      <AbsoluteFill style={{
        justifyContent: 'center', alignItems: 'center', opacity: exitOpacity,
        padding: mode === 'overlay' ? '0 0 60px' : 0,
      }}>
        <div style={{ transform: `translateY(${translateY}%)`, opacity: slideUp }}>
          <PhoneFrame>{card}</PhoneFrame>
        </div>
      </AbsoluteFill>
    );
  }

  if (animation === 'reveal') {
    // Blur reveal — starts blurred, sharpens
    const blurAmount = interpolate(frame, [0, 30], [20, 0], {
      extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
    });
    const brightness = interpolate(frame, [0, 25], [0.3, 1], {
      extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
    });
    const scale = interpolate(frame, [0, 30], [1.1, 1], {
      extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
    });

    return (
      <AbsoluteFill style={{
        justifyContent: 'center', alignItems: 'center', opacity: exitOpacity,
        padding: mode === 'overlay' ? '0 0 60px' : 0,
      }}>
        <div style={{
          filter: `blur(${blurAmount}px) brightness(${brightness})`,
          transform: `scale(${scale})`,
        }}>
          {card}
        </div>
      </AbsoluteFill>
    );
  }

  // Default: slide animation
  const slideUp = spring({ frame, fps, config: { stiffness: 200, damping: 22 } });
  const translateY = interpolate(slideUp, [0, 1], [80, 0]);

  return (
    <AbsoluteFill style={{
      justifyContent: mode === 'overlay' ? 'flex-end' : 'center',
      alignItems: 'center', opacity: exitOpacity,
      padding: mode === 'overlay' ? '0 0 80px' : 0,
    }}>
      <div style={{ transform: `translateY(${translateY}px)`, opacity: slideUp }}>
        {card}
      </div>
    </AbsoluteFill>
  );
};

export interface SocialPostProps {
  content: string;
  metadata?: Record<string, any> | null;
  durationInFrames: number;
  mode?: 'visual' | 'overlay';
}

// Overlay wrapper
export const SocialPostOverlay: React.FC<OverlayProps> = (props) => (
  <SocialPost {...props} mode="overlay" />
);
