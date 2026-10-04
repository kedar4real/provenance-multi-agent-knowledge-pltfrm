import { Dialog } from "@base-ui/react/dialog";
import { X } from "lucide-react";
import { useId, useState, type FormEvent } from "react";

import { api, ApiError } from "../lib/api";
import { identities } from "../lib/identities";
import { Button } from "./ui";

interface Props {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function AddIdentityDialog({ open, onOpenChange }: Props) {
  const [key, setKey] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);
  const inputId = useId();
  const hintId = useId();
  const errorId = useId();

  async function submit(event: FormEvent) {
    event.preventDefault();
    const apiKey = key.trim();
    if (!apiKey) {
      setError("Paste an API key first.");
      return;
    }
    setPending(true);
    setError(null);
    try {
      const me = await api.me(apiKey);
      identities.add({ key: apiKey, name: me.name, displayName: me.display_name, groups: me.groups });
      setKey("");
      onOpenChange(false);
    } catch (e) {
      setError(e instanceof ApiError && e.status === 401 ? "That key isn't valid." : String((e as Error).message));
    } finally {
      setPending(false);
    }
  }

  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Backdrop className="fixed inset-0 z-40 bg-ink/20 transition-opacity duration-150 data-ending-style:opacity-0 data-starting-style:opacity-0" />
        <Dialog.Viewport className="fixed inset-0 z-50 grid place-items-center p-4">
          <Dialog.Popup className="w-full max-w-md rounded-xl border border-rule bg-sheet p-6 shadow-lg transition-[opacity,transform] duration-150 ease-out data-ending-style:scale-95 data-ending-style:opacity-0 data-starting-style:scale-95 data-starting-style:opacity-0">
            <div className="flex items-start justify-between gap-4">
              <Dialog.Title className="font-serif text-xl font-medium">Add an identity</Dialog.Title>
              <Dialog.Close aria-label="Close" className="-m-2 rounded-md p-2 text-ink-3 hover:bg-inset hover:text-ink">
                <X aria-hidden className="size-4" />
              </Dialog.Close>
            </div>
            <Dialog.Description className="mt-1 text-ink-2">
              Each identity is a demo user with its own access groups. What it can see is decided by the
              database, not this page.
            </Dialog.Description>

            <form onSubmit={submit} className="mt-5 space-y-2" noValidate>
              <label htmlFor={inputId} className="block text-sm font-medium">
                API key
              </label>
              <input
                id={inputId}
                type="password"
                autoComplete="off"
                spellCheck={false}
                value={key}
                onChange={(e) => setKey(e.target.value)}
                aria-describedby={error ? `${errorId} ${hintId}` : hintId}
                aria-invalid={error ? true : undefined}
                placeholder="pk_…"
                className="w-full rounded-md border border-rule bg-inset px-3 py-2 font-mono text-sm placeholder:text-ink-4 aria-invalid:border-danger"
              />
              {error && (
                <p id={errorId} role="alert" className="text-sm text-danger">
                  {error}
                </p>
              )}
              <p id={hintId} className="text-sm text-ink-3">
                Issue one with{" "}
                <code className="rounded bg-inset px-1 py-0.5 font-mono text-[13px] text-ink-2">
                  uv run python -m provenance.api.keys issue ana_tech
                </code>
                . Stored only in this browser.
              </p>
              <div className="flex justify-end gap-2 pt-3">
                <Dialog.Close render={<Button variant="ghost" />}>Cancel</Dialog.Close>
                <Button type="submit" disabled={pending} aria-busy={pending}>
                  {pending ? "Checking…" : "Add identity"}
                </Button>
              </div>
            </form>
          </Dialog.Popup>
        </Dialog.Viewport>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
