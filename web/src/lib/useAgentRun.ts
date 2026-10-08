import { useCallback, useEffect, useRef, useState } from "react";

import { ApiError, streamQuery, type AgentResult, type TraceEvent } from "./api";

/** A step plus when it finished, in ms since the question was sent (for the timing chart). */
export interface TimedStep extends TraceEvent {
  at: number;
}

export type RunState =
  | { status: "idle" }
  | { status: "running"; question: string; steps: TimedStep[]; draft: string; startedAt: number }
  | { status: "done"; question: string; steps: TimedStep[]; result: AgentResult; elapsedMs: number }
  | { status: "error"; question: string; steps: TimedStep[]; message: string };

/** Asks a question over /v1/query and tracks the stream: steps as they finish, the answer's
 *  text as it is written (a draft, unverified until the result arrives), then the result. */
export function useAgentRun(apiKey: string, onDone?: (question: string, result: AgentResult, elapsedMs: number) => void) {
  const [run, setRun] = useState<RunState>({ status: "idle" });
  const inFlight = useRef<AbortController | null>(null);
  const done = useRef(onDone);
  done.current = onDone;

  useEffect(() => () => inFlight.current?.abort(), []);

  const ask = useCallback(
    async (q: string) => {
      const question = q.trim();
      if (!question) return;
      inFlight.current?.abort();
      const controller = new AbortController();
      inFlight.current = controller;
      const steps: TimedStep[] = [];
      let draft = "";
      const startedAt = performance.now();
      setRun({ status: "running", question, steps, draft, startedAt });
      try {
        await streamQuery(
          apiKey,
          question,
          (event) => {
            if (event.kind === "step") {
              steps.push({ ...event.data, at: performance.now() - startedAt });
              setRun({ status: "running", question, steps: [...steps], draft, startedAt });
            } else if (event.kind === "delta") {
              draft = event.data.reset ? "" : draft + event.data.text;
              setRun({ status: "running", question, steps: [...steps], draft, startedAt });
            } else if (event.kind === "result") {
              const elapsedMs = performance.now() - startedAt;
              setRun({ status: "done", question, steps: [...steps], result: event.data, elapsedMs });
              done.current?.(question, event.data, elapsedMs);
            } else {
              setRun({ status: "error", question, steps: [...steps], message: event.data.message });
            }
          },
          controller.signal,
        );
      } catch (e) {
        if (controller.signal.aborted) return;
        setRun({ status: "error", question, steps, message: e instanceof ApiError ? e.message : String(e) });
      }
    },
    [apiKey],
  );

  /** Shows a stored answer (from history) as if it had just finished. */
  const show = useCallback((question: string, result: AgentResult, elapsedMs: number) => {
    inFlight.current?.abort();
    setRun({ status: "done", question, steps: timedFromTrace(result.trace), result, elapsedMs });
  }, []);

  const reset = useCallback(() => {
    inFlight.current?.abort();
    setRun({ status: "idle" });
  }, []);

  return { run, ask, show, reset };
}

/** Without arrival times (a stored answer), lay the steps end to end. */
export function timedFromTrace(trace: TraceEvent[]): TimedStep[] {
  let at = 0;
  return trace.map((step) => {
    at += step.ms;
    return { ...step, at };
  });
}
