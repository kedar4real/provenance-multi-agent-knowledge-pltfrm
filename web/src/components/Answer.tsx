import {
  Check,
  CircleAlert,
  Coins,
  Copy,
  Cpu,
  FileCheck,
  FileText,
  Gauge,
  MousePointerClick,
  SearchX,
  Table2,
  Zap,
} from "lucide-react";
import { Fragment, useState, type ReactNode } from "react";

import type { AgentResult, Evidence } from "../lib/api";
import { cn } from "../lib/cn";
import type { Identity } from "../lib/identities";
import type { TimedStep } from "../lib/useAgentRun";
import { AnswerChart, ClaimInspector, ExportButtons } from "./AnswerExtras";
import { verificationProblem } from "./Steps";
import { TracePanel } from "./TracePanel";

// ---- Answer -----------------------------------------------------------------------------

const CITATION = /\[((?:[PF]\d+)(?:\s*,\s*[PF]\d+)*)\]/g;

export function AnswerView({
  result,
  elapsedMs,
  identity,
  onOpenSource,
  steps,
  compact = false,
}: {
  result: AgentResult;
  elapsedMs: number;
  identity: Identity;
  onOpenSource: (id: number) => void;
  /** Steps with arrival times, for the timing chart; omitted for stored answers. */
  steps?: TimedStep[];
  /** Side-by-side comparison: the answer, its chart and claims, without the trace. */
  compact?: boolean;
}) {
  const [focusedFact, setFocusedFact] = useState<string | null>(null);
  const [claim, setClaim] = useState<string | null>(null);
  const byId = new Map(result.evidence.map((e) => [e.id, e]));

  if (result.control?.abstained) {
    return (
      <article className="space-y-5">
        <div className="animate-rise rounded-2xl border border-pencil/30 bg-sheet px-5 py-4 shadow-card">
          <p className="stamp mb-3 text-pencil">Withheld</p>
          <p className="font-display text-2xl">Not confident enough to answer.</p>
          <p className="mt-1 text-sm text-ink-2">
            A draft was written, but its weakest claim scored {Math.round((result.confidence ?? 0) * 100)}% confidence.
            Rather than risk a wrong answer, here is what was found, so you can read it yourself.
          </p>
        </div>
        <RunSummary result={result} />
        {!compact && <TracePanel result={result} elapsedMs={elapsedMs} steps={steps} />}
        <EvidenceList
          evidence={result.evidence}
          cited={new Set()}
          sql={result.sql}
          focused={null}
          onOpen={(id) => {
            const evidence = byId.get(id);
            if (evidence?.kind === "passage" && evidence.chunk_id !== null) onOpenSource(evidence.chunk_id);
          }}
        />
      </article>
    );
  }

  if (result.declined) {
    return (
      <div className="flex animate-rise gap-4 rounded-2xl border border-rule bg-sheet px-5 py-4 shadow-card">
        <span aria-hidden className="icon-tile size-10 rounded-xl">
          <SearchX className="size-5" />
        </span>
        <div>
          <p className="font-display text-2xl">No answer from the evidence.</p>
          <p className="mt-1 text-sm text-ink-2">
            Nothing {identity.displayName.split(" ")[0]} can see answers this. It may be in filings outside their
            access, or in no filing at all.
          </p>
        </div>
      </div>
    );
  }

  const openCitation = (id: string) => {
    const evidence = byId.get(id);
    if (evidence?.kind === "passage" && evidence.chunk_id !== null) onOpenSource(evidence.chunk_id);
    if (evidence?.kind === "fact") {
      setFocusedFact(id);
      document.getElementById(`evidence-${id}`)?.scrollIntoView({ block: "nearest", behavior: "smooth" });
    }
  };
  const pickClaim = (sentence: string) => setClaim((cur) => (cur === sentence ? null : sentence));

  return (
    <article className="space-y-5" data-print-root>
      <header className="flex animate-rise flex-wrap items-center justify-between gap-x-4 gap-y-3 border-b border-rule pb-3">
        <h2 className="flex items-center gap-2.5 font-display text-[28px] leading-none">
          <span aria-hidden className="icon-tile size-9 rounded-xl">
            <FileCheck className="size-[18px]" />
          </span>
          Answer
        </h2>
        <div className="flex flex-wrap items-center gap-3">
          <ConfidenceBadge confidence={result.confidence} />
          <VerificationBadge result={result} />
          {!compact && (
            <span className="flex items-center print:hidden">
              <CopyButton text={result.answer} />
              <ExportButtons result={result} identity={identity} />
            </span>
          )}
        </div>
      </header>
      <RunSummary result={result} />
      <p className="flex items-center gap-1.5 text-[12px] text-ink-4 print:hidden">
        <MousePointerClick aria-hidden className="size-3.5" />
        Click a sentence to see the evidence behind it.
      </p>
      <div className="space-y-3 font-serif text-[18.5px] leading-[1.72] text-ink">
        {renderAnswer(result.answer, byId, openCitation, claim, pickClaim)}
      </div>
      {claim && (
        <ClaimInspector
          sentence={claim}
          result={result}
          onOpen={openCitation}
          onClose={() => setClaim(null)}
        />
      )}
      <AnswerChart result={result} />
      <ClaimConfidence claims={result.claims} />
      {!compact && <TracePanel result={result} elapsedMs={elapsedMs} steps={steps} />}
      {!compact && (
        <EvidenceList
          evidence={result.evidence}
          cited={citedIds(result.answer)}
          sql={result.sql}
          focused={focusedFact}
          onOpen={openCitation}
        />
      )}
    </article>
  );
}

