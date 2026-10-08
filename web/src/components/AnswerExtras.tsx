import { ArrowUpRight, ChartColumn, Download, Printer, Quote, X } from "lucide-react";
import type { ReactNode } from "react";

import type { AgentResult, Evidence } from "../lib/api";
import type { Identity } from "../lib/identities";
import { ChartFrame, ColumnChart, MAX_SERIES } from "./charts";

const CITATION = /\[((?:[PF]\d+)(?:\s*,\s*[PF]\d+)*)\]/g;
const NUMBER = /\$?\d{1,3}(?:,\d{3})+(?:\.\d+)?%?|\$?\d+(?:\.\d+)?%?/g;

function citations(text: string): string[] {
  return [...new Set([...text.matchAll(CITATION)].flatMap((m) => (m[1] ?? "").split(",").map((s) => s.trim())))];
}

function digits(n: string): string {
  return n.replace(/[$,%]/g, "");
}

/** True when an evidence number is the claim's number, as written or scaled: a data row's
 *  31370000000.0 is the answer's "$31.37 billion"; 0.062 can be "6.2%". */
function sameNumber(evidence: number, claim: number): boolean {
  const close = (a: number, b: number) => Math.abs(a - b) <= Math.max(Math.abs(b) * 0.005, 0.005);
  return [1, 1e3, 1e6, 1e9, 1e12, 0.01].some((scale) => close(evidence / scale, claim));
}

/** Highlights, in an evidence text, the numbers that also appear in the claim. */
function highlightNumbers(text: string, wanted: Set<string>): ReactNode[] {
  if (wanted.size === 0) return [text];
  const claims = [...wanted].map(Number).filter((n) => Number.isFinite(n) && !(n >= 1900 && n <= 2100 && Number.isInteger(n)));
  const parts: ReactNode[] = [];
  let last = 0;
  for (const m of text.matchAll(NUMBER)) {
    const value = Number(digits(m[0]));
    if (!claims.some((c) => sameNumber(value, c))) continue;
    const at = m.index ?? 0;
    parts.push(text.slice(last, at), <mark key={at} className="evidence">{m[0]}</mark>);
    last = at + m[0].length;
  }
  parts.push(text.slice(last));
  return parts;
}

/** One sentence of the answer, and the evidence it cites: the passages (with the sentence's
 *  numbers highlighted where they occur) or data rows, and the claim's calibrated confidence
 *  when a calibrator has scored it. */
export function ClaimInspector({
  sentence,
  result,
  onOpen,
  onClose,
}: {
  sentence: string;
  result: AgentResult;
  onOpen: (id: string) => void;
  onClose: () => void;
}) {
  const ids = citations(sentence);
  const byId = new Map(result.evidence.map((e) => [e.id, e]));
  const cited = ids.map((id) => byId.get(id)).filter((e): e is Evidence => Boolean(e));
  const numbers = new Set(
    [...sentence.replace(CITATION, "").matchAll(NUMBER)].map((m) => digits(m[0])).filter((d) => d.length > 1),
  );
  const plain = sentence.replace(CITATION, "").replaceAll("**", "").replace(/\s+([.,;:])/g, "$1").trim();
  const scored = result.claims.find(
    (c) => c.confidence !== null && (plain.includes(c.text.trim()) || c.text.includes(plain.slice(0, 60))),
  );
  return (
    <section
      aria-label="Evidence for the selected sentence"
      className="animate-rise rounded-2xl border border-mark-strong/40 bg-sheet p-4 shadow-lift"
    >
      <header className="flex items-start gap-3">
        <span aria-hidden className="icon-tile size-8 rounded-lg">
          <Quote className="size-4" />
        </span>
        <div className="min-w-0 flex-1">
          <p className="text-[13px] text-ink-3">Selected claim</p>
          <p className="font-serif text-[16px] text-ink">{plain}</p>
          <p className="mt-1 flex flex-wrap gap-x-3 text-[12px] text-ink-3">
            <span>
              {cited.length === 0 ? "Cites no evidence" : `Cites ${cited.map((e) => e.id).join(", ")}`}
            </span>
            {scored?.confidence != null && (
              <span>
                Confidence <span className="font-mono text-ink">{Math.round(scored.confidence * 100)}%</span>
              </span>
            )}
            {numbers.size > 0 && <span>Numbers found in the evidence are highlighted</span>}
          </p>
        </div>
        <button
          type="button"
          onClick={onClose}
          aria-label="Close"
          className="grid size-7 place-items-center rounded-full text-ink-3 hover:bg-inset hover:text-ink"
        >
          <X aria-hidden className="size-4" />
        </button>
      </header>
      <ul className="mt-3 space-y-2">
        {cited.map((e) => (
          <li key={e.id} className="rounded-xl border border-rule bg-paper/60 px-3 py-2.5">
            <p className="flex items-center justify-between gap-2 text-[12px] text-ink-3">
              <span>
                <span className="mr-2 font-mono font-medium text-mark-ink">{e.id}</span>
                {e.label}
              </span>
              {e.kind === "passage" && (
                <button
                  type="button"
                  onClick={() => onOpen(e.id)}
                  className="inline-flex items-center gap-1 rounded-md px-1.5 py-0.5 text-ink-2 hover:bg-inset hover:text-ink"
                >
                  In the filing <ArrowUpRight aria-hidden className="size-3.5" />
                </button>
              )}
            </p>
            <p className={e.kind === "fact" ? "mt-1 font-mono text-[12px] text-ink-2" : "mt-1 line-clamp-5 font-serif text-[15px] text-ink-2"}>
              {highlightNumbers(e.text, numbers)}
            </p>
          </li>
        ))}
      </ul>
    </section>
  );
}

