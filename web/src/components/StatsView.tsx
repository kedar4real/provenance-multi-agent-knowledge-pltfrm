import { Activity, CircleGauge, Coins, Gauge, Layers, RefreshCw, Timer, Wallet, Zap } from "lucide-react";
import { useCallback, useEffect, useState } from "react";

import { api, type MetricsSnapshot, type Stats } from "../lib/api";
import type { Identity } from "../lib/identities";
import { BarList, ChartFrame, ColumnChart, Meter, StatTile } from "./charts";

const OUTCOMES: Record<string, string> = {
  answered: "Answered",
  cache_hit: "From cache",
  declined: "No answer in evidence",
  abstained: "Withheld (low confidence)",
};
const ROLES: Record<string, string> = {
  serve_small: "Small model",
  serve_large: "Large model",
  bulk: "Bulk (SQL, rewrite)",
  judge: "Judge",
};

const sum = (o: Record<string, number>) => Object.values(o).reduce((a, b) => a + b, 0);
const count = (n: number) => (n >= 10_000 ? `${(n / 1000).toFixed(1)}K` : Math.round(n).toLocaleString());

function since(ts: number): string {
  const s = Date.now() / 1000 - ts;
  if (s < 3600) return `${Math.max(1, Math.round(s / 60))} min`;
  if (s < 86400) return `${(s / 3600).toFixed(1)} h`;
  return `${(s / 86400).toFixed(1)} days`;
}

/** Median and 90th percentile from cumulative histogram buckets (upper bounds). */
function quantile(buckets: [number, number][], q: number): number | null {
  const total = buckets.at(-1)?.[1] ?? 0;
  if (!total) return null;
  const bound = buckets.find(([, cum]) => cum >= q * total)?.[0];
  return typeof bound === "number" && Number.isFinite(bound) ? bound : Infinity; // the +Inf bucket arrives as null
}

function within(bound: number | null, last: number): string {
  if (bound === null) return "–";
  return Number.isFinite(bound) ? `≤ ${bound} s` : `> ${last} s`;
}

/** Live numbers from the controller since the API started: how many questions, how the
 *  cache and routing behaved, tokens and API-equivalent cost, latency, and your budget. */
export function StatsView({ identity }: { identity: Identity }) {
  const [stats, setStats] = useState<Stats | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [updated, setUpdated] = useState<number>(0);

  const load = useCallback(
    (signal?: AbortSignal) =>
      api.stats(identity.key, signal).then(
        (s) => {
          setStats(s);
          setError(null);
          setUpdated(Date.now());
        },
        (e: Error) => {
          if (!signal?.aborted) setError(e.message);
        },
      ),
    [identity.key],
  );

  useEffect(() => {
    const controller = new AbortController();
    void load(controller.signal);
    const id = window.setInterval(() => void load(controller.signal), 10_000);
    return () => {
      controller.abort();
      window.clearInterval(id);
    };
  }, [load]);

  if (error) return <p className="text-sm text-danger">{error}</p>;
  if (!stats) {
    return (
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4" aria-busy="true">
        {[0, 1, 2, 3].map((i) => (
          <div key={i} className="skeleton h-28 rounded-2xl" />
        ))}
      </div>
    );
  }
  const m = stats.metrics;
  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h2 className="flex items-center gap-2.5 font-display text-[28px] leading-none">
            <span aria-hidden className="icon-tile size-9 rounded-xl">
              <Activity className="size-[18px]" />
            </span>
            Dashboard
          </h2>
          <p className="mt-2 text-sm text-ink-3">
            {m ? `Since the API started ${since(m.started_at)} ago` : "Metrics are off"} · refreshes every 10 s
          </p>
        </div>
        <button
          type="button"
          onClick={() => void load()}
          className="inline-flex items-center gap-1.5 rounded-lg border border-rule bg-sheet px-3 py-1.5 text-[13px] text-ink-2 shadow-card hover:text-ink"
        >
          <RefreshCw aria-hidden className="size-3.5" />
          {updated ? new Date(updated).toLocaleTimeString() : "Refresh"}
        </button>
      </header>
      {m ? <Body m={m} stats={stats} /> : null}
      {stats.budget && <BudgetCard spent={stats.budget.spent} limit={stats.budget.limit} who={identity.displayName} />}
    </div>
  );
}