/** Splits a paragraph into sentences, keeping each sentence's trailing citations with it. */
export function sentences(line: string): string[] {
  return line.split(/(?<=[.!?](?:\s*\[[PF]\d+(?:\s*,\s*[PF]\d+)*\])*)\s+(?=[A-Z"\u201c(])/).filter(Boolean);
}

/** Paragraphs and "*"/"-" bullet lists, the only markdown the models produce here. Each
 *  sentence is clickable: it opens the claim inspector. */
function renderAnswer(
  text: string,
  byId: Map<string, Evidence>,
  onOpen: (id: string) => void,
  selected: string | null,
  onPick: (sentence: string) => void,
): ReactNode[] {
  const blocks: ReactNode[] = [];
  let bullets: string[] = [];
  const line = (body: string) =>
    sentences(body).map((sentence, i) => (
      <Fragment key={i}>
        {i > 0 && " "}
        <span
          role="button"
          tabIndex={0}
          aria-pressed={selected === sentence}
          onClick={() => onPick(sentence)}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === " ") {
              e.preventDefault();
              onPick(sentence);
            }
          }}
          className={cn(
            "cursor-pointer rounded-sm transition-colors duration-150 [box-decoration-break:clone] hover:bg-mark/35 focus-visible:outline-2",
            selected === sentence && "bg-mark/60",
          )}
        >
          {renderWithCitations(sentence, byId, onOpen)}
        </span>
      </Fragment>
    ));
  const flush = () => {
    if (!bullets.length) return;
    blocks.push(
      <ul
        key={`ul-${blocks.length}`}
        className="animate-rise list-disc space-y-1 pl-6 marker:text-pencil"
        style={{ animationDelay: `${120 + blocks.length * 90}ms` }}
      >
        {bullets.map((b, i) => (
          <li key={i}>{line(b)}</li>
        ))}
      </ul>,
    );
    bullets = [];
  };
  let table: string[][] = [];
  const flushTable = () => {
    if (!table.length) return;
    const [head, ...body] = table;
    blocks.push(
      <div
        key={`t-${blocks.length}`}
        className="animate-rise overflow-x-auto rounded-xl border border-rule bg-sheet font-sans text-[14px] leading-normal shadow-card"
        style={{ animationDelay: `${120 + blocks.length * 90}ms` }}
      >
        <table className="greenbar w-full text-left">
          <thead className="border-b border-rule-strong text-ink-3">
            <tr>
              {(head ?? []).map((cell, i) => (
                <th key={i} scope="col" className="px-3 py-2 font-medium">
                  {renderWithCitations(cell, byId, onOpen)}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="tabular-nums">
            {body.map((row, r) => (
              <tr key={r}>
                {row.map((cell, i) => (
                  <td key={i} className="px-3 py-1.5">
                    {renderWithCitations(cell, byId, onOpen)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>,
    );
    table = [];
  };
  for (const raw of text.split("\n")) {
    const trimmed = raw.trim();
    // Markdown tables: rows of |cells|; the |---|---| divider is dropped.
    if (/^\|.*\|$/.test(trimmed)) {
      flush();
      if (!/^\|[\s:|-]+\|$/.test(trimmed)) table.push(trimmed.slice(1, -1).split("|").map((c) => c.trim()));
      continue;
    }
    flushTable();
    const bullet = /^[*-]\s+(.*)$/.exec(trimmed);
    if (bullet) {
      bullets.push(bullet[1] ?? "");
      continue;
    }
    flush();
    // A heading (#...) or a line that is wholly bold reads as a subheading, not a claim.
    const heading = /^#{1,4}\s+(.*)$/.exec(trimmed)?.[1] ?? /^\*\*([^*]+)\*\*:?$/.exec(trimmed)?.[1];
    if (heading) {
      blocks.push(
        <h3
          key={`h-${blocks.length}`}
          className="animate-rise pt-1 font-sans text-[15px] font-semibold text-ink"
          style={{ animationDelay: `${120 + blocks.length * 90}ms` }}
        >
          {heading}
        </h3>,
      );
      continue;
    }
    if (trimmed)
      blocks.push(
        <p key={`p-${blocks.length}`} className="animate-rise" style={{ animationDelay: `${120 + blocks.length * 90}ms` }}>
          {line(trimmed)}
        </p>,
      );
  }
  flush();
  flushTable();
  return blocks;
}

function renderWithCitations(text: string, byId: Map<string, Evidence>, onOpen: (id: string) => void): ReactNode[] {
  const parts: ReactNode[] = [];
  let last = 0;
  for (const match of text.matchAll(CITATION)) {
    parts.push(...renderBold(text.slice(last, match.index), match.index ?? 0));
    const ids = (match[1] ?? "").split(",").map((s) => s.trim());
    parts.push(
      <Fragment key={match.index}>
        {ids.map((id) => (
          <button
            key={id}
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              onOpen(id);
            }}
            disabled={!byId.has(id)}
            aria-label={`Source ${id}: ${byId.get(id)?.label ?? "missing"}`}
            className="mx-0.5 inline-flex -translate-y-[0.35em] items-center rounded-md bg-mark/70 px-1.5 align-baseline font-mono text-[11px] leading-[1.5] font-medium text-mark-ink ring-1 ring-mark-strong/40 transition-[background-color,transform,box-shadow] duration-150 hover:-translate-y-[0.5em] hover:bg-mark hover:text-ink hover:shadow-card disabled:bg-transparent disabled:text-danger disabled:ring-danger/50"
          >
            {id}
          </button>
        ))}
      </Fragment>,
    );
    last = (match.index ?? 0) + match[0].length;
  }
  parts.push(...renderBold(text.slice(last), last));
  return parts;
}

function renderBold(text: string, keyBase: number): ReactNode[] {
  return text.split(/\*\*(.+?)\*\*/g).map((part, i) =>
    i % 2 ? (
      <strong key={`${keyBase}-${i}`} className="font-semibold">
        {part}
      </strong>
    ) : (
      part
    ),
  );
}

/** Which model answered, whether it came from the cache, and what it would have cost. */
function RunSummary({ result }: { result: AgentResult }) {
  const c = result.control;
  if (!c) return null;
  const tokens = c.usage.input_tokens + c.usage.output_tokens;
  const item = "inline-flex items-center gap-1.5 rounded-full bg-inset px-2.5 py-1";
  return (
    <p
      className="flex animate-rise flex-wrap gap-2 font-mono text-[12px] text-ink-3 tabular-nums"
      title="API-equivalent cost: tokens priced at Claude Haiku (small) and Sonnet (large) list prices. The real calls ran on free tiers."
    >
      {c.cache?.hit ? (
        <span className={item}>
          <Zap aria-hidden className="size-3.5 text-ok" />
          From an earlier answer
        </span>
      ) : (
        <>
          <span className={item}>
            <Cpu aria-hidden className="size-3.5" />
            {c.tier === "small" ? "Small" : "Large"} model{c.escalated && " · escalated"}
          </span>
          <span className={item}>
            <Coins aria-hidden className="size-3.5" />
            {tokens.toLocaleString()} tokens · ${c.usage.cost_usd.toFixed(4)}
          </span>
        </>
      )}
    </p>
  );
}

/** Copies the answer text, citations included. */
function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <button
      type="button"
      onClick={() => {
        void navigator.clipboard.writeText(text).then(() => {
          setCopied(true);
          window.setTimeout(() => setCopied(false), 1600);
        });
      }}
      aria-label={copied ? "Copied" : "Copy answer"}
      title="Copy answer"
      className="grid size-8 place-items-center rounded-lg text-ink-3 transition-colors hover:bg-inset hover:text-ink"
    >
      {copied ? (
        <Check aria-hidden className="size-4 animate-pop text-ok" />
      ) : (
        <Copy aria-hidden className="size-4" />
      )}
    </button>
  );
}

// Bands for words, not decisions: the abstention threshold is chosen in M8 from the
// risk-coverage curve. Below 0.5 the claim is more likely unsupported than supported.
export function confidenceWord(p: number): string {
  if (p >= 0.85) return "high";
  if (p >= 0.6) return "moderate";
  if (p >= 0.5) return "low";
  return "doubtful";
}

function ConfidenceBadge({ confidence }: { confidence: number | null }) {
  if (confidence === null) return null;
  return (
    <p
      className={cn(
        "inline-flex items-baseline gap-2 text-[13px] tabular-nums",
        confidence >= 0.6 ? "text-ink-2" : "text-danger",
      )}
      title="Calibrated probability that the answer's weakest claim is supported by the evidence"
    >
      <Gauge aria-hidden className="size-4 self-center" />
      <span className="font-mono text-[15px] font-medium">{Math.round(confidence * 100)}%</span>
      <span className="h-1.5 w-14 self-center overflow-hidden rounded-full bg-inset" aria-hidden>
        <span
          className={cn("block h-full origin-left animate-[grow_700ms_ease-out_both] rounded-full", confidence >= 0.6 ? "bg-ok" : "bg-danger")}
          style={{ width: `${Math.round(confidence * 100)}%` }}
        />
      </span>
      <span className="italic">{confidenceWord(confidence)}</span>
    </p>
  );
}

function ClaimConfidence({ claims }: { claims: AgentResult["claims"] }) {
  const scored = claims.filter((c): c is typeof c & { confidence: number } => c.confidence !== null);
  if (scored.length < 2) return null;
  return (
    <details className="rounded-xl border border-rule bg-sheet px-4 py-3 shadow-card">
      <summary className="cursor-pointer text-sm text-ink-3 hover:text-ink">
        Confidence per claim (the answer is as strong as its weakest)
      </summary>
      <ul className="mt-3 space-y-2">
        {scored.map((c, i) => (
          <li key={i} className="grid grid-cols-[4rem_1fr] items-baseline gap-3 text-sm">
            <span
              className={cn(
                "font-mono text-[12px] tabular-nums",
                c.confidence < 0.5 ? "text-danger" : "text-ink-3",
              )}
            >
              {Math.round(c.confidence * 100)}%
            </span>
            <span className="text-ink-2">{c.text}</span>
          </li>
        ))}
      </ul>
    </details>
  );
}

function VerificationBadge({ result }: { result: AgentResult }) {
  const v = result.verification;
  if (!v) return null;
  return (
    <p className="flex flex-wrap items-center gap-3">
      <span
        className={cn("stamp animate-stamp", v.ok ? "text-ok" : "text-danger")}
        title={v.ok ? "Every number in the answer was found in the evidence it cites" : verificationProblem({ ...v })}
      >
        {v.ok ? <Check aria-hidden className="size-3.5" /> : <CircleAlert aria-hidden className="size-3.5" />}
        {v.ok ? "Traced" : "Unverified"}
        {result.revisions > 0 && <span className="opacity-70">· rev. 1</span>}
      </span>
      {!v.ok && <span className="text-[13px] text-danger">{verificationProblem({ ...v })}</span>}
      <span className="sr-only">{v.ok ? "Every number traced to cited evidence" : ""}</span>
    </p>
  );
}

export function citedIds(answer: string): Set<string> {
  return new Set([...answer.matchAll(CITATION)].flatMap((m) => (m[1] ?? "").split(",").map((s) => s.trim())));
}

function EvidenceList({
  evidence,
  cited,
  sql,
  focused,
  onOpen,
}: {
  evidence: Evidence[];
  cited: Set<string>;
  sql: AgentResult["sql"];
  focused: string | null;
  onOpen: (id: string) => void;
}) {
  const allPassages = evidence.filter((e) => e.kind === "passage");
  const passages = allPassages.filter((e) => cited.has(e.id));
  const uncited = allPassages.filter((e) => !cited.has(e.id));
  const allFacts = evidence.filter((e) => e.kind === "fact");
  const facts = allFacts.filter((e) => cited.has(e.id));
  const uncitedFacts = allFacts.length - facts.length;
  return (
    <section aria-label="Evidence" className="space-y-4 pt-3">
      <h2 className="flex items-center gap-2.5">
        <span aria-hidden className="icon-tile size-8 rounded-lg">
          <FileText className="size-4" />
        </span>
        <span className="font-display text-xl">Exhibits</span>
        <span className="smallcaps text-ink-4">cited evidence</span>
      </h2>
      {facts.length > 0 && sql && (
        <div className="overflow-x-auto rounded-xl border border-rule bg-sheet shadow-card">
          <table className="greenbar w-full text-left text-[13px]">
            <thead className="border-b border-rule-strong text-ink-3">
              <tr>
                <th scope="col" className="smallcaps px-3 py-2 font-medium">
                  <Table2 aria-hidden className="size-3.5" />
                  <span className="sr-only">Citation</span>
                </th>
                {sql.columns.map((c) => (
                  <th key={c} scope="col" className="smallcaps px-3 py-2 font-medium whitespace-nowrap">
                    {c.replaceAll("_", " ")}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="font-mono tabular-nums">
              {facts.map((fact) => (
                <tr
                  key={fact.id}
                  id={`evidence-${fact.id}`}
                  className={cn(focused === fact.id && "!bg-mark/70")}
                >
                  <td className="px-3 py-1.5 font-medium text-mark-ink">{fact.id}</td>
                  {(sql.rows[Number(fact.id.slice(1)) - 1] ?? []).map((v, j) => (
                    <td key={j} className="px-3 py-1.5">
                      {formatCell(v)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {passages.length > 0 && <PassageList passages={passages} onOpen={onOpen} />}
      {(uncited.length > 0 || uncitedFacts > 0) && (
        <details className="group">
          <summary className="cursor-pointer text-sm text-ink-3 hover:text-ink">
            Retrieved but not cited:{" "}
            {[
              uncited.length > 0 && `${uncited.length} ${uncited.length === 1 ? "passage" : "passages"}`,
              uncitedFacts > 0 && `${uncitedFacts} data ${uncitedFacts === 1 ? "row" : "rows"}`,
            ]
              .filter(Boolean)
              .join(", ")}
          </summary>
          <div className="mt-2">
            <PassageList passages={uncited} onOpen={onOpen} />
          </div>
        </details>
      )}
    </section>
  );
}

function PassageList({ passages, onOpen }: { passages: Evidence[]; onOpen: (id: string) => void }) {
  return (
    <>
      {passages.length > 0 && (
        <ul className="space-y-2.5">
          {passages.map((p, i) => (
            <li key={p.id} className="animate-rise" style={{ animationDelay: `${i * 60}ms` }}>
              <button
                type="button"
                onClick={() => onOpen(p.id)}
                className="group lift grid w-full grid-cols-[2.75rem_1fr] gap-x-3 rounded-xl border border-rule bg-sheet px-4 py-3 text-left hover:border-rule-strong"
              >
                <span className="icon-tile h-7 w-9 rounded-lg font-mono text-[11px] font-medium">{p.id}</span>
                <span className="min-w-0">
                  <span className="block text-[13px] text-ink-3">{p.label}</span>
                  <span className="mt-1 line-clamp-2 font-serif text-[15px] text-ink-2 group-hover:text-ink">
                    {p.text}
                  </span>
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </>
  );
}

export function formatCell(value: unknown): string {
  if (typeof value === "number" && Math.abs(value) >= 1e6) {
    const abs = Math.abs(value);
    const [div, unit] = abs >= 1e9 ? [1e9, "B"] : [1e6, "M"];
    return `${value < 0 ? "-" : ""}$${(abs / div).toFixed(2)}${unit}`;
  }
  return String(value ?? "–");
}
