import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import type { OverlayProps } from '../overlays';

interface ChatMessage {
  from: string;
  text: string;
}

export function parseMessages(content: string): ChatMessage[] {
  try {
    const parsed = JSON.parse(content);
    if (Array.isArray(parsed) && parsed.every(m => m.from && m.text)) return parsed;
  } catch {}
  return [{ from: 'Unknown', text: content }];
}

// Platform color schemes
const PLATFORMS = {
  imessage: {
    incoming: { bg: '#e5e5ea', text: '#000', radius: 18 },
    outgoing: { bg: '#007aff', text: '#fff', radius: 18 },
    visualBg: '#1c1c1e',
    overlayBg: 'rgba(28,28,30,0.9)',
    senderColor: '#8e8e93',
    font: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
  },
  android: {
    incoming: { bg: '#ffffff', text: '#000', radius: 8 },
    outgoing: { bg: '#dcf8c6', text: '#000', radius: 8 },
    visualBg: '#e5ddd5',
    overlayBg: 'rgba(229,221,213,0.9)',
    senderColor: '#666',
    font: 'Roboto, "Segoe UI", sans-serif',
  },
  generic: {
    incoming: { bg: '#2a2a2e', text: '#fff', radius: 12 },
    outgoing: { bg: '#0d9488', text: '#fff', radius: 12 },
    visualBg: '#111',
    overlayBg: 'rgba(17,17,17,0.9)',
    senderColor: '#888',
    font: 'sans-serif',
  },
} as const;

type PlatformKey = keyof typeof PLATFORMS;
type AnimationMode = 'typing' | 'instant' | 'scroll';

// Typing indicator (3 bouncing dots)
function TypingDots({ color, frame }: { color: string; frame: number }) {
  return (
    <div style={{ display: 'flex', gap: 4, padding: '8px 14px' }}>
      {[0, 1, 2].map(i => {
        const bounce = Math.sin((frame + i * 4) * 0.3) * 3;
        return (
          <div key={i} style={{
            width: 8, height: 8, borderRadius: '50%',
            backgroundColor: color,
            opacity: 0.5,
            transform: `translateY(${bounce}px)`,
          }} />
        );
      })}
    </div>
  );
}

function MessageBubble({
  msg, isOutgoing, platform, showSender,
}: {
  msg: ChatMessage; isOutgoing: boolean; platform: PlatformKey; showSender: boolean;
}) {
  const scheme = PLATFORMS[platform];
  const style = isOutgoing ? scheme.outgoing : scheme.incoming;

  return (
    <div style={{
      display: 'flex', flexDirection: 'column',
      alignItems: isOutgoing ? 'flex-end' : 'flex-start',
      width: '100%',
    }}>
      {showSender && (
        <span style={{ fontSize: 12, color: scheme.senderColor, marginBottom: 2, fontFamily: scheme.font }}>
          {msg.from}
        </span>
      )}
      <div style={{
        background: style.bg, color: style.text,
        padding: '10px 16px', borderRadius: style.radius,
        maxWidth: '70%', fontSize: 16, lineHeight: 1.4,
        fontFamily: scheme.font,
        boxShadow: platform === 'android' ? '0 1px 2px rgba(0,0,0,0.1)' : 'none',
      }}>
        {msg.text}
      </div>
    </div>
  );
}

