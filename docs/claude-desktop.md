# Claude Desktop -> mcpgate -> provenance-mcp

Claude Desktop launches `mcpgate`, which launches `provenance-mcp`, which calls the running
API with an API key. Claude only ever sees the tools the gate approved, and only the data that
key's principal may see.

```
Claude Desktop --stdio--> mcpgate --stdio--> provenance-mcp --HTTP + API key--> provenance API
```

## Setup (once)

1. The API must be running: `uv run python -m provenance.api`.
2. Issue a key for the principal Claude should act as. Issuing replaces that principal's
   previous key, so pick one you don't use in the web UI (e.g. `fin_finance`):
   ```powershell
   uv run python -m provenance.api.keys issue fin_finance
   ```
3. Look at what the gate would serve, then approve it (pins the tool definitions):
   ```powershell
   $env:PROVENANCE_API_KEY = "<the key>"
   .venv\Scripts\mcpgate.exe inspect --policy config\mcpgate.yaml --caller claude-desktop -- .venv\Scripts\provenance-mcp.exe
   .venv\Scripts\mcpgate.exe approve --policy config\mcpgate.yaml -- .venv\Scripts\provenance-mcp.exe
   ```
   The policy uses `first_use: require_approval`, so nothing is served before this step.
4. Add the server to Claude Desktop's `claude_desktop_config.json` (the key is stored there,
   on your machine only). Its location depends on how Desktop was installed: the Microsoft
   Store app keeps it under
   `%LOCALAPPDATA%\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\`, a direct install
   under `%APPDATA%\Claude\`. (Desktop's Settings > Developer > Edit Config opens the right file.)
   ```json
   {
     "mcpServers": {
       "provenance": {
         "command": "C:\\Users\\Kedar\\projects\\provenance\\.venv\\Scripts\\mcpgate.exe",
         "args": [
           "run", "--policy", "C:\\Users\\Kedar\\projects\\provenance\\config\\mcpgate.yaml",
           "--caller", "claude-desktop",
           "--", "C:\\Users\\Kedar\\projects\\provenance\\.venv\\Scripts\\provenance-mcp.exe"
         ],
         "env": { "PROVENANCE_API_KEY": "<the key>" }
       }
     }
   }
   ```
5. Restart Claude Desktop. The tools menu shows `whoami`, `search_filings`, `get_passage` and
   `ask`. Try: "Using provenance, what drove JPMorgan's net interest income in fiscal 2025?"

## What to look at

- `.mcpgate/audit.jsonl`: every listing, call, refusal, drift and flagged output.
- If `provenance-mcp`'s tools ever change (a code change, or a compromised package), the gate
  blocks the changed tools until you run `approve` again: the same check that stops a rug pull.
- The gate passes `provenance-mcp` only `PROVENANCE_API_KEY` and `PROVENANCE_API_URL` from its
  environment (`upstream_env` in the policy).

## Try the attacks

```powershell
.venv\Scripts\mcpgate.exe inspect --policy config\mcpgate.yaml --caller claude-desktop -- .venv\Scripts\python.exe packages\mcpgate\fixtures\evil_server.py
```

reports the poisoned and shadowing tools. Run against the evil server, the gate hides them,
withholds the injected weather report, and blocks `translate` once it rug-pulls.
