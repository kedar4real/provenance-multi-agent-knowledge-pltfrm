import { Collapsible } from "@base-ui/react/collapsible";
import { Switch } from "@base-ui/react/switch";
import { Toggle } from "@base-ui/react/toggle";
import { ToggleGroup } from "@base-ui/react/toggle-group";
import { ArrowRight, ChevronRight, Search } from "lucide-react";
import { useId, type FormEvent } from "react";

import type { Mode, SearchParams } from "../lib/api";
import { Button } from "./ui";

const MODES: { value: Mode; label: string; hint: string }[] = [
  { value: "hybrid", label: "Hybrid", hint: "meaning + keywords" },
  { value: "dense", label: "Meaning", hint: "embeddings only" },
  { value: "bm25", label: "Keywords", hint: "BM25 only" },
];

export const EXAMPLES = [
  "What supply chain risks from tariffs does Apple describe?",
  "How did JPMorgan's net interest income change in 2025?",
  "What is driving data center demand at Nvidia?",
];

interface Props {
  params: SearchParams;
  onChange: (params: SearchParams) => void;
  onSubmit: () => void;
  pending: boolean;
  disabled: boolean;
}

export function SearchForm({ params, onChange, onSubmit, pending, disabled }: Props) {
  const inputId = useId();
  const set = <K extends keyof SearchParams>(key: K, value: SearchParams[K]) => onChange({ ...params, [key]: value });

  function submit(event: FormEvent) {
    event.preventDefault();
    if (params.query.trim()) onSubmit();
  }

  return (
    <form onSubmit={submit} role="search" className="space-y-3">
      <label htmlFor={inputId} className="sr-only">
        Ask about the filings
      </label>
      <div className="flex items-center gap-2 rounded-lg border border-rule bg-sheet p-1.5 pl-3.5 focus-within:border-rule-strong">
        <Search aria-hidden className="size-4 shrink-0 text-ink-4" />
        <input
          id={inputId}
          type="search"
          value={params.query}
          onChange={(e) => set("query", e.target.value)}
          placeholder="Ask about any of the 30 companies' 10-K filings…"
          maxLength={1000}
          disabled={disabled}
          className="h-9 min-w-0 flex-1 bg-transparent text-[16px] placeholder:text-ink-4 focus:outline-none disabled:cursor-not-allowed"
        />
        <Button type="submit" disabled={disabled || pending || !params.query.trim()} aria-busy={pending}>
          {pending ? "Searching…" : "Search"}
          {!pending && <ArrowRight aria-hidden className="size-4" />}
        </Button>
      </div>

      <Collapsible.Root>
        <Collapsible.Trigger className="group flex items-center gap-1 text-sm text-ink-3 hover:text-ink">
          <ChevronRight aria-hidden className="size-3.5 transition-transform duration-150 group-data-panel-open:rotate-90" />
          Retrieval settings
          <span className="font-mono text-[12px] text-ink-4">
            {params.mode} · rerank {params.rerank ? "on" : "off"} · rewrite {params.rewrite ? "on" : "off"}
          </span>
        </Collapsible.Trigger>
        <Collapsible.Panel className="mt-3 flex flex-wrap items-center gap-x-6 gap-y-3 rounded-lg border border-rule bg-inset px-4 py-3">
          <div className="flex items-center gap-3">
            <span id={`${inputId}-mode`} className="text-sm text-ink-2">
              Retriever
            </span>
            <ToggleGroup
              aria-labelledby={`${inputId}-mode`}
              value={[params.mode]}
              onValueChange={(v: string[]) => v[0] && set("mode", v[0] as Mode)}
              className="flex rounded-md border border-rule bg-sheet p-0.5"
            >
              {MODES.map((m) => (
                <Toggle
                  key={m.value}
                  value={m.value}
                  title={m.hint}
                  className="h-7 rounded px-2.5 text-sm text-ink-2 hover:text-ink data-pressed:bg-ink data-pressed:text-paper"
                >
                  {m.label}
                </Toggle>
              ))}
            </ToggleGroup>
          </div>
          <LabeledSwitch
            label="Rerank"
            hint="cross-encoder, ~4 s"
            checked={params.rerank}
            onChange={(v) => set("rerank", v)}
          />
          <LabeledSwitch
            label="Rewrite"
            hint="LLM query + filters"
            checked={params.rewrite}
            onChange={(v) => set("rewrite", v)}
          />
        </Collapsible.Panel>
      </Collapsible.Root>
    </form>
  );
}

function LabeledSwitch(props: { label: string; hint: string; checked: boolean; onChange: (v: boolean) => void }) {
  const id = useId();
  return (
    <div className="flex items-center gap-2.5">
      <Switch.Root
        id={id}
        checked={props.checked}
        onCheckedChange={props.onChange}
        className="relative flex h-5 w-9 shrink-0 rounded-full border border-rule-strong bg-rule p-0.5 transition-colors duration-150 data-checked:border-ink data-checked:bg-ink"
      >
        <Switch.Thumb className="size-3.5 rounded-full bg-sheet shadow-sm transition-transform duration-150 data-checked:translate-x-4" />
      </Switch.Root>
      <label htmlFor={id} className="text-sm text-ink-2">
        {props.label} <span className="text-ink-4">{props.hint}</span>
      </label>
    </div>
  );
}
