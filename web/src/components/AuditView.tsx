import { CircleAlert, CircleCheck, FileWarning, Filter, ScrollText, ShieldBan, ShieldCheck } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { api, type AuditReport } from "../lib/api";
import { cn } from "../lib/cn";
import type { Identity } from "../lib/identities";
import { BarList, ChartFrame, StackedDays, StatTile } from "./charts";

// Status colours carry state and always appear with an icon and a label.
const OUTCOMES = [
  { key: "ok", label: "OK", color: "var(--color-ok)" },
  { key: "error", label: "Error", color: "var(--color-warn)" },
  { key: "denied", label: "Denied", color: "var(--color-danger)" },
];

function OutcomeBadge({ outcome }: { outcome: string }) {
  const Icon = outcome === "ok" ? CircleCheck : outcome === "denied" ? ShieldBan : CircleAlert;
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-medium",
        outcome === "ok" ? "bg-ok/12 text-ok" : "bg-danger/10 text-danger",
      )}
    >
      <Icon aria-hidden className="size-3" />
      {outcome}
    </span>
  );
}

/** For auditors: every tool call the agent made (who, which tool, a redacted preview of what
 *  for, the outcome), activity per day, and the passages quarantined as possible prompt
 *  injections. The database refuses this to anyone without the auditor group. */
