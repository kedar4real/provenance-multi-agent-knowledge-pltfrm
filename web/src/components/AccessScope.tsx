import { ShieldCheck } from "lucide-react";
import { useEffect, useState } from "react";

import { api, type Me } from "../lib/api";
import type { Identity } from "../lib/identities";

/** What the current identity can see, before they search. The database decides this
 *  (row-level security); the page only reports it. */
export function AccessScope({ identity }: { identity: Identity }) {
  const [me, setMe] = useState<Me | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    api.me(identity.key, controller.signal).then(setMe, () => undefined);
    return () => controller.abort();
  }, [identity.key]);

  if (!me) return <p className="h-5" aria-hidden />;

  const { tickers, documents } = me.visible;
  const name = identity.displayName.split(" ")[0];
  return (
    <p className="flex flex-wrap items-center gap-x-2 gap-y-1 text-sm text-ink-3">
      <ShieldCheck aria-hidden className="size-4 text-ink-4" />
      <span>
        {name} can see <span className="text-ink-2 tabular-nums">{tickers.length}</span>{" "}
        {tickers.length === 1 ? "company" : "companies"} ·{" "}
        <span className="text-ink-2 tabular-nums">{documents}</span> filings
      </span>
      <span className="font-mono text-[12px] text-ink-4">
        {tickers.length > 12 ? `${tickers.slice(0, 12).join(" ")} +${tickers.length - 12}` : tickers.join(" ")}
      </span>
    </p>
  );
}