function Body({ m, stats }: { m: MetricsSnapshot; stats: Stats }) {
  const byOutcome = Object.fromEntries(Object.entries(m.queries).map(([o, tiers]) => [o, sum(tiers)]));
  const total = sum(byOutcome);
  const hits = (m.cache_lookups.exact ?? 0) + (m.cache_lookups.semantic ?? 0);
  const lookups = hits + (m.cache_lookups.miss ?? 0);
  const tiers = { small: 0, large: 0 } as Record<string, number>;
  for (const t of Object.values(m.queries)) for (const [tier, n] of Object.entries(t)) tiers[tier] = (tiers[tier] ?? 0) + n;
  const tokens = Object.values(m.tokens).reduce((a, k) => a + (k.input ?? 0) + (k.output ?? 0), 0);
  const cost = sum(m.cost_usd);
  const lastBound = Math.max(0, ...m.latency_buckets.map(([b]) => (Number.isFinite(b) ? b : 0)));
  const p50 = quantile(m.latency_buckets, 0.5);
  const p90 = quantile(m.latency_buckets, 0.9);
  // Non-cumulative counts per latency bucket, for the histogram.
  const histogram = m.latency_buckets
    .filter(([bound]) => typeof bound === "number" && Number.isFinite(bound))
    .map(([bound, cum], i, all) => ({ bound, n: cum - (i ? (all[i - 1]?.[1] ?? 0) : 0) }));

  return (
    <>
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <StatTile label="Questions" value={count(total)} note={`${count(byOutcome.answered ?? 0)} answered`} icon={<Layers className="size-4" />} />
        <StatTile
          label="Cache hit rate"
          value={lookups ? `${Math.round((hits / lookups) * 100)}%` : "–"}
          note={`${count(hits)} of ${count(lookups)} lookups`}
          icon={<Zap className="size-4" />}
          delay={60}
        />
        <StatTile
          label="Tokens"
          value={count(tokens)}
          note={<>API-equivalent ${cost.toFixed(3)}</>}
          icon={<Coins className="size-4" />}
          delay={120}
        />
        <StatTile
          label="Typical answer time"
          value={within(p50, lastBound)}
          note={p90 !== null ? `90% ${within(p90, lastBound).replace("≤", "within")}` : "no answers yet"}
          icon={<Timer className="size-4" />}
          delay={180}
        />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <ChartFrame
          title="Outcomes"
          subtitle="What happened to each question"
          table={{ columns: ["outcome", "questions"], rows: Object.entries(byOutcome).map(([o, n]) => [OUTCOMES[o] ?? o, n]) }}
        >
          <BarList
            label="Questions by outcome"
            format={count}
            rows={Object.entries(byOutcome)
              .sort((a, b) => b[1] - a[1])
              .map(([o, n]) => ({ name: OUTCOMES[o] ?? o, value: n, tone: o === "abstained" ? "warn" : undefined }))}
          />
        </ChartFrame>
        <ChartFrame
          title="Routing"
          subtitle={`Which model tier answered${sum(m.escalations) ? ` · ${count(sum(m.escalations))} escalated` : ""}`}
          table={{ columns: ["tier", "questions"], rows: Object.entries(tiers).map(([t, n]) => [t, n]) }}
        >
          <BarList
            label="Questions by model tier"
            format={count}
            rows={[
              { name: "Small model", value: tiers.small ?? 0 },
              { name: "Large model", value: tiers.large ?? 0 },
              ...Object.entries(m.escalations).map(([r, n]) => ({ name: `Escalated: ${r.replaceAll("_", " ")}`, value: n, tone: "warn" as const })),
            ]}
          />
        </ChartFrame>
        <ChartFrame
          title="Tokens by role"
          subtitle="Input and output tokens per model role"
          legend={["Input", "Output"]}
          table={{
            columns: ["role", "input", "output", "API-equivalent $"],
            rows: Object.entries(m.tokens).map(([r, k]) => [ROLES[r] ?? r, k.input ?? 0, k.output ?? 0, (m.cost_usd[r] ?? 0).toFixed(4)]),
          }}
        >
          <ColumnChart
            label="Tokens by role"
            categories={Object.keys(m.tokens).map((r) => ROLES[r] ?? r)}
            series={[
              { name: "Input", values: Object.values(m.tokens).map((k) => k.input ?? 0) },
              { name: "Output", values: Object.values(m.tokens).map((k) => k.output ?? 0) },
            ]}
            format={count}
          />
        </ChartFrame>
        <ChartFrame
          title="Answer time"
          subtitle={`Questions per latency bucket · mean ${(m.latency_sum_s / Math.max(total, 1)).toFixed(1)} s`}
          table={{ columns: ["up to (s)", "questions"], rows: histogram.map((h) => [h.bound, h.n]) }}
        >
          <ColumnChart
            label="Questions"
            categories={histogram.map((h) => `≤${h.bound}s`)}
            series={[{ name: "Questions", values: histogram.map((h) => h.n) }]}
            format={count}
            integer
          />
        </ChartFrame>
      </div>

      <div className="flex flex-wrap gap-3 text-[13px]">
        <span className="inline-flex items-center gap-2 rounded-full border border-rule bg-sheet px-3 py-1.5 shadow-card">
          <Gauge aria-hidden className="size-4 text-ink-3" />
          {m.running} running · {m.waiting} queued
        </span>
        {sum(m.shed) > 0 && (
          <span className="inline-flex items-center gap-2 rounded-full border border-rule bg-sheet px-3 py-1.5 shadow-card">
            <CircleGauge aria-hidden className="size-4 text-pencil" />
            {count(sum(m.shed))} refused (budget or overload)
          </span>
        )}
        <span className="inline-flex items-center gap-2 rounded-full border border-rule bg-sheet px-3 py-1.5 shadow-card">
          <span className={`size-2 rounded-full ${stats.breakers_open.length ? "bg-danger" : "bg-ok"}`} />
          {stats.breakers_open.length ? `Paused providers: ${stats.breakers_open.join(", ")}` : "All model providers available"}
        </span>
      </div>
    </>
  );
}

function BudgetCard({ spent, limit, who }: { spent: number; limit: number; who: string }) {
  const share = limit ? spent / limit : 0;
  return (
    <section className="animate-rise rounded-2xl border border-rule bg-sheet p-4 shadow-card">
      <p className="mb-3 flex items-center justify-between gap-3 text-sm">
        <span className="flex items-center gap-2 font-medium">
          <Wallet aria-hidden className="size-4 text-ink-3" />
          {who.split(" ")[0]}'s token budget today
        </span>
        <span className="font-mono text-[13px] text-ink-2 tabular-nums">
          {spent.toLocaleString()} / {limit.toLocaleString()} ({Math.round(share * 100)}%)
        </span>
      </p>
      <Meter value={spent} max={limit} label="Tokens used today" />
      <p className="mt-2 text-[12px] text-ink-4">Resets at midnight UTC. Questions are refused (HTTP 429) once it's spent.</p>
    </section>
  );
}
