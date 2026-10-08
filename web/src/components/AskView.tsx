import { ArrowRight, ArrowUpRight, Check, CircleAlert, LoaderCircle, ShieldAlert, Zap } from "lucide-react";
import { Fragment, useId, useRef, useState, type FormEvent, type ReactNode } from "react";

import { ApiError, streamQuery, type AgentResult, type Evidence, type TraceEvent } from "../lib/api";
import { cn } from "../lib/cn";
import type { Identity } from "../lib/identities";
import { STEP_LABELS, formatMs } from "../lib/steps";
import { ExampleList } from "./ExampleList";
import { TracePanel } from "./TracePanel";
import { Button } from "./ui";

const EXAMPLES = [
  "How did JPMorgan's net interest income change in fiscal 2025, and what drove it?",
  "Compare Apple's and Microsoft's R&D spending in fiscal 2025.",
  "What risks does Nvidia describe about export controls?",
];

type RunState =
  | { status: "idle" }
  | { status: "running"; steps: TraceEvent[] }
  | { status: "done"; steps: TraceEvent[]; result: AgentResult; elapsedMs: number }
  | { status: "error"; steps: TraceEvent[]; message: string };

interface Props {
  identity: Identity;
  onOpenSource: (chunkId: number) => void;
}

export function AskView({ identity, onOpenSource }: Props) {
  const [question, setQuestion] = useState("");
  const [run, setRun] = useState<RunState>({ status: "idle" });
  const inFlight = useRef<AbortController | null>(null);
  const inputId = useId();

  async function ask(q: string) {
    const text = q.trim();
    if (!text) return;
    inFlight.current?.abort();
    const controller = new AbortController();
    inFlight.current = controller;
    const steps: TraceEvent[] = [];
    const started = performance.now();
    setRun({ status: "running", steps });
    try {
      await streamQuery(
        identity.key,
        text,
        (event) => {
          if (event.kind === "step") {
            steps.push(event.data);
            setRun({ status: "running", steps: [...steps] });
          } else if (event.kind === "result") {
            setRun({ status: "done", steps: [...steps], result: event.data, elapsedMs: performance.now() - started });
          } else {
            setRun({ status: "error", steps: [...steps], message: event.data.message });
          }
        },
        controller.signal,
      );
    } catch (e) {
      if (controller.signal.aborted) return;
      setRun({ status: "error", steps, message: e instanceof ApiError ? e.message : String(e) });
    }
  }

  function submit(event: FormEvent) {
    event.preventDefault();
    void ask(question);
  }

  return (
    <div className="space-y-6">
      <form onSubmit={submit} className="space-y-2">
        <label htmlFor={inputId} className="sr-only">
          Ask a question
        </label>
        <div className="flex items-end gap-3 rounded-lg border border-rule-strong bg-sheet p-2 pl-4 shadow-[3px_3px_0_var(--color-rule)] transition-shadow focus-within:shadow-[3px_3px_0_var(--color-pencil)]">
          <span aria-hidden className="mb-2 font-display text-xl leading-none text-pencil">
            Q.
          </span>
          <textarea
            id={inputId}
            rows={1}
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                void ask(question);
              }
            }}
            placeholder="Ask a question. The agent reads filings, queries the numbers, and checks its answer."
            maxLength={1000}
            className="field-sizing-content max-h-40 min-h-9 min-w-0 flex-1 resize-none bg-transparent py-1.5 font-serif text-[17px] placeholder:text-ink-4 focus:outline-none"
          />
          <Button type="submit" disabled={run.status === "running" || !question.trim()} aria-busy={run.status === "running"}>
            {run.status === "running" ? "Working…" : "Ask"}
            {run.status !== "running" && <ArrowRight aria-hidden className="size-4" />}
          </Button>
        </div>
      </form>

      {run.status === "idle" && (
        <ExampleList
          examples={EXAMPLES}
          onPick={(q) => {
            setQuestion(q);
            void ask(q);
          }}
        />
      )}

      {run.status !== "idle" && <StepTimeline steps={run.steps} running={run.status === "running"} />}

      {run.status === "error" && (
        <p role="alert" className="rounded-lg border border-l-[3px] border-danger/40 border-l-danger bg-sheet px-4 py-3 text-sm text-danger">
          {run.message}
        </p>
      )}

      {run.status === "done" && (
        <AnswerView result={run.result} elapsedMs={run.elapsedMs} identity={identity} onOpenSource={onOpenSource} />
      )}
    </div>
  );
}

// ---- Steps ------------------------------------------------------------------------------

const TIER_REASONS: Record<string, string> = {
  simple: "a single lookup",
  multiple_companies: "several companies",
  multiple_years: "several years",
  comparison: "a comparison",
  calculation: "a calculation",
  explanation: "an explanation",
  long: "a long question",
  routing_off: "routing is off",
};

