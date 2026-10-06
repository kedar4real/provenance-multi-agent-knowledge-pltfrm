import { CornerDownRight } from "lucide-react";

import { ITEM_TITLES, type SearchResult } from "../lib/api";
import { formatMs } from "../lib/steps";
import { Chip } from "./ui";

// Stage order matches the pipeline; each gets a quiet shade so the bar reads as one object.
const STAGES: { key: string; label: string; shade: string }[] = [
  { key: "rewrite", label: "Rewrite", shade: "bg-ink-4" },
  { key: "embed", label: "Embed", shade: "bg-ink-2" },
  { key: "dense", label: "Dense", shade: "bg-ink-2" },
  { key: "bm25", label: "BM25", shade: "bg-ink-3" },
  { key: "fetch", label: "Fetch", shade: "bg-ink-3" },
  { key: "rerank", label: "Rerank", shade: "bg-mark-strong" },
];

export function ResultsSummary({ result }: { result: SearchResult }) {
  const stages = STAGES.filter((s) => (result.timings_ms[s.key] ?? 0) > 0);
  const total = stages.reduce((sum, s) => sum + (result.timings_ms[s.key] ?? 0), 0);
  const { tickers, fiscal_years, items } = result.filters;
  const hasFilters = tickers.length + fiscal_years.length + items.length > 0;

  return (
    <section aria-label="How this search ran" className="space-y-3 border-b border-rule pb-4">
      <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
        <p className="text-sm text-ink-2">
          <span className="font-medium text-ink tabular-nums">{result.hits.length}</span>{" "}
          {result.hits.length === 1 ? "passage" : "passages"}
          {result.reranked && " · reranked"}
        </p>
        <p className="font-mono text-[12px] text-ink-3 tabular-nums">{formatMs(total)} total</p>
      </div>

      {result.rewrite !== "off" && (
        <div className="flex items-start gap-2 text-sm">
          <CornerDownRight aria-hidden className="mt-0.5 size-3.5 shrink-0 text-ink-4" />
          {result.rewrite === "ok" ? (
            <p className="min-w-0 text-ink-2">
              Searched for <span className="font-serif text-[15px] text-ink italic">“{result.search_query}”</span>
              {hasFilters && (
                <span className="ml-2 inline-flex flex-wrap gap-1 align-middle">
                  {tickers.map((t) => (
                    <Chip key={t}>{t}</Chip>
                  ))}
                  {fiscal_years.map((y) => (
                    <Chip key={y}>FY{y}</Chip>
                  ))}
                  {items.map((i) => (
                    <Chip key={i}>{ITEM_TITLES[i] ?? `Item ${i}`}</Chip>
                  ))}
                </span>
              )}
              {result.filters_relaxed && (
                <span className="mt-1 block text-ink-3">
                  Nothing you can see matched those filters, so they were dropped.
                </span>
              )}
            </p>
          ) : (
            <p className="text-ink-3">Query rewriting was unavailable; searched your words as typed.</p>
          )}
        </div>
      )}

      {total > 0 && (
        <div>
          <div className="flex h-1.5 overflow-hidden rounded-full bg-inset" aria-hidden>
            {stages.map((s) => (
              <div
                key={s.key}
                className={`${s.shade} h-full border-r border-sheet last:border-r-0`}
                style={{ width: `${((result.timings_ms[s.key] ?? 0) / total) * 100}%` }}
              />
            ))}
          </div>
          <dl className="mt-2 flex flex-wrap gap-x-4 gap-y-1 font-mono text-[12px] text-ink-3">
            {stages.map((s) => (
              <div key={s.key} className="flex gap-1.5">
                <dt>{s.label}</dt>
                <dd className="text-ink-2 tabular-nums">{formatMs(result.timings_ms[s.key] ?? 0)}</dd>
              </div>
            ))}
          </dl>
        </div>
      )}
    </section>
  );
}
