## Dev environment setup
- Install [uv](https://docs.astral.sh/uv/getting-started/installation/) package manager
- Create venv and install dependencies: `uv sync`
- Activate virtual environment as described below
- Install pre-commit hooks `pre-commit install`
- Install pre commit message hook: `pre-commit install --hook-type commit-msg`

## Automating Tokensave hooks
`tokensave sync` and `tokensave branch add`/`branch gc` are wired into local git hooks via a dedicated
pre-commit config, `.tokensave-hooks.yaml`, kept separate from `.pre-commit-config.yaml` (the config CI runs
for quality gates) so CI never invokes tokensave. Install once per clone:
```bash
pre-commit install -c .tokensave-hooks.yaml -t post-commit -t post-merge -t post-rewrite -t post-checkout
```
This wires:
- `post-commit`, `post-merge`, `post-rewrite` → `tokensave sync` (after commits, merges/pulls, rebases/amends)
- `post-checkout` → `tokensave branch add` + `tokensave branch gc` (after switching branches)