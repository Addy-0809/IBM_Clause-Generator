import { useState } from 'react';
import './App.css';

const CLAUSE_TYPES = [
  'Arbitration',
  'Indemnity',
  'Confidentiality',
  'Termination',
  'Custom',
];

function App() {
  const [clauseType, setClauseType] = useState(CLAUSE_TYPES[0]);
  const [prompt, setPrompt] = useState('');
  const [examples, setExamples] = useState(['']);
  const [clause, setClause] = useState('');
  const [exporting, setExporting] = useState(false);
  const [error, setError] = useState('');

  const handleExampleChange = (idx, value) => {
    setExamples(exs => exs.map((ex, i) => (i === idx ? value : ex)));
  };

  const addExample = () => setExamples(exs => [...exs, '']);

  const removeExample = idx => setExamples(exs => exs.filter((_, i) => i !== idx));

  const generateClause = async () => {
    setClause('');
    setError('');
    const res = await fetch('http://localhost:8000/generate-clause', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ clause_type: clauseType, prompt, examples }),
    });
    const data = await res.json();
    if (data.clause) {
      setClause(data.clause);
    } else if (data.error) {
      setError(data.error);
    }
  };

  const exportClause = async (type) => {
    setExporting(true);
    const res = await fetch('http://localhost:8000/export', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ clause_text: clause, export_type: type }),
    });
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = type === 'word' ? 'clause.docx' : 'clause.pdf';
    a.click();
    setExporting(false);
  };

  return (
    <div className="container">
      <h1>Legal Clause Generator</h1>
      <div className="form-section">
        <label>Clause Type:</label>
        <select value={clauseType} onChange={e => setClauseType(e.target.value)}>
          {CLAUSE_TYPES.map(type => (
            <option key={type} value={type}>{type}</option>
          ))}
        </select>
        <label>Prompt:</label>
        <textarea value={prompt} onChange={e => setPrompt(e.target.value)} placeholder="Describe the clause or provide instructions..." />
        <label>Few-shot Examples:</label>
        {examples.map((ex, idx) => (
          <div key={idx} style={{ display: 'flex', alignItems: 'center', marginBottom: 4 }}>
            <input
              type="text"
              value={ex}
              onChange={e => handleExampleChange(idx, e.target.value)}
              placeholder={`Example ${idx + 1}`}
              style={{ flex: 1 }}
            />
            {examples.length > 1 && (
              <button onClick={() => removeExample(idx)} style={{ marginLeft: 4 }}>Remove</button>
            )}
          </div>
        ))}
        <button onClick={addExample}>Add Example</button>
        <button onClick={generateClause} style={{ marginTop: 12 }}>Generate Clause</button>
      </div>
      {clause && (
        <div className="result-section">
          <h2>Generated Clause</h2>
          <pre style={{ background: '#f4f4f4', padding: 12 }}>{clause}</pre>
          <button onClick={() => exportClause('word')} disabled={exporting}>Export as Word</button>
          <button onClick={() => exportClause('pdf')} disabled={exporting} style={{ marginLeft: 8 }}>Export as PDF</button>
        </div>
      )}
      {error && <div style={{ color: 'red', marginTop: 12 }}>{error}</div>}
    </div>
  );
}

export default App;
