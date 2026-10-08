import { useSyncExternalStore } from "react";

import type { AgentResult } from "./api";

/** Past questions and their answers, per identity, kept in this browser only. A
 *  convenience: it can be empty (private window, cleared storage) and the app works the same. */
export interface HistoryItem {
  id: string;
  identity: string;
  question: string;
  askedAt: number;
  elapsedMs: number;
  result: AgentResult;
}

const KEY = "provenance.history.v1";
const LIMIT = 40;
const listeners = new Set<() => void>();
let items: HistoryItem[] = load();

function load(): HistoryItem[] {
  try {
    const raw = localStorage.getItem(KEY);
    return raw ? (JSON.parse(raw) as HistoryItem[]) : [];
  } catch {
    return [];
  }
}

function save(next: HistoryItem[]): void {
  items = next;
  try {
    localStorage.setItem(KEY, JSON.stringify(next));
  } catch {
    // Full or blocked storage: keep the in-memory list for this session.
  }
  listeners.forEach((l) => l());
}

export const history = {
  add(identity: string, question: string, result: AgentResult, elapsedMs: number): void {
    const item: HistoryItem = {
      id: `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 7)}`,
      identity,
      question,
      askedAt: Date.now(),
      elapsedMs,
      result,
    };
    save([item, ...items.filter((i) => !(i.identity === identity && i.question === question))].slice(0, LIMIT));
  },
  remove(id: string): void {
    save(items.filter((i) => i.id !== id));
  },
  clear(identity: string): void {
    save(items.filter((i) => i.identity !== identity));
  },
};

function subscribe(listener: () => void): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

export function useHistory(identity: string): HistoryItem[] {
  const all = useSyncExternalStore(subscribe, () => items);
  return all.filter((i) => i.identity === identity);
}
