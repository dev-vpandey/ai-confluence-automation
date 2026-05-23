# config.yaml for Runtime Settings

Confluence base URL and HTTP timeouts are hardcoded in three source files. Any environment change (staging instance, different org) requires editing source code. A centralised config file removes that friction without introducing a new runtime dependency.

## Considered Options

**Env vars only** — extend the existing `CONFLUENCE_TOKEN` pattern with `CONFLUENCE_BASE_URL`, `CONFLUENCE_TIMEOUT_*`, etc. No new deps, but a growing list of env vars with no schema or defaults file. Harder to document and set up across machines.

**`.env` file + python-dotenv** — flat key=value file, auto-loaded. Requires adding `python-dotenv` dependency. Flat format makes nested config (e.g. per-operation timeouts) awkward.

**`config.yaml` (chosen)** — structured file at project root, gitignored, with `config.example.yaml` as the documented template. `pyyaml` is already a common dep in Python tooling. Supports grouped sections (`confluence:`, `timeouts:`) that scale cleanly if more settings are added.

## Consequences

- `config.yaml` is opt-in: if absent, all modules fall back to hardcoded defaults. Existing users are unaffected.
- `CONFLUENCE_TOKEN` env var is unchanged — auth loading is not touched by this change.
- Scope is intentionally narrow: `confluence.base_url`, `confluence.session_file`, and the three HTTP timeouts. REST API paths, cookie names, and Chrome DB paths stay hardcoded — they are protocol constants, not environment-specific settings.
- `pyyaml>=6.0` added to `requirements.txt`.
