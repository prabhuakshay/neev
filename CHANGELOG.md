# Changelog

## Unreleased

## v0.2.0 - 2026-06-09

### Added
- `neev share` subcommand for generating HMAC-signed, scoped share links that bypass auth for a single path
- `share_secret` config wiring through CLI, `neev.toml`, and user config
- `--public-url` flag (with matching TOML key) to set the externally reachable base URL shown in the banner and share links
- user-level `neev.toml` support resolved via XDG / `%APPDATA%` / `~/.config`
- rendered HTML file previews in the browser, with a toggle to view the raw source

### Changed
- split the monolithic `cli.py` into focused `cli`, `cli_validators`, and `cli_banner` modules
- dropped environment-variable configuration in favor of CLI flags and TOML files

### Fixed
- HTML source preview no longer highlights a placeholder before the file loads, and re-highlights correctly once highlight.js and the fetched text are ready

## v0.1.0 - 2026-04-12

Initial public release.

### Added
- zero-dependency HTTP file server CLI (`neev`) built on the Python standard library
- directory listings with per-file icons, breadcrumbs, and sortable columns
- in-browser previews for text, markdown (server-rendered), images, and PDFs
- HTTP Basic Auth via `--auth user:pass` or `NEEV_AUTH` env var, with constant-time credential comparison
- streaming ZIP downloads of folders (`--enable-zip-download`) with `--max-zip-size` cap
- opt-in file uploads (`--enable-upload`) with filename sanitization and path-traversal protection
- `--read-only` mode that force-disables writes
- `--show-hidden`, `--banner`, and custom `--host` / `--port` flags
- `neev.toml` config file support, merged under CLI precedence
- HTTP Range request support for resumable downloads and media seeking
- threaded HTTP server for concurrent request handling
- hardened origin checks and auth/upload robustness
- comprehensive README with CLI, HTTP API, security model, recipes, and architecture
