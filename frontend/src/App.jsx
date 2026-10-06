import { useState } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

function App() {
  const [prompt, setPrompt] = useState('Create a modern fintech landing page for a startup in Lagos.');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch(`${API_BASE_URL}/api/build`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt,
          tone: 'premium',
          style: 'dark',
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to build app');
      }

      setResult(data);
    } catch (err) {
      setError(err.message || 'Could not connect to backend');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-shell">
      <section className="panel left-panel">
        <div className="header-block">
          <p className="eyebrow">Website & App Builder</p>
          <h1>Describe your next idea</h1>
        </div>

        <form onSubmit={handleSubmit} className="prompt-form">
          <textarea
            value={prompt}
            onChange={(event) => setPrompt(event.target.value)}
            rows={8}
            placeholder="Create a modern fintech landing page for a startup in Lagos"
          />

          <button type="submit" disabled={loading}>
            {loading ? 'Building...' : 'Build app'}
          </button>
        </form>

        {error && <div className="error-box">{error}</div>}
      </section>

      <section className="panel right-panel">
        {result ? (
          <>
            <div className="result-header">
              <span className="badge">{result.app_type}</span>
              <h2>{result.title}</h2>
            </div>

            <div className="meta-grid">
              <div>
                <label>Theme</label>
                <strong>{result.theme}</strong>
              </div>
              <div>
                <label>Style</label>
                <strong>{result.style}</strong>
              </div>
              <div>
                <label>Location</label>
                <strong>{result.location?.city || 'N/A'}</strong>
              </div>
              <div>
                <label>Weather</label>
                <strong>{result.location?.weather || 'N/A'}</strong>
              </div>
            </div>

            <div className="preview-card">
              <div className="hero-block">
                <span>{result.title}</span>
                <h3>{result.hero_headline}</h3>
                <p>{result.hero_text}</p>
              </div>

              <div className="mini-grid">
                {result.pages.map((page) => (
                  <div key={page} className="mini-item">
                    {page}
                  </div>
                ))}
              </div>

              <div className="cta-row">
                <button type="button">Get started</button>
                <button type="button" className="ghost-button">View demo</button>
              </div>
            </div>
          </>
        ) : (
          <div className="empty-state">
            <h2>Ready to generate</h2>
            <p>Your app specification and preview will appear here.</p>
          </div>
        )}
      </section>
    </div>
  );
}

export default App;
