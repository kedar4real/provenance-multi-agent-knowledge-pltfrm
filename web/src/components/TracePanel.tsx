import type { AgentResult, LLMCall } from "../lib/api";
import { STEP_LABELS, formatMs } from "../lib/steps";

/** How the answer was made: each step's time, the model calls it made, their tokens and
 *  API-equivalent cost. Parallel steps (search and SQL) overlap, so step times don't add up
 *  to the total; the total is measured in the browser. */
export function TracePanel({ result, elapsedMs }: { result: AgentResult; elapsedMs: number | null }) {
  const calls = result.control?.usage.calls ?? [];
  const byNode = new Map<string, LLMCall[]>();
  for (const call of calls) byNode.set(call.node, [...(byNode.get(call.node) ?? []), call]);
  const usage = result.control?.usage;

  return (
    <details className="rounded-lg border border-rule bg-sheet">
      <summary className="cursor-pointer px-4 py-3 text-sm text-ink-3 hover:text-ink">
        <span className="font-medium text-ink-2">Schedule of work</span>
        <span className="ml-2">how this answer was made</span>
        <span className="ml-2 font-mono text-[12px] text-ink-4 tabular-nums">
          {result.trace.length} steps · {calls.length} model calls
          {elapsedMs !== null && <> · {formatMs(elapsedMs)}</>}
        </span>
      </summary>
      <div className="overflow-x-auto border-t border-rule">
        <table className="greenbar w-full text-left text-[13px]">
          <caption className="sr-only">Steps, model calls, tokens and cost for this answer</caption>
          <thead className="smallcaps text-ink-4">
            <tr className="border-b border-rule">
              <th scope="col" className="px-4 py-2 font-normal">Step</th>
              <th scope="col" className="px-2 py-2 text-right font-normal">Time</th>
              <th scope="col" className="px-2 py-2 font-normal">Model</th>
              <th scope="col" className="px-2 py-2 text-right font-normal whitespace-nowrap">Tokens in / out</th>
              <th scope="col" className="px-4 py-2 text-right font-normal">Cost</th>
            </tr>
          </thead>
          <tbody>
            {result.trace.map((step, i) => {
              const own = byNode.get(step.step) ?? [];
              // A node's calls are listed once, on its first step (a revision repeats "write").
              const first = result.trace.findIndex((s) => s.step === step.step) === i;
              const shown = first ? own : [];
              return (
                <tr key={i} className="align-top">
                  <th scope="row" className="min-w-44 px-4 py-2 font-normal text-ink-2">
                    {STEP_LABELS[step.step] ?? step.step}
                  </th>
                  <td className="px-2 py-2 text-right font-mono whitespace-nowrap text-ink-3 tabular-nums">{formatMs(step.ms)}</td>
                  <td className="px-2 py-2 font-mono text-[12px] text-ink-3">
                    {shown.map((c, j) => (
                      <div key={j} className="whitespace-nowrap">
                        {c.provider}/{c.model}
                      </div>
                    ))}
                  </td>
                  <td className="px-2 py-2 text-right font-mono text-ink-3 tabular-nums">
                    {shown.map((c, j) => (
                      <div key={j} className="whitespace-nowrap">
                        {c.input_tokens.toLocaleString()} / {c.output_tokens.toLocaleString()}
                      </div>
                    ))}
                  </td>
                  <td className="px-4 py-2 text-right font-mono text-ink-3 tabular-nums">
                    {shown.map((c, j) => (
                      <div key={j}>${c.cost_usd.toFixed(4)}</div>
                    ))}
                  </td>
                </tr>
              );
            })}
          </tbody>
          {usage && (
            <tfoot className="border-t-[3px] border-double border-rule-strong text-ink">
              <tr>
                <th scope="row" className="px-4 py-2 font-medium">Total</th>
                <td className="px-2 py-2 text-right font-mono whitespace-nowrap tabular-nums">
                  {elapsedMs !== null ? formatMs(elapsedMs) : ""}
                </td>
                <td />
                <td className="px-2 py-2 text-right font-mono tabular-nums">
                  {usage.input_tokens.toLocaleString()} / {usage.output_tokens.toLocaleString()}
                </td>
                <td className="px-4 py-2 text-right font-mono tabular-nums">${usage.cost_usd.toFixed(4)}</td>
              </tr>
            </tfoot>
          )}
        </table>
      </div>
      <p className="border-t border-rule px-4 py-2 text-[12px] text-pretty text-ink-4">
        Cost is what these tokens would cost at Claude Haiku (small model) and Sonnet (large model) list prices;
        every call here ran on a free tier. Search and financial-data steps run in parallel, so step times overlap.
      </p>
    </details>
  );
}
