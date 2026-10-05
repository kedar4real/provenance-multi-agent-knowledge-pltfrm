import { Dialog } from "@base-ui/react/dialog";
import { Tabs } from "@base-ui/react/tabs";
import { useRef, useState } from "react";

import { AccessScope } from "./components/AccessScope";
import { AskView } from "./components/AskView";
import { AddIdentityButton, IdentityMenu } from "./components/IdentityMenu";
import { HitCard } from "./components/HitCard";
import { ResultsSummary } from "./components/ResultsSummary";
import { EXAMPLES, SearchForm } from "./components/SearchForm";
import { SourcePanel } from "./components/SourcePanel";
import { api, ApiError, type SearchParams, type SearchResult } from "./lib/api";
import { useIdentities, type Identity } from "./lib/identities";
import { useMediaQuery } from "./lib/useMediaQuery";

type SearchState =
  | { status: "idle" }
  | { status: "pending" }
  | { status: "done"; result: SearchResult }
  | { status: "error"; message: string; requestId: string | null };

export default function App() {
  const { active } = useIdentities();
  return (
    <div className="min-h-dvh">
      <header className="sticky top-0 z-20 border-b border-rule bg-paper">
        <div className="mx-auto flex h-14 max-w-[90rem] items-center justify-between gap-4 px-4 pt-[env(safe-area-inset-top)] sm:px-6">
          <div className="flex items-baseline gap-3">
            <span className="font-serif text-xl font-semibold">provenance</span>
            <span className="hidden text-sm text-ink-3 sm:inline">10-K research, every passage traced</span>
          </div>
          <IdentityMenu />
        </div>
      </header>
      {active ? (
        <Workspace key={active.name} identity={active} />
      ) : (
        <main className="mx-auto w-full max-w-3xl px-4 py-8 sm:px-6">
          <Welcome />
        </main>
      )}
    </div>
  );
}

function Workspace({ identity }: { identity: Identity }) {
  const [params, setParams] = useState<SearchParams>({
    query: "",
    k: 8,
    mode: "hybrid",
    rerank: true,
    rewrite: true,
  });
  const [search, setSearch] = useState<SearchState>({ status: "idle" });
  const [selected, setSelected] = useState<number | null>(null);
  const inFlight = useRef<AbortController | null>(null);
  const wide = useMediaQuery("(min-width: 1024px)");

  async function run(next: SearchParams = params) {
    inFlight.current?.abort();
    const controller = new AbortController();
    inFlight.current = controller;
    setSearch({ status: "pending" });
    setSelected(null);
    try {
      const result = await api.search(identity.key, { ...next, query: next.query.trim() }, controller.signal);
      setSearch({ status: "done", result });
    } catch (e) {
      if (controller.signal.aborted) return;
      setSearch({
        status: "error",
        message: (e as Error).message,
        requestId: e instanceof ApiError ? e.requestId : null,
      });
    }
  }

  return (
    <>
      <div
        className={
          selected !== null && wide
            ? "mx-auto grid max-w-[90rem] grid-cols-[minmax(0,1fr)_minmax(0,34rem)]"
            : "mx-auto max-w-[90rem]"
        }
      >
        <main className="mx-auto w-full max-w-3xl px-4 py-6 sm:px-6">
          <Tabs.Root defaultValue="ask">
            <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
              <Tabs.List aria-label="Mode" className="relative flex rounded-md border border-rule bg-sheet p-0.5">
                <Tabs.Tab
                  value="ask"
                  className="h-8 rounded px-3.5 text-sm text-ink-2 hover:text-ink data-active:bg-ink data-active:text-paper"
                >
                  Ask
                </Tabs.Tab>
                <Tabs.Tab
                  value="search"
                  className="h-8 rounded px-3.5 text-sm text-ink-2 hover:text-ink data-active:bg-ink data-active:text-paper"
                >
                  Search passages
                </Tabs.Tab>
              </Tabs.List>
              <AccessScope identity={identity} />
            </div>
            <Tabs.Panel value="ask" keepMounted className="data-hidden:hidden">
              <AskView identity={identity} onOpenSource={setSelected} />
            </Tabs.Panel>
            <Tabs.Panel value="search" keepMounted className="space-y-6 data-hidden:hidden">
              <div className="space-y-3">
                <SearchForm
                  params={params}
                  onChange={setParams}
                  onSubmit={() => void run()}
                  pending={search.status === "pending"}
                  disabled={false}
                />
              </div>
              <Results
                state={search}
                selected={selected}
                onSelect={(id) => setSelected((cur) => (cur === id ? null : id))}
                onExample={(q) => {
                  const next = { ...params, query: q };
                  setParams(next);
                  void run(next);
                }}
                identityName={identity.displayName}
              />
            </Tabs.Panel>
          </Tabs.Root>
        </main>

        {selected !== null && wide && (
          <aside
            aria-label="Source passage"
            className="sticky top-14 h-[calc(100dvh-3.5rem)] border-l border-rule bg-sheet"
          >
            <SourcePanel apiKey={identity.key} chunkId={selected} onClose={() => setSelected(null)} />
          </aside>
        )}
      </div>

      {!wide && (
        <Dialog.Root open={selected !== null} onOpenChange={(open) => !open && setSelected(null)}>
          <Dialog.Portal>
            <Dialog.Backdrop className="fixed inset-0 z-40 bg-ink/20" />
            <Dialog.Popup className="fixed inset-x-0 bottom-0 z-50 h-[85dvh] rounded-t-xl border-t border-rule bg-sheet pb-[env(safe-area-inset-bottom)] transition-transform duration-200 ease-out data-ending-style:translate-y-full data-starting-style:translate-y-full">
              {selected !== null && (
                <SourcePanel
                  apiKey={identity.key}
                  chunkId={selected}
                  onClose={() => setSelected(null)}
                  titleAs={Dialog.Title}
                />
              )}
            </Dialog.Popup>
          </Dialog.Portal>
        </Dialog.Root>
      )}
    </>
  );
}

