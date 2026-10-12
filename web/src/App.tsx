import { Dialog } from "@base-ui/react/dialog";
import { Tabs } from "@base-ui/react/tabs";
import {
  Activity,
  BadgeCheck,
  Columns2,
  Command,
  Eye,
  History,
  LoaderCircle,
  MessageSquareText,
  ScrollText,
  SearchX,
  ShieldCheck,
  Sparkles,
  TextSearch,
  TriangleAlert,
  UserRound,
} from "lucide-react";
import { lazy, Suspense, useCallback, useEffect, useRef, useState } from "react";

import { AccessScope } from "./components/AccessScope";
import { AskView, QUESTION_INPUT_ID } from "./components/AskView";
import { CommandPalette, type PaletteAction } from "./components/CommandPalette";
import { AddIdentityButton, IdentityMenu } from "./components/IdentityMenu";
import { HitCard } from "./components/HitCard";
import { ResultsSummary } from "./components/ResultsSummary";
import { ExampleList } from "./components/ExampleList";
import { EXAMPLES, SearchForm } from "./components/SearchForm";
import { SourcePanel } from "./components/SourcePanel";
import { api, ApiError, type SearchParams, type SearchResult } from "./lib/api";
import { identities, useIdentities, type Identity } from "./lib/identities";
import { useMediaQuery } from "./lib/useMediaQuery";

// The heavier views load on first use, keeping the first page small.
const CompareView = lazy(() => import("./components/CompareView").then((m) => ({ default: m.CompareView })));
const StatsView = lazy(() => import("./components/StatsView").then((m) => ({ default: m.StatsView })));
const AuditView = lazy(() => import("./components/AuditView").then((m) => ({ default: m.AuditView })));

function Loading() {
  return <div className="skeleton h-48 rounded-2xl" aria-busy="true" />;
}

type SearchState =
  | { status: "idle" }
  | { status: "pending" }
  | { status: "done"; result: SearchResult }
  | { status: "error"; message: string; requestId: string | null };

export default function App() {
  const { active } = useIdentities();
  return (
    <div className="min-h-dvh">
      <header className="glass sticky top-0 z-20 border-b border-rule">
        <div className="mx-auto flex h-14 max-w-[90rem] items-center justify-between gap-4 px-4 pt-[env(safe-area-inset-top)] sm:px-6">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-2.5">
              <span aria-hidden className="grid size-8 place-items-center rounded-lg bg-ink text-paper shadow-card">
                <ScrollText className="size-4" />
              </span>
              <span className="font-display text-[25px] leading-none tracking-tight">
                provenance<span className="text-pencil">.</span>
              </span>
            </span>
            <span className="smallcaps hidden text-ink-3 md:inline">
              S&amp;P 500 annual reports (10-K filings)
            </span>
          </div>
          <IdentityMenu />
        </div>
      </header>
      {active ? (
        <Workspace key={active.name} identity={active} />
      ) : (
        <main className="mx-auto min-h-[calc(100dvh-3.5rem)] w-full max-w-3xl px-4 py-8 sm:px-8">
          <Welcome />
        </main>
      )}
    </div>
  );
}

type Tab = "ask" | "compare" | "search" | "dashboard" | "audit";

const TAB_CLASS =
  "relative z-10 flex h-9 shrink-0 items-center gap-2 rounded-full px-3.5 text-sm text-ink-3 transition-colors hover:text-ink data-active:font-medium data-active:text-ink";

function isTyping(target: EventTarget | null): boolean {
  const el = target as HTMLElement | null;
  return Boolean(el && (el.isContentEditable || ["INPUT", "TEXTAREA", "SELECT"].includes(el.tagName)));
}