// ---- Chart of the financial data behind a numeric answer --------------------------------

function pick(columns: string[], test: (c: string) => boolean): number {
  return columns.findIndex((c) => test(c.toLowerCase()));
}

function compact(v: number): string {
  const abs = Math.abs(v);
  if (abs >= 1e9) return `$${(v / 1e9).toFixed(abs >= 1e11 ? 0 : 1)}B`;
  if (abs >= 1e6) return `$${(v / 1e6).toFixed(abs >= 1e8 ? 0 : 1)}M`;
  if (abs >= 1e3) return v.toLocaleString(undefined, { maximumFractionDigits: 0 });
  return v.toLocaleString(undefined, { maximumFractionDigits: 2 });
}

/** When the answer used financial data with one metric across companies and/or years, chart
 *  it. Mixed metrics (different units) aren't charted; the table under Exhibits has them. */
export function AnswerChart({ result }: { result: AgentResult }) {
  const sql = result.sql;
  if (!sql || sql.rows.length < 2) return null;
  const cols = sql.columns;
  const value = pick(cols, (c) => /value|amount|total|revenue|income|spend|usd|expense/.test(c) && !/year|unit/.test(c));
  const year = pick(cols, (c) => /fiscal_year|year|period/.test(c));
  const who = pick(cols, (c) => /ticker|company|name/.test(c));
  const metric = pick(cols, (c) => /metric|concept|tag|label/.test(c));
  const valueIdx = value >= 0 ? value : cols.findIndex((_, i) => i !== year && sql.rows.every((r) => typeof r[i] === "number"));
  if (valueIdx < 0) return null;
  if (metric >= 0 && new Set(sql.rows.map((r) => String(r[metric]))).size > 1) return null;

  const rows = sql.rows.filter((r) => typeof r[valueIdx] === "number");
  const seriesNames = who >= 0 ? [...new Set(rows.map((r) => String(r[who])))] : ["Value"];
  const categories =
    year >= 0
      ? [...new Set(rows.map((r) => String(r[year])))].sort()
      : who >= 0
        ? seriesNames
        : rows.map((_, i) => String(i + 1));
  if (categories.length < 1 || rows.length < 2) return null;
  const byCategoryOnly = year < 0;
  const series = byCategoryOnly
    ? [{ name: metric >= 0 ? String(rows[0]?.[metric]) : "Value", values: categories.map((c) => Number(rows.find((r) => String(r[who]) === c)?.[valueIdx] ?? null)) }]
    : seriesNames.slice(0, MAX_SERIES).map((name) => ({
        name,
        values: categories.map((c) => {
          const row = rows.find((r) => String(r[year]) === c && (who < 0 || String(r[who]) === name));
          return row ? Number(row[valueIdx]) : null;
        }),
      }));
  const title = metric >= 0 ? String(rows[0]?.[metric]).replaceAll("_", " ") : cols[valueIdx]?.replaceAll("_", " ") ?? "Value";

  return (
    <ChartFrame
      className="animate-rise"
      title={
        <span className="flex items-center gap-2">
          <ChartColumn aria-hidden className="size-4 text-ink-3" />
          {title}
        </span>
      }
      subtitle={`From the reported financial data the answer cites${seriesNames.length > MAX_SERIES ? ` (first ${MAX_SERIES} companies; all in the table)` : ""}`}
      legend={byCategoryOnly ? undefined : series.map((s) => s.name)}
      table={{ columns: cols.map((c) => c.replaceAll("_", " ")), rows: sql.rows.map((r) => r.map((v) => (typeof v === "number" ? compact(v) : String(v ?? "–")))) }}
    >
      <ColumnChart categories={categories.map((c) => (year >= 0 && /^\d{4}$/.test(c) ? `FY${c}` : c))} series={series} format={compact} label={title} />
    </ChartFrame>
  );
}

// ---- Export ------------------------------------------------------------------------------

function toMarkdown(result: AgentResult, identity: Identity): string {
  const v = result.verification;
  const lines = [
    `# ${result.question}`,
    "",
    `*Answered by provenance for ${identity.displayName} on ${new Date().toLocaleString()}.*`,
    "",
    `- Verification: ${v ? (v.ok ? "every number traced to cited evidence" : "failed") : "not run"}`,
    result.confidence !== null ? `- Confidence (weakest claim): ${Math.round(result.confidence * 100)}%` : "",
    result.control ? `- Model tier: ${result.control.tier}; tokens: ${result.control.usage.input_tokens + result.control.usage.output_tokens}` : "",
    "",
    "## Answer",
    "",
    result.answer,
    "",
    "## Evidence",
    "",
    ...result.evidence.map((e) => `**[${e.id}]** ${e.label}\n\n> ${e.text.replace(/\n+/g, " ")}\n`),
  ];
  return lines.filter((l, i, all) => !(l === "" && all[i - 1] === "")).join("\n");
}

export function ExportButtons({ result, identity }: { result: AgentResult; identity: Identity }) {
  const download = () => {
    const blob = new Blob([toMarkdown(result, identity)], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `provenance-${result.question.slice(0, 40).replace(/[^a-z0-9]+/gi, "-").toLowerCase()}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };
  const button = "grid size-8 place-items-center rounded-lg text-ink-3 transition-colors hover:bg-inset hover:text-ink";
  return (
    <>
      <button type="button" onClick={download} className={button} title="Download as Markdown" aria-label="Download as Markdown">
        <Download aria-hidden className="size-4" />
      </button>
      <button type="button" onClick={() => window.print()} className={button} title="Print or save as PDF" aria-label="Print or save as PDF">
        <Printer aria-hidden className="size-4" />
      </button>
    </>
  );
}