const ESCALATION_REASONS: Record<string, string> = {
  failed_verification: "the small model's numbers or citations still failed verification",
  declined_with_evidence: "the small model gave up although evidence was found",
  low_confidence: "the small model's answer scored low confidence",
};

function StepTimeline({ steps, running }: { steps: TraceEvent[]; running: boolean }) {
  return (
    <section aria-label="Agent steps" aria-live="polite">
      <p className="smallcaps mb-2 text-ink-3">Working</p>
      <ol className="border-t border-rule">
        {steps.map((step, i) => (
          <li
            key={i}
            className="grid animate-rise grid-cols-[2rem_1.25rem_1fr] items-start gap-x-2 border-b border-rule py-2.5 text-sm"
            style={{ animationDuration: "320ms" }}
          >
            <span className="pt-px font-mono text-[12px] text-ink-4 tabular-nums">{String(i + 1).padStart(2, "0")}</span>
            <StepIcon step={step} />
            <div className="min-w-0">
              <div className="flex items-baseline">
                <span className="font-medium">{STEP_LABELS[step.step] ?? step.step}</span>
                <span aria-hidden className="leader" />
                <span className="font-mono text-[12px] text-ink-3 tabular-nums">{formatMs(step.ms)}</span>
              </div>
              <StepDetail step={step} />
            </div>
          </li>
        ))}
        {running && (
          <li className="grid grid-cols-[2rem_1.25rem_1fr] items-center gap-x-2 border-b border-rule py-2.5 text-sm text-ink-3">
            <span className="font-mono text-[12px] text-ink-4 tabular-nums">
              {String(steps.length + 1).padStart(2, "0")}
            </span>
            <LoaderCircle aria-hidden className="size-4 animate-spin text-pencil motion-reduce:animate-none" />
            <span className="italic">{inProgress(steps)}</span>
          </li>
        )}
      </ol>
    </section>
  );
}

function inProgress(steps: TraceEvent[]): string {
  const done = new Set(steps.map((s) => s.step));
  const last = steps.at(-1)?.step;
  if (!last) return "Choosing a model…";
  if (last === "route") return "Checking earlier answers…";
  if (last === "cache") return "Choosing sources…";
  if (last === "escalate") return steps.at(-1)?.detail.skipped ? "Finishing…" : "Rewriting with the large model…";
  if (last === "plan") {
    const plan = steps.find((s) => s.step === "plan")?.detail ?? {};
    const work = [plan.needs_text && "reading filings", plan.needs_numbers && "querying financial data"];
    return `${capitalize(work.filter(Boolean).join(" and "))}…`;
  }
  if ((last === "search" || last === "sql") && !done.has("write")) return "Waiting for the other source, then writing…";
  if (last === "verify" && steps.at(-1)?.detail.ok === false) return "Revising the answer…";
  if (last === "write" || last === "revise") return "Checking numbers and citations…";
  if (last === "verify" || last === "score") return "Finishing…";
  return "Writing the answer…";
}

function capitalize(text: string): string {
  return text.charAt(0).toUpperCase() + text.slice(1);
}

function StepIcon({ step }: { step: TraceEvent }) {
  const failed = step.step === "verify" && step.detail.ok === false;
  if (failed) return <CircleAlert aria-label="needs revision" className="mt-0.5 size-4 shrink-0 text-danger" />;
  if (step.step === "escalate")
    return <ArrowUpRight aria-label="escalated" className="mt-0.5 size-4 shrink-0 text-ink-2" />;
  if (step.step === "abstain")
    return <ShieldAlert aria-label="withheld" className="mt-0.5 size-4 shrink-0 text-danger" />;
  if (step.step === "cache" && step.detail.hit)
    return <Zap aria-label="answered from cache" className="mt-0.5 size-4 shrink-0 text-ok" />;
  return <Check aria-hidden className="mt-0.5 size-4 shrink-0 text-ok" />;
}

