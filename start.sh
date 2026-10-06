body {
  margin: 0;
  font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: #07111f;
  color: #f2f7ff;
}

* { box-sizing: border-box; }

button, textarea {
  font: inherit;
}

.app-shell {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 1fr 1.2fr;
  gap: 24px;
  padding: 32px;
}

.panel {
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 24px;
  padding: 24px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

h1 {
  font-size: 2.2rem;
  margin: 0 0 8px 0;
}

.subtitle {
  color: #a9b9d1;
  margin-bottom: 24px;
}

textarea {
  width: 100%;
  min-height: 200px;
  resize: vertical;
  border-radius: 16px;
  background: #0f172a;
  color: #e5eefb;
  border: 1px solid rgba(148, 163, 184, 0.3);
  padding: 16px;
  margin-bottom: 16px;
}

button {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  border: none;
  border-radius: 12px;
  color: white;
  padding: 12px 18px;
  font-weight: 700;
  cursor: pointer;
}

button.secondary {
  background: transparent;
  border: 1px solid rgba(148, 163, 184, 0.5);
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error {
  margin-top: 16px;
  background: rgba(127, 29, 29, 0.3);
  border: 1px solid rgba(239, 68, 68, 0.5);
  color: #fecaca;
  padding: 12px 14px;
  border-radius: 12px;
}

.result-header {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 20px;
}

.badge {
  display: inline-flex;
  width: fit-content;
  background: rgba(59, 130, 246, 0.12);
  border: 1px solid rgba(96, 165, 250, 0.35);
  color: #bfdbfe;
  border-radius: 999px;
  padding: 5px 10px;
  font-size: 0.8rem;
  text-transform: uppercase;
}

.meta-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 24px;
}

.meta-grid > div {
  background: rgba(15, 23, 42, 0.9);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 12px;
  padding: 12px;
}

.meta-grid label {
  display: block;
  color: #8ea3bf;
  margin-bottom: 6px;
  font-size: 0.78rem;
}

.preview-box {
  margin-top: 18px;
}

.preview-card {
  margin-top: 12px;
  background: linear-gradient(135deg, #0f172a, #111827);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 20px;
  padding: 20px;
}

.hero {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(15, 118, 110, 0.18));
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 16px;
}

.hero span {
  color: #7dd3fc;
  font-size: 0.8rem;
  text-transform: uppercase;
}

.hero h4 {
  font-size: 2rem;
  margin: 10px 0;
}

.section-list {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin: 20px 0;
}

.mini-card {
  background: rgba(15, 23, 42, 0.9);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 12px;
  padding: 16px;
  text-align: center;
}

.cta-row {
  display: flex;
  gap: 12px;
  margin-top: 18px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 100%;
  color: #cbd5e1;
  text-align: center;
}

@media (max-width: 900px) {
  .app-shell {
    grid-template-columns: 1fr;
  }
}