export const TextChat: React.FC<TextChatProps> = ({
  content, metadata, durationInFrames, mode = 'overlay',
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const messages = parseMessages(content);
  const platform = ((metadata?.platform as PlatformKey) || 'imessage') as PlatformKey;
  const animation = ((metadata?.animation as AnimationMode) || 'typing') as AnimationMode;
  const scheme = PLATFORMS[platform] || PLATFORMS.imessage;

  // Determine first sender = incoming
  const firstSender = messages[0]?.from;

  const bg = mode === 'visual' ? scheme.visualBg : scheme.overlayBg;

  // Exit fade
  const exitOpacity = interpolate(frame, [durationInFrames - 15, durationInFrames], [1, 0], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });

  if (animation === 'scroll') {
    // All messages visible, scroll down
    const totalHeight = messages.length * 60; // estimate
    const scrollY = interpolate(frame, [0, durationInFrames - 15], [0, -Math.max(0, totalHeight - 300)], {
      extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
    });

    return (
      <AbsoluteFill style={{ justifyContent: mode === 'overlay' ? 'flex-end' : 'center', alignItems: 'center', opacity: exitOpacity }}>
        <div style={{
          background: bg, borderRadius: mode === 'overlay' ? 16 : 0,
          padding: mode === 'overlay' ? '20px 24px' : '40px 60px',
          width: mode === 'overlay' ? '60%' : '100%',
          height: mode === 'overlay' ? undefined : '100%',
          maxHeight: mode === 'overlay' ? '60%' : undefined,
          overflow: 'hidden',
          display: 'flex', flexDirection: 'column',
        }}>
          <div style={{ transform: `translateY(${scrollY}px)`, display: 'flex', flexDirection: 'column', gap: 12 }}>
            {messages.map((msg, i) => (
              <MessageBubble
                key={i} msg={msg}
                isOutgoing={msg.from !== firstSender}
                platform={platform}
                showSender={i === 0 || messages[i - 1].from !== msg.from}
              />
            ))}
          </div>
        </div>
      </AbsoluteFill>
    );
  }

  // Typing and instant modes: messages appear one at a time
  // Typing: ~40 frames per message (typing indicator takes time)
  // Instant: ~20 frames per message (faster pacing, no indicator)
  const availableFrames = durationInFrames - 15; // reserve 15 for exit
  const framesPerMsg = animation === 'typing'
    ? Math.floor(availableFrames / messages.length)
    : Math.max(8, Math.floor(availableFrames / (messages.length * 2)));

  const typingFrames = animation === 'typing' ? Math.min(15, Math.floor(framesPerMsg * 0.35)) : 0;

  return (
    <AbsoluteFill style={{
      justifyContent: mode === 'overlay' ? 'flex-end' : 'center',
      alignItems: 'center',
      opacity: exitOpacity,
      padding: mode === 'overlay' ? '0 0 80px' : 0,
    }}>
      <div style={{
        background: bg, borderRadius: mode === 'overlay' ? 16 : 0,
        padding: mode === 'overlay' ? '20px 24px' : '60px 80px',
        width: mode === 'overlay' ? '55%' : '100%',
        height: mode === 'visual' ? '100%' : undefined,
        display: 'flex', flexDirection: 'column', gap: 12,
        justifyContent: mode === 'visual' ? 'center' : undefined,
      }}>
        {messages.map((msg, i) => {
          const msgStart = i * framesPerMsg;
          const isOutgoing = msg.from !== firstSender;
          const showSender = i === 0 || messages[i - 1].from !== msg.from;

          // Is this message visible yet?
          if (frame < msgStart) return null;

          // Show typing indicator
          if (animation === 'typing' && frame < msgStart + typingFrames) {
            return (
              <div key={i} style={{ alignSelf: isOutgoing ? 'flex-end' : 'flex-start' }}>
                <TypingDots color={scheme.senderColor} frame={frame} />
              </div>
            );
          }

          // Message appearance animation
          const appearFrame = msgStart + typingFrames;
          const slideUp = spring({
            frame: frame - appearFrame,
            fps,
            config: { stiffness: 300, damping: 25 },
          });

          const opacity = animation === 'instant'
            ? interpolate(frame, [msgStart, msgStart + 8], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' })
            : slideUp;

          const translateY = animation === 'instant'
            ? interpolate(frame, [msgStart, msgStart + 8], [10, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' })
            : interpolate(slideUp, [0, 1], [20, 0]);

          return (
            <div key={i} style={{ opacity, transform: `translateY(${translateY}px)` }}>
              <MessageBubble
                msg={msg} isOutgoing={isOutgoing}
                platform={platform} showSender={showSender}
              />
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

// Interface for direct use
export interface TextChatProps {
  content: string;
  metadata?: Record<string, any> | null;
  durationInFrames: number;
  mode?: 'visual' | 'overlay';
}

// Overlay wrapper (receives OverlayProps, passes mode='overlay')
export const TextChatOverlay: React.FC<OverlayProps> = (props) => (
  <TextChat {...props} mode="overlay" />
);
