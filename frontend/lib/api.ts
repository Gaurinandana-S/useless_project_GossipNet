import { GameState, QuestionResponse, GuessResponse, GiveUpResponse } from '@/types/game';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api';

async function safeFetch(url: string, init?: RequestInit): Promise<Response> {
  try {
    return await fetch(url, init);
  } catch (err: any) {
    throw new Error(
      'Cannot connect to backend server at http://127.0.0.1:8000. Please ensure the FastAPI backend is running (e.g. run_backend.bat or run_all.bat).'
    );
  }
}

export async function createGame(
  difficulty: number = 1,
  seed?: number,
  gameMode: string = 'GUESS_RUMOR_START'
): Promise<GameState> {
  const res = await safeFetch(`${API_BASE}/game/create`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ difficulty, random_seed: seed, game_mode: gameMode }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to create game' }));
    throw new Error(err.detail || 'Failed to create game');
  }
  return res.json();
}

export async function getGame(gameId: string): Promise<GameState> {
  const res = await safeFetch(`${API_BASE}/game/${gameId}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to fetch game' }));
    throw new Error(err.detail || 'Failed to fetch game');
  }
  return res.json();
}

export async function askQuestion(
  gameId: string,
  personId: string,
  questionKey?: string,
  customText?: string
): Promise<QuestionResponse> {
  const res = await safeFetch(`${API_BASE}/game/${gameId}/question`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ person_id: personId, question_key: questionKey, custom_text: customText }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to evaluate question' }));
    throw new Error(err.detail || 'Failed to ask question');
  }
  return res.json();
}

export async function makeGuess(gameId: string, personId: string): Promise<GuessResponse> {
  const res = await safeFetch(`${API_BASE}/game/${gameId}/guess`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ person_id: personId }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to submit guess' }));
    throw new Error(err.detail || 'Failed to submit guess');
  }
  return res.json();
}

export async function giveUp(gameId: string): Promise<GiveUpResponse> {
  const res = await safeFetch(`${API_BASE}/game/${gameId}/give-up`, {
    method: 'POST',
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to give up' }));
    throw new Error(err.detail || 'Failed to give up');
  }
  return res.json();
}

export async function nextGame(gameId: string): Promise<GameState> {
  const res = await safeFetch(`${API_BASE}/game/${gameId}/next`, {
    method: 'POST',
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to generate next rumor round' }));
    throw new Error(err.detail || 'Failed to generate next rumor');
  }
  return res.json();
}

