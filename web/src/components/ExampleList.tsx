/** Example questions as a numbered schedule; a click asks it. */
export function ExampleList({ examples, onPick }: { examples: readonly string[]; onPick: (q: string) => void }) {
  return (
    <section aria-label="Example questions" className="pt-2">
      <p className="smallcaps text-ink-3">Try a question</p>
      <ol className="mt-3 border-t border-rule">
        {examples.map((q, i) => (
          <li key={q} className="animate-rise border-b border-rule" style={{ animationDelay: `${i * 70}ms` }}>
            <button
              type="button"
              onClick={() => onPick(q)}
              className="group grid w-full grid-cols-[2.25rem_1fr_auto] items-baseline gap-2 py-3.5 text-left"
            >
              <span className="font-mono text-[12px] text-ink-4 tabular-nums group-hover:text-pencil">
                {String(i + 1).padStart(2, "0")}
              </span>
              <span className="font-serif text-[17px] text-ink-2 transition-colors group-hover:text-ink">{q}</span>
              <span
                aria-hidden
                className="text-ink-4 opacity-0 transition-[opacity,translate] group-hover:translate-x-0.5 group-hover:text-pencil group-hover:opacity-100"
              >
                →
              </span>
            </button>
          </li>
        ))}
      </ol>
    </section>
  );
}
