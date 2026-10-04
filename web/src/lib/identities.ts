// Saved API keys ("identities") for switching between demo users.
//
// Keys live in this browser's localStorage: fine for a local demo of per-user permissions,
// not a pattern for production (there, the browser would hold a session, not a raw key).
import { useSyncExternalStore } from "react";

export interface Identity {
  key: string;
  name: string;
  displayName: string;
  groups: string[];
}

interface State {
  identities: Identity[];
  activeName: string | null;
}

const STORAGE_SLOT = "provenance.identities.v1";
const listeners = new Set<() => void>();
let state: State = read();

function read(): State {
  try {
    const raw = localStorage.getItem(STORAGE_SLOT);
    if (raw) return JSON.parse(raw) as State;
  } catch {
    // Storage blocked or corrupted: start empty rather than fail.
  }
  return { identities: [], activeName: null };
}

function write(next: State): void {
  state = next;
  try {
    localStorage.setItem(STORAGE_SLOT, JSON.stringify(next));
  } catch {
    // Still usable for this session.
  }
  listeners.forEach((l) => l());
}

export const identities = {
  add(identity: Identity): void {
    const others = state.identities.filter((i) => i.name !== identity.name);
    write({ identities: [...others, identity], activeName: identity.name });
  },
  activate(name: string): void {
    write({ ...state, activeName: name });
  },
  remove(name: string): void {
    const rest = state.identities.filter((i) => i.name !== name);
    write({ identities: rest, activeName: state.activeName === name ? (rest[0]?.name ?? null) : state.activeName });
  },
};

function subscribe(listener: () => void): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

export function useIdentities(): { all: Identity[]; active: Identity | null } {
  const snapshot = useSyncExternalStore(subscribe, () => state);
  const active = snapshot.identities.find((i) => i.name === snapshot.activeName) ?? null;
  return { all: snapshot.identities, active };
}
