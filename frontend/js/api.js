const MOCK_URL = './mock-data/status.json';

export async function fetchStatus() {
  const res = await fetch(MOCK_URL, { cache: 'no-store' });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}
