import { Check, ChevronDown, CircleAlert, LoaderCircle, Timer, Workflow, Zap } from "lucide-react";
import { useEffect, useId, useState, type ReactNode } from "react";

import type { TraceEvent } from "../lib/api";
import { cn } from "../lib/cn";
import { STEP_ICONS, STEP_LABELS, formatMs } from "../lib/steps";

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

export function StepTimeline({
  steps,
  running,
  startedAt,
  elapsedMs,
}: {
  steps: TraceEvent[];
  running: boolean;
  startedAt: number | null;
  elapsedMs: number | null;
}) {
  const listId = useId();
  // Open while it works; folds away once the answer is in, and the header toggles it.
  const [open, setOpen] = useState(running);
  const [wasRunning, setWasRunning] = useState(running);
  if (running !== wasRunning) {
    setWasRunning(running);
    setOpen(running);
  }
  return (
    <section
      aria-label="Agent steps"
      aria-live="polite"
      className="relative overflow-hidden rounded-2xl border border-rule bg-sheet shadow-card"
    >
      <button
        type="button"
        aria-expanded={open}
        aria-controls={listId}
        onClick={() => setOpen((o) => !o)}
        className={cn(
          "flex w-full items-center justify-between gap-3 px-4 py-3 text-left transition-colors hover:bg-inset/60",
          open && "border-b border-rule",
        )}
      >
        <span className="flex items-center gap-2 text-sm font-medium">
          <Workflow aria-hidden className="size-4 text-ink-3" />
          {running ? "Working on it" : "How it was answered"}
          {!open && steps.length > 0 && (
            <span className="font-normal text-ink-3">
              · {steps.length} step{steps.length === 1 ? "" : "s"}
            </span>
          )}
        </span>
        <span className="flex items-center gap-3">
          <span className="flex items-center gap-1.5 font-mono text-[12px] text-ink-3 tabular-nums">
            <Timer aria-hidden className="size-3.5" />
            {running && startedAt !== null ? <Elapsed since={startedAt} /> : elapsedMs !== null ? formatMs(elapsedMs) : "–"}
          </span>
          <ChevronDown
            aria-hidden
            className={cn("size-4 text-ink-3 transition-transform duration-200", open && "rotate-180")}
          />
          <span className="sr-only">{open ? "Hide steps" : "Show steps"}</span>
        </span>
      </button>
      {running && (
        <div aria-hidden className="absolute inset-x-0 top-0 h-0.5 overflow-hidden">
          <div className="h-full w-1/3 animate-sweep bg-gradient-to-r from-transparent via-pencil to-transparent" />
        </div>
      )}
      <div
        className={cn(
          "grid transition-[grid-template-rows] duration-300 ease-out",
          open ? "grid-rows-[1fr]" : "grid-rows-[0fr]",
        )}
      >
      <div className="overflow-hidden">
      <ol id={listId} className="px-4 py-1">
        {steps.map((step, i) => (
          <li key={i} className="relative grid animate-rise grid-cols-[2rem_1fr] gap-x-3 py-2.5 text-sm" style={{ animationDuration: "380ms" }}>
            {i < steps.length - 1 + (running ? 1 : 0) && (
              <span aria-hidden className="absolute top-10 bottom-0 left-4 w-px -translate-x-1/2 bg-rule" />
            )}
            <StepIcon step={step} />
            <div className="min-w-0 pt-1">
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
          <li className="grid grid-cols-[2rem_1fr] items-center gap-x-3 py-2.5 text-sm text-ink-3">
            <span className="relative grid size-8 place-items-center">
              <span aria-hidden className="absolute inset-0 animate-ping-soft rounded-full bg-pencil/40" />
              <span className="relative grid size-8 place-items-center rounded-full bg-pencil text-paper">
                <LoaderCircle aria-hidden className="size-4 animate-spin" />
              </span>
            </span>
            <span className="italic">{inProgress(steps)}</span>
          </li>
        )}
      </ol>
      </div>
      </div>
    </section>
  );
}

/** A ticking stopwatch for the run in progress. */
function Elapsed({ since }: { since: number }) {
  const [now, setNow] = useState(() => performance.now());
  useEffect(() => {
    const id = window.setInterval(() => setNow(performance.now()), 100);
    return () => window.clearInterval(id);
  }, []);
  return <>{((now - since) / 1000).toFixed(1)} s</>;
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
  const Icon = STEP_ICONS[step.step] ?? Check;
  const failed = (step.step === "verify" && step.detail.ok === false) || step.step === "abstain";
  const cached = step.step === "cache" && Boolean(step.detail.hit);
  const label = failed ? "needs attention" : cached ? "answered from cache" : "done";
  return (
    <span
      aria-label={label}
      className={cn(
        "relative grid size-8 animate-pop place-items-center rounded-full",
        failed ? "bg-danger/12 text-danger" : cached ? "bg-ok/15 text-ok" : "bg-mark/60 text-mark-ink",
      )}
    >
      {cached ? <Zap aria-hidden className="size-4" /> : <Icon aria-hidden className="size-4" />}
      <span
        aria-hidden
        className={cn(
          "absolute -right-0.5 -bottom-0.5 grid size-3.5 place-items-center rounded-full ring-2 ring-sheet",
          failed ? "bg-danger text-paper" : "bg-ok text-paper",
        )}
      >
        {failed ? <CircleAlert className="size-2.5" /> : <Check className="size-2.5" strokeWidth={3} />}
      </span>
    </span>
  );
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

export function verificationProblem(d: Record<string, unknown>): string {
  const numbers = (d.unsupported_numbers as string[] | undefined) ?? [];
  const unknown = (d.unknown_citations as string[] | undefined) ?? [];
  if (numbers.length) return `Not found in cited evidence: ${numbers.join(", ")}`;
  if (unknown.length) return `Cites missing evidence: ${unknown.join(", ")}`;
  if (d.uncited) return "Answer had no citations";
  return "Failed verification";
}
