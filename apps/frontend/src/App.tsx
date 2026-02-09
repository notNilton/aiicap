import { useState } from 'react';
import GeneratePage from './pages/GeneratePage';
import GalleryPage from './pages/GalleryPage';
import CorrectionPage from './pages/CorrectionPage';
import './App.css';

type Tab = 'generate' | 'gallery' | 'correction';

function App() {
  const [activeTab, setActiveTab] = useState<Tab>('generate');

  return (
    <div className="app">
      <header className="app-header">
        <h1 className="logo">AIICAP</h1>
        <nav className="nav">
          <button
            className={activeTab === 'generate' ? 'active' : ''}
            onClick={() => setActiveTab('generate')}
          >
            🎨 Gerar
          </button>
          <button
            className={activeTab === 'gallery' ? 'active' : ''}
            onClick={() => setActiveTab('gallery')}
          >
            🖼️ Galeria
          </button>
          <button
            className={activeTab === 'correction' ? 'active' : ''}
            onClick={() => setActiveTab('correction')}
          >
            🔧 Correção
          </button>
        </nav>
      </header>

      <main className="app-main">
        {activeTab === 'generate' && <GeneratePage />}
        {activeTab === 'gallery' && <GalleryPage />}
        {activeTab === 'correction' && <CorrectionPage />}
      </main>

      <footer className="app-footer">
        <p>AIICAP - AI Image Correction and Processing</p>
      </footer>
    </div>
  );
}

export default App;
