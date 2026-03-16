import { useProjectStore } from '../stores/project';
import { SegmentCard } from './SegmentCard';

export function StoryboardTimeline() {
  const storyboard = useProjectStore(s => s.storyboard);
  if (!storyboard) return null;

  // Group segments by section
  const sectionGroups: { section: string; segments: typeof storyboard.segments }[] = [];
  let currentSection = '';

  for (const seg of storyboard.segments) {
    if (seg.section !== currentSection) {
      currentSection = seg.section;
      sectionGroups.push({ section: currentSection, segments: [] });
    }
    sectionGroups[sectionGroups.length - 1].segments.push(seg);
  }

  return (
    <div className="p-4 space-y-6">
      {sectionGroups.map(group => (
        <section key={group.section}>
          <div className="sticky top-0 z-10 bg-editor-bg/90 backdrop-blur-sm pb-2 mb-3">
            <h2 className="text-sm font-bold text-gray-300 uppercase tracking-wide">
              {group.section}
            </h2>
            <span className="text-xs text-gray-600">
              {group.segments.length} segments
            </span>
          </div>

          <div className="space-y-2">
            {group.segments.map(seg => (
              <SegmentCard key={seg.id} segment={seg} />
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}
