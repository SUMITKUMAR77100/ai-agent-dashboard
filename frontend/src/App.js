import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import './App.css';

const API = 'http://localhost:8080';

const TOOL_ICONS = {
  web_search: '🔍',
  calculator: '🧮',
  document_retrieval: '📄',
};

const QUICK_QUESTIONS = [
  "What are the top 3 Node.js ORMs?",
  "What is RAG and how does it work?",
  "If I earn 1500000 per year, what is my monthly salary?",
  "What is the difference between DPO and PPO?",
  "Search for best AI tools and calculate 15% of 25000",
];

function StepCard({ step, index }) {
  const [open, setOpen] = useState(true);

  return (
    <div className="step-card">
      <div className="step-header" onClick={() => setOpen(!open)}>
        <div className="step-number">{index + 1}</div>
        <span className="tool-icon">{TOOL_ICONS[step.tool] || '🔧'}</span>
        <span className="tool-name">{step.tool}</span>
        <span className="step-toggle">{open ? '▲' : '▼'}</span>
      </div>
      {open && (
        <div className="step-body">
          <div className="step-label">Input</div>
          <div className="step-content">
            {JSON.stringify(step.input, null, 2)}
          </div>
          <div className="step-label">Result</div>
          <div className="step-content">{step.result}</div>
        </div>
      )}
    </div>
  );
}

function Message({ msg }) {
  return (
    <div className={`message ${msg.role}`}>
      <div className="avatar">{msg.role === 'user' ? '👤' : '🤖'}</div>
      <div className="bubble">
        {msg.loading ? (
          <div className="loading-dots">
            <span /><span /><span />
          </div>
        ) : (
          <ReactMarkdown>{msg.content}</ReactMarkdown>
        )}
      </div>
    </div>
  );
}

export default function App() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: '👋 Hi! I\'m your AI Research Agent. I can **search the web**, **calculate numbers**, and **retrieve documents** to answer your questions.\n\nTry asking me anything — you can see my thinking process in the left sidebar!',
    }
  ]);
  const [input, setInput]         = useState('');
  const [loading, setLoading]     = useState(false);
  const [steps, setSteps]         = useState([]);
  const [stats, setStats]         = useState({ questions: 0, toolCalls: 0, tokens: 0 });
  const [summary, setSummary]     = useState(null);
  const bottomRef = useRef(null);
  const inputRef  = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const getHistory = () =>
    messages
      .filter(m => !m.loading && m.role !== 'system')
      .map(m => ({ role: m.role, content: m.content }));

  const sendMessage = async (question) => {
    const q = question || input.trim();
    if (!q || loading) return;

    setInput('');
    setLoading(true);
    setSteps([]);

    setMessages(prev => [
      ...prev,
      { role: 'user', content: q },
      { role: 'assistant', content: '', loading: true }
    ]);

    try {
      const res = await fetch(`${API}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: q, history: getHistory() }),
      });

      if (!res.ok) throw new Error(`Server error: ${res.status}`);
      const data = await res.json();

      setMessages(prev => {
        const updated = [...prev];
        updated[updated.length - 1] = {
          role: 'assistant',
          content: data.answer,
        };
        return updated;
      });

      setSteps(data.steps || []);
      if (data.context_summary) setSummary(data.context_summary);

      setStats(prev => ({
        questions: prev.questions + 1,
        toolCalls: prev.toolCalls + (data.steps?.length || 0),
        tokens: data.tokens_used || prev.tokens,
      }));

    } catch (e) {
      setMessages(prev => {
        const updated = [...prev];
        updated[updated.length - 1] = {
          role: 'assistant',
          content: `⚠️ Error: ${e.message}. Make sure the backend is running on port 8080.`,
        };
        return updated;
      });
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="app">
      {/* ── Sidebar ── */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="sidebar-title">🤖 Agent Dashboard</div>
          <div className="sidebar-subtitle">Week 3 Final Project — ReAct Agent</div>
        </div>

        <div className="stats-bar">
          <div className="stat">
            <span className="stat-value">{stats.questions}</span>
            Questions
          </div>
          <div className="stat">
            <span className="stat-value">{stats.toolCalls}</span>
            Tool Calls
          </div>
          <div className="stat">
            <span className="stat-value">{stats.tokens}</span>
            Tokens
          </div>
        </div>

        {summary && (
          <div className="context-summary">
            <div className="context-label">⚡ Context Summarised</div>
            <div className="context-text">{summary}</div>
          </div>
        )}

        <div className="thinking-panel">
          <div className="thinking-title">🧠 Agent Thinking</div>
          {steps.length === 0 ? (
            <div className="no-steps">
              Ask a question to see the agent's reasoning steps here
            </div>
          ) : (
            steps.map((step, i) => (
              <StepCard key={i} step={step} index={i} />
            ))
          )}
        </div>
      </aside>

      {/* ── Chat ── */}
      <main className="chat-area">
        <div className="chat-header">
          <div className="chat-header-title">💬 AI Research Agent</div>
          <div className="model-badge">llama-3.1-8b · Groq</div>
        </div>

        <div className="messages">
          {messages.map((msg, i) => (
            <Message key={i} msg={msg} />
          ))}
          <div ref={bottomRef} />
        </div>

        <div className="input-area">
          <div className="quick-questions">
            {QUICK_QUESTIONS.map((q, i) => (
              <button
                key={i}
                className="quick-btn"
                onClick={() => sendMessage(q)}
                disabled={loading}
              >
                {q.length > 40 ? q.slice(0, 40) + '...' : q}
              </button>
            ))}
          </div>
          <div className="input-row">
            <textarea
              ref={inputRef}
              className="input-field"
              placeholder="Ask anything — I'll use tools to find the answer..."
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKey}
              disabled={loading}
              rows={1}
            />
            <button
              className="send-btn"
              onClick={() => sendMessage()}
              disabled={loading || !input.trim()}
            >
              {loading ? '⏳' : '➤'}
            </button>
          </div>
          <div className="input-hint">Enter to send · Shift+Enter for new line</div>
        </div>
      </main>
    </div>
  );
}