function Workspace({ identity }: { identity: Identity }) {
  const { all } = useIdentities();
  const [params, setParams] = useState<SearchParams>({
    query: "",
    k: 8,
    mode: "hybrid",
    rerank: true,
    rewrite: true,
  });
  const [search, setSearch] = useState<SearchState>({ status: "idle" });
  // The source panel reads with the key of whoever's answer it came from (Compare shows two).
  const [selected, setSelected] = useState<{ chunkId: number; apiKey: string } | null>(null);
  const [tab, setTab] = useState<Tab>("ask");
  const [pending, setPending] = useState<{ question: string; ask: boolean; nonce: number } | null>(null);
  const [historyOpen, setHistoryOpen] = useState(false);
  const [paletteOpen, setPaletteOpen] = useState(false);
  const [auditor, setAuditor] = useState(false);
  const inFlight = useRef<AbortController | null>(null);
  const wide = useMediaQuery("(min-width: 1024px)");

  // Group membership comes from the API, not the locally saved identity, so it's current.
  useEffect(() => {
    const controller = new AbortController();
    api.me(identity.key, controller.signal).then((me) => setAuditor(me.groups.includes("auditor")), () => undefined);
    return () => controller.abort();
  }, [identity.key]);

  const openSource = useCallback((chunkId: number, apiKey?: string) => setSelected({ chunkId, apiKey: apiKey ?? identity.key }), [identity.key]);
  const askAbout = useCallback((question: string, ask = false) => {
    setTab("ask");
    setPending({ question, ask, nonce: Date.now() });
  }, []);
  const takePending = useCallback(() => setPending(null), []);

  useEffect(() => {
    const tabs: Tab[] = ["ask", "compare", "search", "dashboard", ...(auditor ? (["audit"] as Tab[]) : [])];
    const onKey = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setPaletteOpen((o) => !o);
        return;
      }
      if (isTyping(e.target) || e.ctrlKey || e.metaKey || e.altKey) return;
      if (e.key === "/") {
        e.preventDefault();
        setTab("ask");
        window.setTimeout(() => document.getElementById(QUESTION_INPUT_ID)?.focus(), 0);
      } else if (/^[1-5]$/.test(e.key)) {
        const next = tabs[Number(e.key) - 1];
        if (next) setTab(next);
      } else if (e.key.toLowerCase() === "h") {
        setTab("ask");
        setHistoryOpen(true);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [auditor]);

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

  const actions: PaletteAction[] = [
    { id: "go-ask", group: "Go to", label: "Ask", icon: MessageSquareText, hint: "1", run: () => setTab("ask") },
    { id: "go-compare", group: "Go to", label: "Compare two people", icon: Columns2, hint: "2", run: () => setTab("compare") },
    { id: "go-search", group: "Go to", label: "Search passages", icon: TextSearch, hint: "3", run: () => setTab("search") },
    { id: "go-dashboard", group: "Go to", label: "Dashboard", icon: Activity, hint: "4", run: () => setTab("dashboard") },
    ...(auditor
      ? [{ id: "go-audit", group: "Go to", label: "Audit log", icon: ScrollText, hint: "5", run: () => setTab("audit") }]
      : []),
    { id: "focus", group: "Actions", label: "Focus the question box", icon: Sparkles, hint: "/", run: () => askAbout("") },
    { id: "history", group: "Actions", label: "Open history", icon: History, hint: "H", run: () => { setTab("ask"); setHistoryOpen(true); } },
    ...all
      .filter((i) => i.name !== identity.name)
      .map((i) => ({ id: `as-${i.name}`, group: "Switch identity", label: i.displayName, icon: UserRound, run: () => identities.activate(i.name) })),
  ];

  const wideTab = tab === "compare" || tab === "dashboard" || tab === "audit";
  return (
    <>
      <div
        className={
          selected !== null && wide && !wideTab
            ? "mx-auto grid max-w-[90rem] grid-cols-[minmax(0,1fr)_minmax(0,34rem)]"
            : "mx-auto max-w-[90rem]"
        }
      >
        <main
          className={`mx-auto min-h-[calc(100dvh-3.5rem)] w-full px-4 py-6 sm:px-8 ${wideTab ? "max-w-6xl" : "max-w-3xl"}`}
        >
          <Tabs.Root value={tab} onValueChange={(v) => setTab(v as Tab)}>
            <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
              <Tabs.List
                aria-label="Mode"
                className="relative flex max-w-full overflow-x-auto rounded-full border border-rule bg-inset p-1 [scrollbar-width:none]"
              >
                <Tabs.Tab value="ask" className={TAB_CLASS}>
                  <MessageSquareText aria-hidden className="size-4" />
                  Ask
                </Tabs.Tab>
                <Tabs.Tab value="compare" className={TAB_CLASS}>
                  <Columns2 aria-hidden className="size-4" />
                  Compare
                </Tabs.Tab>
                <Tabs.Tab value="search" className={TAB_CLASS}>
                  <TextSearch aria-hidden className="size-4" />
                  Search
                </Tabs.Tab>
                <Tabs.Tab value="dashboard" className={TAB_CLASS}>
                  <Activity aria-hidden className="size-4" />
                  Dashboard
                </Tabs.Tab>
                {auditor && (
                  <Tabs.Tab value="audit" className={TAB_CLASS}>
                    <ScrollText aria-hidden className="size-4" />
                    Audit
                  </Tabs.Tab>
                )}
                <Tabs.Indicator className="absolute top-[var(--active-tab-top)] left-[var(--active-tab-left)] h-[var(--active-tab-height)] w-[var(--active-tab-width)] rounded-full bg-sheet shadow-card ring-1 ring-rule transition-[left,width] duration-300 ease-[cubic-bezier(0.3,1.3,0.5,1)]" />
              </Tabs.List>
              <div className="flex items-center gap-3">
                <AccessScope identity={identity} />
                <button
                  type="button"
                  onClick={() => setPaletteOpen(true)}
                  className="hidden shrink-0 items-center gap-2 rounded-full border border-rule bg-sheet px-3 py-1.5 text-[12px] whitespace-nowrap text-ink-3 shadow-card hover:text-ink sm:inline-flex"
                >
                  <Command aria-hidden className="size-3.5" />
                  Ctrl K
                </button>
              </div>
            </div>
            <Tabs.Panel value="ask" keepMounted className="data-hidden:hidden">
              <AskView
                identity={identity}
                onOpenSource={openSource}
                pending={pending}
                onPendingTaken={takePending}
                historyOpen={historyOpen}
                onHistoryOpenChange={setHistoryOpen}
              />
            </Tabs.Panel>
            <Tabs.Panel value="compare" keepMounted className="data-hidden:hidden">
              <Suspense fallback={<Loading />}>
                <CompareView identity={identity} onOpenSource={openSource} />
              </Suspense>
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
                selected={selected?.chunkId ?? null}
                onSelect={(id) => setSelected((cur) => (cur?.chunkId === id ? null : { chunkId: id, apiKey: identity.key }))}
                onExample={(q) => {
                  const next = { ...params, query: q };
                  setParams(next);
                  void run(next);
                }}
                identityName={identity.displayName}
              />
            </Tabs.Panel>
            <Tabs.Panel value="dashboard" className="data-hidden:hidden">
              <Suspense fallback={<Loading />}>
                <StatsView identity={identity} />
              </Suspense>
            </Tabs.Panel>
            {auditor && (
              <Tabs.Panel value="audit" className="data-hidden:hidden">
                <Suspense fallback={<Loading />}>
                  <AuditView identity={identity} onOpenSource={openSource} />
                </Suspense>
              </Tabs.Panel>
            )}
          </Tabs.Root>
        </main>

        {selected !== null && wide && !wideTab && (
          <aside
            aria-label="Source passage"
            className="sticky top-14 h-[calc(100dvh-3.5rem)] animate-slide-in border-l border-rule bg-sheet shadow-lift"
          >
            <SourcePanel
              apiKey={selected.apiKey}
              chunkId={selected.chunkId}
              onClose={() => setSelected(null)}
              onAskAbout={(q) => askAbout(q)}
            />
          </aside>
        )}
      </div>

      {(!wide || wideTab) && (
        <Dialog.Root open={selected !== null} onOpenChange={(open) => !open && setSelected(null)}>
          <Dialog.Portal>
            <Dialog.Backdrop className="fixed inset-0 z-40 bg-ink/25 backdrop-blur-[2px] transition-opacity duration-200 data-ending-style:opacity-0 data-starting-style:opacity-0" />
            <Dialog.Popup
              className={
                wide
                  ? "fixed inset-y-0 right-0 z-50 w-[34rem] border-l border-rule bg-sheet shadow-lift transition-transform duration-300 ease-[cubic-bezier(0.2,0.8,0.2,1)] data-ending-style:translate-x-full data-starting-style:translate-x-full"
                  : "fixed inset-x-0 bottom-0 z-50 h-[85dvh] rounded-t-2xl border-t border-rule bg-sheet pb-[env(safe-area-inset-bottom)] shadow-lift transition-transform duration-200 ease-out data-ending-style:translate-y-full data-starting-style:translate-y-full"
              }
            >
              {selected !== null && (
                <SourcePanel
                  apiKey={selected.apiKey}
                  chunkId={selected.chunkId}
                  onClose={() => setSelected(null)}
                  titleAs={Dialog.Title}
                  onAskAbout={(q) => {
                    setSelected(null);
                    askAbout(q);
                  }}
                />
              )}
            </Dialog.Popup>
          </Dialog.Portal>
        </Dialog.Root>
      )}

      <CommandPalette open={paletteOpen} onOpenChange={setPaletteOpen} actions={actions} onAsk={(q) => askAbout(q, true)} />
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
      <ExampleList examples={EXAMPLES} onPick={props.onExample} />
    );
  }

  if (state.status === "pending") {
    return (
      <div aria-busy="true" aria-live="polite" className="space-y-3">
        <p className="flex items-center gap-2 text-sm text-ink-3">
          <LoaderCircle aria-hidden className="size-4 animate-spin text-pencil" />
          Searching… reranking takes a few seconds on CPU.
        </p>
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            className="grid animate-rise grid-cols-[6.5rem_1fr] gap-4 rounded-xl border border-rule bg-sheet p-4 shadow-card"
            style={{ animationDelay: `${i * 90}ms` }}
          >
            <div className="space-y-2 border-r border-rule pr-3">
              <div className="skeleton h-3 w-10" />
              <div className="skeleton h-3 w-14" />
            </div>
            <div className="space-y-2">
              <div className="skeleton h-3.5 w-1/3" />
              <div className="skeleton h-3 w-full" />
              <div className="skeleton h-3 w-11/12" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (state.status === "error") {
    return (
      <div role="alert" className="animate-rise rounded-xl border border-danger/30 bg-sheet px-4 py-3 text-sm shadow-card">
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
        <div className="animate-rise py-10 text-center">
          <SearchX aria-hidden className="mx-auto mb-3 size-8 text-ink-4" />
          <p className="font-display text-2xl">No passages {props.identityName} can see match this.</p>
          <p className="mt-1 text-sm text-ink-3">Try naming a company, or turn on Rewrite in retrieval settings.</p>
        </div>
      ) : (
        <ol className="space-y-3">
          {result.hits.map((hit, i) => (
            <li key={hit.chunk_id} className="animate-rise" style={{ animationDelay: `${i * 60}ms` }}>
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
    <section className="relative grid gap-12 py-14 sm:py-20">
      <div aria-hidden className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
        <div className="absolute top-[-6rem] right-[8%] size-[30rem] animate-drift rounded-full bg-mark/60 blur-[90px]" />
        <div
          className="absolute top-[45%] left-[5%] size-[22rem] animate-drift rounded-full bg-pencil/12 blur-[90px]"
          style={{ animationDelay: "-9s" }}
        />
      </div>
      <div>
        <p className="inline-flex animate-rise items-center gap-2 rounded-full border border-rule bg-sheet/70 px-3 py-1 text-[13px] text-ink-2 shadow-card">
          <span className="relative flex size-2">
            <span className="absolute inset-0 animate-ping-soft rounded-full bg-ok" />
            <span className="relative size-2 rounded-full bg-ok" />
          </span>
          60 annual reports · 30 companies · live
        </p>
        <h1
          className="mt-6 max-w-2xl animate-rise font-display text-[2.7rem] leading-[1.03] tracking-tight sm:text-[3.8rem]"
          style={{ animationDelay: "80ms" }}
        >
          Ask the filings.
          <br />
          <span className="bg-gradient-to-r from-ink-2 via-mark-strong to-pencil bg-clip-text text-transparent italic">
            Check every figure.
          </span>
        </h1>
        <p className="mt-6 max-w-xl animate-rise text-[17px] text-ink-2" style={{ animationDelay: "160ms" }}>
          Answers are written from 60 annual reports and the numbers they report, and every figure is traced to the
          passage or data row it came from before you see it. What you can read depends on who you are: the database
          enforces it, not this page.
        </p>
        <div className="mt-8 flex animate-rise flex-wrap items-center gap-4" style={{ animationDelay: "240ms" }}>
          <AddIdentityButton />
          <span className="text-sm text-ink-3">You'll need an API key from the terminal.</span>
        </div>
      </div>
      <dl className="grid grid-cols-1 gap-3 sm:grid-cols-3">
        {PRINCIPLES.map(({ term, text, Icon }, i) => (
          <div
            key={term}
            className="lift animate-rise rounded-2xl border border-rule bg-sheet/80 p-5"
            style={{ animationDelay: `${320 + i * 90}ms` }}
          >
            <dt className="flex items-center gap-3">
              <span aria-hidden className="icon-tile size-9 rounded-xl">
                <Icon className="size-[18px]" />
              </span>
              <span className="font-display text-xl">{term}</span>
            </dt>
            <dd className="mt-3 text-sm text-ink-2">{text}</dd>
          </div>
        ))}
      </dl>
    </section>
  );
}

const PRINCIPLES = [
  {
    term: "Traced",
    text: "Each number is checked against the evidence it cites, and revised once if it isn't there.",
    Icon: BadgeCheck,
  },
  { term: "Scoped", text: "Row-level security in Postgres decides which companies each analyst can read.", Icon: ShieldCheck },
  { term: "Shown", text: "Every step, model call, token and cost behind an answer is laid out for inspection.", Icon: Eye },
];

// In the first eval run the best rerank score had a median of 0.99 for answerable questions
// and 0.14 for unanswerable ones. Below this line, say so instead of implying an answer.
// An uncalibrated hint; calibrated abstention is a later milestone.
const WEAK_EVIDENCE = 0.3;

function WeakEvidenceNotice({ result, identityName }: { result: SearchResult; identityName: string }) {
  const scores = result.hits.map((h) => h.rerank_score).filter((s): s is number => s !== null);
  if (!result.reranked || scores.length === 0 || Math.max(...scores) >= WEAK_EVIDENCE) return null;
  return (
    <div role="status" className="flex animate-rise gap-3 rounded-xl border border-rule bg-inset px-4 py-3 text-sm">
      <TriangleAlert aria-hidden className="mt-0.5 size-4 shrink-0 text-pencil" />
      <div>
      <p className="font-medium text-ink">These passages probably don't answer the question.</p>
      <p className="mt-0.5 text-ink-2">
        The best match scored {Math.max(...scores).toFixed(2)} for relevance. The answer may be in filings{" "}
        {identityName.split(" ")[0]} can't see, or not in any filing.
      </p>
      </div>
    </div>
  );
}
