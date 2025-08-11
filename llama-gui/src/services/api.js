const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8000';
const WS_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/v1/stream';

export async function postCompletion({ prompt, max_tokens = 128, temperature = 0.7, model = 'llama-base' }) {
  const res = await fetch(`${API_BASE}/v1/completions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt, max_tokens, temperature, model }),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function postChatCompletion({ messages, max_tokens = 128, temperature = 0.7, model = 'llama-base' }) {
  const res = await fetch(`${API_BASE}/v1/chat/completions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ messages, max_tokens, temperature, model }),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export function openStream(prompt) {
  const url = new URL(WS_URL);
  // Send initial prompt as first message after connection is opened
  const ws = new WebSocket(url);
  ws.onopen = () => ws.send(prompt);
  return ws;
}
