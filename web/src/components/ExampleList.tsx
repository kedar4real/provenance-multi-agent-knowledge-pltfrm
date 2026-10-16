import { ArrowRight, ChartColumn, Landmark, Lightbulb, MessageCircleQuestion, Scale, type LucideIcon } from "lucide-react";

const ICONS: LucideIcon[] = [Landmark, Scale, ChartColumn];

/** Example questions as a numbered schedule; a click asks it. */
export function ExampleList({ examples, onPick }: { examples: readonly string[]; onPick: (q: string) => void }) {
  return (
    <section aria-label="Example questions" className="pt-2">
      <p className="flex items-center gap-2 text-sm text-ink-3">
        <Lightbulb aria-hidden className="size-4" />
        Try a question
      </p>
      <ol className="mt-3 space-y-2">
        {examples.map((q, i) => {
          const Icon = ICONS[i % ICONS.length] ?? MessageCircleQuestion;
          return (
          <li key={q} className="animate-rise" style={{ animationDelay: `${i * 80}ms` }}>
            <button
              type="button"
              onClick={() => onPick(q)}
              className="group lift grid w-full grid-cols-[2.25rem_1fr_auto] items-center gap-3 rounded-xl border border-rule bg-sheet px-3 py-3 text-left hover:border-rule-strong"
            >
              <span aria-hidden className="icon-tile size-9 rounded-lg transition-transform duration-200 group-hover:scale-110 group-hover:-rotate-6">
                <Icon className="size-4" />
              </span>
              <span className="font-serif text-[17px] text-ink-2 transition-colors group-hover:text-ink">{q}</span>
              <span
                aria-hidden
                className="text-ink-4 opacity-0 transition-[opacity,translate] group-hover:translate-x-0.5 group-hover:text-pencil group-hover:opacity-100"
              >
                <ArrowRight className="size-4" />
              </span>
            </button>
          </li>
          );
        })}
      </ol>
    </section>
  );
}
