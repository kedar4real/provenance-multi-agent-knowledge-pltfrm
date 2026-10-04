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
        "group relative grid grid-cols-[4.5rem_1fr] gap-x-4 rounded-lg border bg-sheet p-4 transition-colors duration-100 sm:grid-cols-[6.5rem_1fr]",
        selected ? "border-ink" : "border-rule hover:border-rule-strong",
      )}
    >
      <aside className="space-y-1.5 border-r border-rule pr-3 text-[12px]">
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
            {hit.company} <span className="font-normal text-ink-3">· {item}</span>
          </button>
        </h3>
        <p className="mt-2 line-clamp-5 font-serif text-[16px] leading-relaxed text-ink-2">{hit.text}</p>
      </div>
    </article>
  );
}

function Signals({ hit }: { hit: Hit }) {
  return (
    <dl className="space-y-1 pt-2 font-mono text-[11px] text-ink-4">
      {hit.rerank_score !== null && (
        <div>
          <dt className="sr-only">Rerank relevance</dt>
          <dd>
            <div
              className="h-1 w-full overflow-hidden rounded-full bg-inset"
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