function StepDetail({ step }: { step: TraceEvent }) {
  const d = step.detail;
  const line = (children: ReactNode) => <p className="mt-0.5 text-ink-3">{children}</p>;
  switch (step.step) {
    case "route": {
      const reasons = ((d.reasons as string[] | undefined) ?? []).map((r) => TIER_REASONS[r] ?? r);
      return line(
        <>
          {d.tier === "small" ? "Small model" : "Large model"} · {reasons.join(", ")}
        </>,
      );
    }
    case "cache":
      if (d.kind === "off" || d.kind === "error") return line(<>Not available</>);
      if (!d.hit)
        return line(
          <>
            No earlier answer
            {typeof d.similarity === "number" && <> (closest match {Math.round(d.similarity * 100)}% similar)</>}
          </>,
        );
      return line(
        d.kind === "exact" ? (
          <>Answered before: same question</>
        ) : (
          <>
            Same question as “{String(d.matched_question)}” ({Math.round(Number(d.similarity) * 100)}% similar,
            same companies, years and metrics)
          </>
        ),
      );
    case "escalate":
      return line(
        d.skipped ? (
          <>Skipped: would exceed this question's token budget</>
        ) : (
          <>Because {ESCALATION_REASONS[String(d.reason)] ?? String(d.reason)}</>
        ),
      );
    case "abstain":
      return line(
        <>
          Confidence {Math.round(Number(d.confidence) * 100)}% is below the {Math.round(Number(d.threshold) * 100)}%
          bar for answering
        </>,
      );
    case "score":
      return typeof d.confidence === "number"
        ? line(<>{String(d.claims)} claims · weakest {Math.round(d.confidence * 100)}%</>)
        : line(<>{String(d.claims)} claims · no calibrated confidence yet</>);
    case "plan": {
      const routes = [d.needs_text && "filings", d.needs_numbers && "financial data"].filter(Boolean);
      return line(<>Will use {routes.join(" and ")}</>);
    }
    case "search":
      return line(
        <>
          {String(d.passages)} passages
          {Array.isArray(d.top) && d.top.length > 0 && <> · {[...new Set(d.top as string[])].join(", ")}</>}
        </>,
      );
    case "sql":
      return (
        <>
          {line(d.error ? <span className="text-danger">{String(d.error)}</span> : <>{String(d.rows)} rows</>)}
          {typeof d.sql === "string" && d.sql && (
            <details className="mt-1">
              <summary className="cursor-pointer text-[13px] text-ink-3 hover:text-ink">SQL it ran</summary>
              <pre className="mt-1 overflow-x-auto rounded bg-inset p-2 font-mono text-[12px] whitespace-pre-wrap text-ink-2">
                {d.sql}
              </pre>
            </details>
          )}
        </>
      );
    case "write":
    case "revise":
      return d.degraded ? line(<>Large model unavailable (free tier); answered with the small model</>) : null;
    case "verify":
      return line(d.ok ? <>Every number found in the evidence it cites</> : <>{verificationProblem(d)}</>);
    default:
      return null;
  }
}

function verificationProblem(d: Record<string, unknown>): string {
  const numbers = (d.unsupported_numbers as string[] | undefined) ?? [];
  const unknown = (d.unknown_citations as string[] | undefined) ?? [];
  if (numbers.length) return `Not found in cited evidence: ${numbers.join(", ")}`;
  if (unknown.length) return `Cites missing evidence: ${unknown.join(", ")}`;
  if (d.uncited) return "Answer had no citations";
  return "Failed verification";
}

// ---- Answer -----------------------------------------------------------------------------

const CITATION = /\[((?:[PF]\d+)(?:\s*,\s*[PF]\d+)*)\]/g;