function Results(props: {
  state: SearchState;
  selected: number | null;
  onSelect: (chunkId: number) => void;
  onExample: (query: string) => void;
  identityName: string;
}) {
  const { state } = props;

  if (state.status === "idle") {
    return (
      <section aria-label="Example questions" className="pt-4">
        <p className="text-sm text-ink-3">Try a question</p>
        <ul className="mt-2 divide-y divide-rule border-y border-rule">
          {EXAMPLES.map((q) => (
            <li key={q}>
              <button
                type="button"
                onClick={() => props.onExample(q)}
                className="w-full py-3 text-left font-serif text-[17px] text-ink-2 hover:text-ink"
              >
                {q}
              </button>
            </li>
          ))}
        </ul>
      </section>
    );
  }

  if (state.status === "pending") {
    return (
      <div aria-busy="true" aria-live="polite" className="space-y-3">
        <p className="text-sm text-ink-3">Searching… reranking takes a few seconds on CPU.</p>
        {[0, 1, 2].map((i) => (
          <div key={i} className="grid grid-cols-[6.5rem_1fr] gap-4 rounded-lg border border-rule bg-sheet p-4">
            <div className="space-y-2 border-r border-rule pr-3">
              <div className="h-3 w-10 animate-pulse rounded bg-inset" />
              <div className="h-3 w-14 animate-pulse rounded bg-inset" />
            </div>
            <div className="space-y-2">
              <div className="h-3.5 w-1/3 animate-pulse rounded bg-inset" />
              <div className="h-3 w-full animate-pulse rounded bg-inset" />
              <div className="h-3 w-11/12 animate-pulse rounded bg-inset" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (state.status === "error") {
    return (
      <div role="alert" className="rounded-lg border border-danger/40 bg-sheet px-4 py-3 text-sm">
        <p className="text-danger">{state.message}</p>
        {state.requestId && <p className="mt-1 font-mono text-[12px] text-ink-3">request {state.requestId}</p>}
      </div>
    );
  }

  const { result } = state;
  return (
    <div className="space-y-4" aria-live="polite">
      <ResultsSummary result={result} />
      <WeakEvidenceNotice result={result} identityName={props.identityName} />
      {result.hits.length === 0 ? (
        <div className="py-10 text-center">
          <p className="font-serif text-lg">No passages {props.identityName} can see match this.</p>
          <p className="mt-1 text-sm text-ink-3">Try naming a company, or turn on Rewrite in retrieval settings.</p>
        </div>
      ) : (
        <ol className="space-y-3">
          {result.hits.map((hit, i) => (
            <li key={hit.chunk_id}>
              <HitCard
                hit={hit}
                rank={i + 1}
                selected={props.selected === hit.chunk_id}
                onSelect={() => props.onSelect(hit.chunk_id)}
              />
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}

function Welcome() {
  return (
    <section className="py-16">
      <h1 className="max-w-xl font-serif text-[2.5rem] leading-[1.1] font-medium">
        Search 60 annual reports. See only what you're cleared for.
      </h1>
      <p className="mt-4 max-w-xl text-ink-2">
        Every result is a passage from a real 10-K filing, traced to its section and accession number.
        What you can see depends on who you are: the database enforces it, not this page.
      </p>
      <div className="mt-8 flex flex-wrap items-center gap-3">
        <AddIdentityButton />
        <span className="text-sm text-ink-3">You'll need an API key from the terminal.</span>
      </div>
    </section>
  );
}

// In the first eval run the best rerank score had a median of 0.99 for answerable questions
// and 0.14 for unanswerable ones. Below this line, say so instead of implying an answer.
// An uncalibrated hint; calibrated abstention is a later milestone.
const WEAK_EVIDENCE = 0.3;

function WeakEvidenceNotice({ result, identityName }: { result: SearchResult; identityName: string }) {
  const scores = result.hits.map((h) => h.rerank_score).filter((s): s is number => s !== null);
  if (!result.reranked || scores.length === 0 || Math.max(...scores) >= WEAK_EVIDENCE) return null;
  return (
    <div role="status" className="rounded-lg border border-rule bg-inset px-4 py-3 text-sm">
      <p className="font-medium text-ink">These passages probably don't answer the question.</p>
      <p className="mt-0.5 text-ink-2">
        The best match scored {Math.max(...scores).toFixed(2)} for relevance. The answer may be in filings{" "}
        {identityName.split(" ")[0]} can't see, or not in any filing.
      </p>
    </div>
  );
}
