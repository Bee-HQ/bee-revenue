import { useProjectStore } from '../stores/project';

export function AssetStatusBanner() {
  const assetStatus = useProjectStore(s => s.assetStatus);
  if (!assetStatus) return null;

  const { total, found, needsDownload, needsGeneration, needsFile, missing } = assetStatus;
  const notReady = total - found;

  if (notReady === 0) {
    return (
      <div className="bg-green-900/30 border-b border-green-800 px-4 py-1.5 text-xs text-green-300 flex items-center gap-2">
        <span>All {total} segments have media assigned</span>
      </div>
    );
  }

  return (
    <div className="bg-yellow-900/20 border-b border-yellow-800/30 px-4 py-1.5 text-xs flex items-center gap-4">
      <span className="text-yellow-400 font-medium">{found}/{total} segments ready</span>
      {needsDownload > 0 && (
        <span className="text-blue-400">{needsDownload} need stock footage</span>
      )}
      {needsGeneration > 0 && (
        <span className="text-pink-400">{needsGeneration} need generation</span>
      )}
      {needsFile > 0 && (
        <span className="text-red-400">{needsFile} missing files</span>
      )}
      {missing > 0 && (
        <span className="text-gray-500">{missing} no visual defined</span>
      )}
    </div>
  );
}