function AnswerView({
  result,
  elapsedMs,
  identity,
  onOpenSource,
}: {
  result: AgentResult;
  elapsedMs: number;
  identity: Identity;
  onOpenSource: (id: number) => void;
}) {
  const [focusedFact, setFocusedFact] = useState<string | null>(null);
  const byId = new Map(result.evidence.map((e) => [e.id, e]));

  if (result.control?.abstained) {
    return (
      <article className="space-y-5">
        <div className="border-l-[3px] border-pencil bg-sheet px-5 py-4">
          <p className="stamp mb-3 text-pencil">Withheld</p>
          <p className="font-display text-2xl">Not confident enough to answer.</p>
          <p className="mt-1 text-sm text-ink-2">
            A draft was written, but its weakest claim scored {Math.round((result.confidence ?? 0) * 100)}% confidence.
            Rather than risk a wrong answer, here is what was found, so you can read it yourself.
          </p>
        </div>
        <RunSummary result={result} />
        <TracePanel result={result} elapsedMs={elapsedMs} />
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
      <div className="border-l-[3px] border-rule-strong bg-sheet px-5 py-4">
        <p className="font-display text-2xl">No answer from the evidence.</p>
        <p className="mt-1 text-sm text-ink-2">
          Nothing {identity.displayName.split(" ")[0]} can see answers this. It may be in filings outside their
          access, or in no filing at all.
        </p>
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

  return (
    <article className="space-y-5">
      <header className="flex flex-wrap items-center justify-between gap-x-4 gap-y-3 border-b-[3px] border-double border-rule-strong pb-3">
        <h2 className="font-display text-[28px] leading-none">Answer</h2>
        <div className="flex flex-wrap items-center gap-3">
          <ConfidenceBadge confidence={result.confidence} />
          <VerificationBadge result={result} />
        </div>
      </header>
      <RunSummary result={result} />
      <div className="space-y-3 font-serif text-[18.5px] leading-[1.72] text-ink">
        {renderAnswer(result.answer, byId, openCitation)}
      </div>
      <ClaimConfidence claims={result.claims} />
      <TracePanel result={result} elapsedMs={elapsedMs} />
      <EvidenceList
        evidence={result.evidence}
        cited={citedIds(result.answer)}
        sql={result.sql}
        focused={focusedFact}
        onOpen={openCitation}
      />
    </article>
  );
}

/** Paragraphs and "*"/"-" bullet lists, the only markdown the models produce here. */
function renderAnswer(text: string, byId: Map<string, Evidence>, onOpen: (id: string) => void): ReactNode[] {
  const blocks: ReactNode[] = [];
  let bullets: string[] = [];
  const flush = () => {
    if (!bullets.length) return;
    blocks.push(
      <ul key={`ul-${blocks.length}`} className="list-disc space-y-1 pl-6 marker:text-ink-4">
        {bullets.map((b, i) => (
          <li key={i}>{renderWithCitations(b, byId, onOpen)}</li>
        ))}
      </ul>,
    );
    bullets = [];
  };
  for (const raw of text.split("\n")) {
    const line = raw.trim();
    const bullet = /^[*-]\s+(.*)$/.exec(line);
    if (bullet) {
      bullets.push(bullet[1] ?? "");
      continue;
    }
    flush();
    if (line) blocks.push(<p key={`p-${blocks.length}`}>{renderWithCitations(line, byId, onOpen)}</p>);
  }
  flush();
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
            onClick={() => onOpen(id)}
            disabled={!byId.has(id)}
            aria-label={`Source ${id}: ${byId.get(id)?.label ?? "missing"}`}
            className="mx-0.5 inline-flex -translate-y-[0.35em] items-center rounded-sm border-b-2 border-mark-strong bg-mark/60 px-1 align-baseline font-mono text-[11px] leading-[1.4] font-medium text-mark-ink transition-colors hover:bg-mark hover:text-ink disabled:border-danger disabled:bg-transparent disabled:text-danger"
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
  const parts = [
    c.cache?.hit ? "From an earlier answer" : `${c.tier === "small" ? "Small" : "Large"} model`,
    c.escalated && "escalated",
    !c.cache?.hit && `${tokens.toLocaleString()} tokens`,
    !c.cache?.hit && `$${c.usage.cost_usd.toFixed(4)} at list prices`,
  ].filter(Boolean);
  return (
    <p
      className="font-mono text-[12px] text-ink-4 tabular-nums"
      title="API-equivalent cost: tokens priced at Claude Haiku (small) and Sonnet (large) list prices. The real calls ran on free tiers."
    >
      {parts.join(" · ")}
    </p>
  );
}

// Bands for words, not decisions: the abstention threshold is chosen in M8 from the
// risk-coverage curve. Below 0.5 the claim is more likely unsupported than supported.
function confidenceWord(p: number): string {
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
      <span className="smallcaps text-ink-4">Confidence</span>
      <span className="font-mono text-[15px] font-medium">{Math.round(confidence * 100)}%</span>
      <span className="italic">{confidenceWord(confidence)}</span>
    </p>
  );
}

function ClaimConfidence({ claims }: { claims: AgentResult["claims"] }) {
  const scored = claims.filter((c): c is typeof c & { confidence: number } => c.confidence !== null);
  if (scored.length < 2) return null;
  return (
    <details className="border-y border-rule py-3">
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

function citedIds(answer: string): Set<string> {
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
      <h2 className="flex items-baseline gap-3">
        <span className="font-display text-xl">Exhibits</span>
        <span className="smallcaps text-ink-4">cited evidence</span>
      </h2>
      {facts.length > 0 && sql && (
        <div className="overflow-x-auto rounded-lg border border-rule bg-sheet">
          <table className="greenbar w-full text-left text-[13px]">
            <thead className="border-b border-rule-strong text-ink-3">
              <tr>
                <th scope="col" className="smallcaps px-3 py-2 font-medium">
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
        <ul className="space-y-2">
          {passages.map((p) => (
            <li key={p.id}>
              <button
                type="button"
                onClick={() => onOpen(p.id)}
                className="group grid w-full grid-cols-[2.75rem_1fr] gap-x-3 rounded-lg border border-rule bg-sheet px-4 py-3 text-left transition-[border-color,box-shadow] hover:border-rule-strong hover:shadow-[3px_3px_0_var(--color-rule)]"
              >
                <span className="pt-0.5 font-mono text-[12px] font-medium text-mark-ink">{p.id}</span>
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

function formatCell(value: unknown): string {
  if (typeof value === "number" && Math.abs(value) >= 1e6) {
    const abs = Math.abs(value);
    const [div, unit] = abs >= 1e9 ? [1e9, "B"] : [1e6, "M"];
    return `${value < 0 ? "-" : ""}$${(abs / div).toFixed(2)}${unit}`;
  }
  return String(value ?? "–");
}