export function AuditView({ identity, onOpenSource }: { identity: Identity; onOpenSource: (chunkId: number) => void }) {
  const [report, setReport] = useState<AuditReport | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [tool, setTool] = useState<string>("all");
  const [who, setWho] = useState<string>("all");

  useEffect(() => {
    const controller = new AbortController();
    api.audit(identity.key, controller.signal).then(setReport, (e: Error) => {
      if (!controller.signal.aborted) setError(e.message);
    });
    return () => controller.abort();
  }, [identity.key]);

  const daily = useMemo(() => {
    const days = new Map<string, Record<string, number>>();
    for (const d of report?.daily ?? []) {
      const row = days.get(d.day) ?? {};
      row[d.outcome] = (row[d.outcome] ?? 0) + d.calls;
      days.set(d.day, row);
    }
    // Fill the gaps so quiet days show as empty, not missing.
    const keys = [...days.keys()].sort();
    const out: string[] = [];
    if (keys.length) {
      const start = new Date(`${keys[0]}T00:00:00Z`);
      const end = new Date(`${keys.at(-1)}T00:00:00Z`);
      for (let d = start; d <= end; d = new Date(d.getTime() + 86_400_000)) out.push(d.toISOString().slice(0, 10));
    }
    return { days: out, counts: Object.fromEntries(days) };
  }, [report]);

  if (error) {
    return (
      <div className="flex animate-rise gap-4 rounded-2xl border border-rule bg-sheet p-5 shadow-card">
        <ShieldBan aria-hidden className="size-6 shrink-0 text-danger" />
        <div>
          <p className="font-display text-2xl">Audit log unavailable</p>
          <p className="mt-1 text-sm text-ink-2">{error}</p>
        </div>
      </div>
    );
  }
  if (!report) return <div className="skeleton h-64 rounded-2xl" aria-busy="true" />;

  const tools = [...new Set(report.entries.map((e) => e.tool))].sort();
  const people = [...new Set(report.entries.map((e) => e.principal))].sort();
  const entries = report.entries.filter((e) => (tool === "all" || e.tool === tool) && (who === "all" || e.principal === who));
  const errors = report.entries.filter((e) => e.outcome !== "ok").length;
  const byPrincipal = people.map((p) => ({ name: p, value: report.entries.filter((e) => e.principal === p).length }));

  return (
    <div className="space-y-5">
      <header>
        <h2 className="flex items-center gap-2.5 font-display text-[28px] leading-none">
          <span aria-hidden className="icon-tile size-9 rounded-xl">
            <ScrollText className="size-[18px]" />
          </span>
          Audit log
        </h2>
        <p className="mt-2 flex items-center gap-1.5 text-sm text-ink-3">
          <ShieldCheck aria-hidden className="size-4" />
          Append-only: the app can write it but never change it. Readable here only with the auditor group.
        </p>
      </header>

      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <StatTile label="Tool calls" value={report.entries.length.toLocaleString()} note="most recent 300" icon={<ScrollText className="size-4" />} />
        <StatTile label="Errors or denials" value={errors.toLocaleString()} note={`${report.entries.length ? Math.round((errors / report.entries.length) * 100) : 0}% of calls`} icon={<CircleAlert className="size-4" />} delay={60} />
        <StatTile label="Passages scanned" value={report.scanned.toLocaleString()} note="for prompt injection" icon={<ShieldCheck className="size-4" />} delay={120} />
        <StatTile label="Quarantined" value={report.flagged.toLocaleString()} note="withheld from answers" icon={<FileWarning className="size-4" />} delay={180} />
      </div>

      <div className="grid gap-4 lg:grid-cols-[2fr_1fr]">
        <ChartFrame
          title="Tool calls per day"
          subtitle="Last 14 days, by outcome"
          legend={OUTCOMES.map((o) => o.label)}
          legendColors={OUTCOMES.map((o) => o.color)}
          table={{ columns: ["day", ...OUTCOMES.map((o) => o.label)], rows: daily.days.map((d) => [d, ...OUTCOMES.map((o) => daily.counts[d]?.[o.key] ?? 0)]) }}
        >
          {daily.days.length ? (
            <StackedDays days={daily.days} outcomes={OUTCOMES} counts={daily.counts} />
          ) : (
            <p className="py-10 text-center text-sm text-ink-4">No tool calls in the last 14 days</p>
          )}
        </ChartFrame>
        <ChartFrame title="Calls by person" subtitle="In the recent entries" table={{ columns: ["principal", "calls"], rows: byPrincipal.map((r) => [r.name, r.value]) }}>
          <BarList label="Calls by person" rows={byPrincipal.sort((a, b) => b.value - a.value)} format={(v) => v.toLocaleString()} />
        </ChartFrame>
      </div>

      <section className="rounded-2xl border border-rule bg-sheet shadow-card">
        <header className="flex flex-wrap items-center gap-2 border-b border-rule px-4 py-3">
          <p className="mr-auto text-sm font-medium">Entries</p>
          <Filter aria-hidden className="size-3.5 text-ink-4" />
          <FilterSelect label="Tool" value={tool} options={tools} onChange={setTool} />
          <FilterSelect label="Person" value={who} options={people} onChange={setWho} />
        </header>
        <div className="max-h-[28rem] overflow-auto">
          <table className="greenbar w-full text-left text-[13px]">
            <thead className="smallcaps sticky top-0 bg-sheet text-ink-4">
              <tr>
                <th scope="col" className="px-4 py-2 font-medium">When</th>
                <th scope="col" className="px-2 py-2 font-medium">Who</th>
                <th scope="col" className="px-2 py-2 font-medium">Tool</th>
                <th scope="col" className="px-2 py-2 font-medium">Input (redacted)</th>
                <th scope="col" className="px-4 py-2 font-medium">Outcome</th>
              </tr>
            </thead>
            <tbody>
              {entries.map((e, i) => (
                <tr key={`${e.request_id}-${i}`} className="align-top">
                  <td className="px-4 py-2 font-mono text-[12px] whitespace-nowrap text-ink-3 tabular-nums">
                    {new Date(e.at).toLocaleString(undefined, { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })}
                  </td>
                  <td className="px-2 py-2 whitespace-nowrap">{e.principal}</td>
                  <td className="px-2 py-2 font-mono text-[12px]">{e.tool}</td>
                  <td className="max-w-[22rem] px-2 py-2 text-ink-2">
                    <span className="line-clamp-2">{e.input_preview}</span>
                  </td>
                  <td className="px-4 py-2">
                    <OutcomeBadge outcome={e.outcome} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {entries.length === 0 && <p className="py-8 text-center text-sm text-ink-4">No entries match</p>}
        </div>
      </section>

      <section className="rounded-2xl border border-rule bg-sheet shadow-card">
        <header className="flex items-center gap-2 border-b border-rule px-4 py-3">
          <FileWarning aria-hidden className="size-4 text-pencil" />
          <p className="text-sm font-medium">Quarantined passages</p>
          <p className="ml-auto text-[12px] text-ink-4">Flagged at ingest; never shown to the answer writer</p>
        </header>
        <ul className="divide-y divide-rule">
          {report.quarantined.map((q) => (
            <li key={q.chunk_id}>
              <button type="button" onClick={() => onOpenSource(q.chunk_id)} className="grid w-full grid-cols-[4.5rem_1fr_auto] gap-3 px-4 py-3 text-left hover:bg-inset">
                <span className="font-mono text-[12px] font-medium">
                  {q.ticker}
                  <span className="block font-normal text-ink-4">FY{q.fiscal_year}</span>
                </span>
                <span className="min-w-0">
                  <span className="line-clamp-2 text-[13px] text-ink-2">{q.preview}</span>
                  <span className="mt-1 flex flex-wrap gap-1">
                    {q.reasons.map((r) => (
                      <span key={r} className="rounded-full bg-danger/10 px-2 py-0.5 text-[11px] text-danger">
                        {r.replaceAll("_", " ")}
                      </span>
                    ))}
                  </span>
                </span>
                <span className="font-mono text-[12px] text-ink-3 tabular-nums">{q.score !== null ? q.score.toFixed(2) : "–"}</span>
              </button>
            </li>
          ))}
          {report.quarantined.length === 0 && <li className="px-4 py-6 text-center text-sm text-ink-4">Nothing quarantined in your sectors</li>}
        </ul>
      </section>
    </div>
  );
}

function FilterSelect({ label, value, options, onChange }: { label: string; value: string; options: string[]; onChange: (v: string) => void }) {
  return (
    <label className="inline-flex items-center gap-1.5 text-[12px] text-ink-3">
      {label}
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="rounded-lg border border-rule bg-sheet px-2 py-1 text-[12px] text-ink focus:border-pencil/50 focus:outline-none"
      >
        <option value="all">All</option>
        {options.map((o) => (
          <option key={o} value={o}>
            {o}
          </option>
        ))}
      </select>
    </label>
  );
}
