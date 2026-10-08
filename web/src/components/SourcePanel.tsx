import { BookOpen, ExternalLink, Globe, Hash, Layers, X } from "lucide-react";
import { useEffect, useState } from "react";

import { api, ApiError, ITEM_TITLES, type Source } from "../lib/api";

interface Props {
  apiKey: string;
  chunkId: number;
  onClose: () => void;
  /** Rendered inside a dialog on small screens, which supplies its own title element. */
  titleAs?: React.ElementType;
}

type State = { status: "loading" } | { status: "ready"; source: Source } | { status: "error"; message: string };

export function SourcePanel({ apiKey, chunkId, onClose, titleAs: Title = "h2" }: Props) {
  const [state, setState] = useState<State>({ status: "loading" });

  // Fetching is a side effect tied to which passage is open, so it lives in an effect.
  useEffect(() => {
    const controller = new AbortController();
    setState({ status: "loading" });
    api
      .source(apiKey, chunkId, controller.signal)
      .then((source) => setState({ status: "ready", source }))
      .catch((e: unknown) => {
        if (controller.signal.aborted) return;
        const message =
          e instanceof ApiError && e.status === 404
            ? "This passage isn't available to the current identity."
            : (e as Error).message;
        setState({ status: "error", message });
      });
    return () => controller.abort();
  }, [apiKey, chunkId]);

  return (
    <div className="flex h-full flex-col">
      <header className="flex items-start justify-between gap-3 border-b border-rule px-5 py-4">
        <span aria-hidden className="icon-tile size-10 rounded-xl">
          <BookOpen className="size-5" />
        </span>
        <div className="min-w-0 flex-1">
          <p className="smallcaps text-pencil">Source exhibit</p>
          <Title className="mt-1 truncate font-display text-[22px] leading-tight">
            {state.status === "ready"
              ? `${state.source.company} · 10-K FY${state.source.fiscal_year}`
              : "Loading passage…"}
          </Title>
        </div>
        <button
          type="button"
          onClick={onClose}
          aria-label="Close source"
          className="-m-1 grid size-8 place-items-center rounded-full text-ink-3 transition-[background-color,transform] hover:rotate-90 hover:bg-inset hover:text-ink"
        >
          <X aria-hidden className="size-4" />
        </button>
      </header>

      {state.status === "loading" && <SourceSkeleton />}
      {state.status === "error" && (
        <p role="alert" className="px-5 py-6 text-sm text-danger">
          {state.message}
        </p>
      )}
      {state.status === "ready" && <SourceBody source={state.source} />}
    </div>
  );
}

function SourceBody({ source }: { source: Source }) {
  const before = source.text.slice(0, source.highlight_start);
  const cited = source.text.slice(source.highlight_start, source.highlight_end);
  const after = source.text.slice(source.highlight_end);
  const truncatedStart = source.window_start > 0;
  const truncatedEnd = source.window_start + source.text.length < source.section_length;

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <dl className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-1 border-b border-rule px-5 py-3 text-[13px]">
        <dt className="smallcaps flex items-center gap-1.5 pt-0.5 text-ink-4"><Layers aria-hidden className="size-3" />Section</dt>
        <dd>
          Item {source.item} · {ITEM_TITLES[source.item] ?? source.section_title}
        </dd>
        <dt className="smallcaps flex items-center gap-1.5 pt-0.5 text-ink-4"><Hash aria-hidden className="size-3" />Accession</dt>
        <dd className="font-mono text-[12px] tabular-nums">{source.accession}</dd>
        <dt className="smallcaps flex items-center gap-1.5 pt-0.5 text-ink-4"><Globe aria-hidden className="size-3" />Filing</dt>
        <dd>
          <a
            href={source.url}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1 underline decoration-pencil/50 underline-offset-2 hover:decoration-pencil"
          >
            Open on sec.gov
            <ExternalLink aria-hidden className="size-3" />
            <span className="sr-only">(opens in a new tab)</span>
          </a>
        </dd>
      </dl>
      <div className="relative min-h-0 flex-1 overflow-y-auto px-5 py-5">
        <p className="font-serif text-[17px] leading-[1.7] whitespace-pre-line text-ink-3">
          {truncatedStart && <span aria-hidden>… </span>}
          {before}
          <mark
            ref={centerInScroller}
            className="evidence"
            aria-label="Cited passage"
          >
            {cited}
          </mark>
          {after}
          {truncatedEnd && <span aria-hidden> …</span>}
        </p>
      </div>
    </div>
  );
}

// scrollIntoView would also scroll the page behind the panel; move only the panel.
function centerInScroller(mark: HTMLElement | null): void {
  const scroller = mark?.closest<HTMLElement>(".overflow-y-auto");
  if (!mark || !scroller) return;
  scroller.scrollTop = Math.max(mark.offsetTop - scroller.clientHeight / 3, 0);
}

function SourceSkeleton() {
  return (
    <div className="space-y-3 px-5 py-6" aria-busy="true" aria-label="Loading passage">
      {[92, 100, 85, 97, 60].map((w, i) => (
        <div key={i} className="skeleton h-3.5" style={{ width: `${w}%` }} />
      ))}
    </div>
  );
}
