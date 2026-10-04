import { ITEM_TITLES, type Hit } from "../lib/api";
import { cn } from "../lib/cn";

interface Props {
  hit: Hit;
  rank: number;
  selected: boolean;
  onSelect: () => void;
}

/** One retrieved passage. The left rail is its provenance: where it came from and why it ranked. */
export function HitCard({ hit, rank, selected, onSelect }: Props) {
  const item = ITEM_TITLES[hit.item] ?? `Item ${hit.item}`;
  return (
    <article
      className={cn(
        "group relative grid grid-cols-1 gap-y-3 rounded-lg border bg-sheet p-4 transition-colors duration-100 sm:grid-cols-[6.5rem_1fr] sm:gap-x-4 sm:gap-y-0",
        selected ? "border-ink" : "border-rule hover:border-rule-strong",
      )}
    >
      <aside className="flex flex-wrap items-center gap-x-3 gap-y-1 border-b border-rule pb-2.5 text-[12px] sm:block sm:space-y-1.5 sm:border-r sm:border-b-0 sm:pr-3 sm:pb-0">
        <p className="font-mono font-medium text-ink tabular-nums">{hit.ticker}</p>
        <p className="font-mono text-ink-3 tabular-nums">FY{hit.fiscal_year}</p>
        <p className="text-ink-3">{item}</p>
        <Signals hit={hit} />
      </aside>

      <div className="min-w-0">
        <h3 className="flex items-baseline gap-2 text-sm">
          <span className="font-mono text-[12px] text-ink-4 tabular-nums" aria-label={`Result ${rank}`}>
            {String(rank).padStart(2, "0")}
          </span>
          {/* The whole card is clickable through this button's ::after; one tab stop per card. */}
          <button
            type="button"
            onClick={onSelect}
            aria-pressed={selected}
            className="text-left font-medium text-ink after:absolute after:inset-0 after:rounded-lg focus-visible:outline-none group-has-focus-visible:outline-2 group-has-focus-visible:outline-offset-2 group-has-focus-visible:outline-mark-strong"
          >
            {hit.company}
          </button>
        </h3>
        {isTable(hit.text) ? (
          <p className="mt-2 line-clamp-3 font-mono text-[13px] leading-relaxed text-ink-2 tabular-nums">
            <span className="mr-2 rounded border border-rule px-1 font-sans text-[11px] text-ink-3">table</span>
            {hit.text}
          </p>
        ) : (
          <p className="mt-2 line-clamp-4 font-serif text-[16px] leading-relaxed text-ink-2">{hit.text}</p>
        )}
      </div>
    </article>
  );
}

// Financial tables flatten into rows of numbers; prose typesetting makes them unreadable.
function isTable(text: string): boolean {
  const digits = text.replace(/[^0-9]/g, "").length;
  return digits / Math.max(text.length, 1) > 0.12;
}

function Signals({ hit }: { hit: Hit }) {
  return (
    <dl className="flex items-center gap-3 font-mono text-[11px] text-ink-4 sm:block sm:space-y-1 sm:pt-2">
      {hit.rerank_score !== null && (
        <div className="flex items-center gap-1.5 sm:block">
          <dt className="sr-only">Rerank relevance</dt>
          <dd className="contents sm:block">
            <div
              className="h-1 w-10 overflow-hidden rounded-full bg-inset sm:w-full"
              role="meter"
              aria-label="Rerank relevance"
              aria-valuemin={0}
              aria-valuemax={1}
              aria-valuenow={Number(hit.rerank_score.toFixed(2))}
            >
              <div className="h-full bg-mark-strong" style={{ width: `${Math.max(hit.rerank_score, 0.03) * 100}%` }} />
            </div>
            <span className="tabular-nums">{hit.rerank_score.toFixed(2)}</span>
          </dd>
        </div>
      )}
      <div className="flex gap-1">
        <dt>dense</dt>
        <dd className="tabular-nums">{hit.dense_rank ? `#${hit.dense_rank}` : "–"}</dd>
      </div>
      <div className="flex gap-1">
        <dt>bm25</dt>
        <dd className="tabular-nums">{hit.bm25_rank ? `#${hit.bm25_rank}` : "–"}</dd>
      </div>
    </dl>
  );
}
