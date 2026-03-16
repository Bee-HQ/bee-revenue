import { useProjectStore } from './stores/project';
import { Layout } from './components/Layout';
import { LoadProject } from './components/LoadProject';

export default function App() {
  const storyboard = useProjectStore(s => s.storyboard);

  if (!storyboard) {
    return <LoadProject />;
  }

  return <Layout />;
}
