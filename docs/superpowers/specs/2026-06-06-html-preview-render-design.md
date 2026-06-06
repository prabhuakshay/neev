# Rendered HTML Preview — Design

**Date:** 2026-06-06
**Status:** Approved

## Problem

`.html`/`.htm` files are already "previewable" in neev, but clicking **Preview**
renders the HTML **source code** with syntax highlighting (via the text/code
preview). Opening the raw file link renders the page, but without neev's preview
chrome (back button, download). There is no way to view a rendered HTML page
inside neev's UI.

## Goal

Clicking **Preview** on an HTML file renders the page inside neev's preview
frame, with a toggle to switch between the rendered page and its
syntax-highlighted source.

## Decisions

- **Full-fidelity render (no `sandbox`).** The iframe runs scripts at neev's
  origin. User-approved; rationale in Security Model below.
- **Render/source toggle.** The preview page defaults to the rendered page and
  offers a control to switch to source.

## Design

### 1. Routing — `src/neev/server.py`

Add one branch in `do_GET`, **after** the markdown check and **before** the
generic `is_previewable_type` check (HTML passes `is_previewable_type` via the
`text/` prefix, so ordering is load-bearing):

```python
if "preview" in query and get_mime_type(resolved) == "text/html":
    serve_html_preview(self, resolved, request_path)
    return
```

Matching on `mime == "text/html"` covers `.html` and `.htm`. `.xhtml`
(guessed as `application/xhtml+xml`) is **intentionally out of scope** — it
continues to show source via the existing text preview.

### 2. Handler — `src/neev/server_preview.py`

New `serve_html_preview(handler, path, request_path)`, mirroring the existing
preview handlers. Computes:

- `raw_url = encode_attr_url(raw_path)` — **no query string**. This is the
  iframe `src`; it hits `serve_file` → inline `text/html` → the browser
  renders it. It must NOT be `?download` (forces attachment) or `?preview`
  (would recurse into this handler). Relative CSS/img/script links inside the
  HTML resolve against the file's own directory, so they load correctly.
- `raw_url_js = script_safe_json(raw_path)` — JSON-encoded raw path, fetched
  client-side for the source view.
- `download_url = encode_attr_url(raw_path) + "?download"` — forced download.
- `parent = _parent_url(request_path)` — back link.

Sends the page as `text/html; charset=utf-8`, same response shape as the other
preview handlers.

### 3. Template — `src/neev/html_render.py` (new module)

New `render_html_preview(filename, raw_url, raw_url_js, parent_url, download_url)`.

A new module — not an addition to `html_preview.py` — because:

- Markdown preview already follows this "own module" precedent
  (`html_markdown.py`), so this is consistent.
- It keeps `html_preview.py` (currently 209 lines) under the project's
  300-line limit.

The page:

- Reuses the existing preview header/footer look (back link + download button).
- **Default view:** a full-fidelity `<iframe src="{raw_url}">` with **no**
  `sandbox` attribute, in a tall container styled like the PDF `<embed>`
  (`height:85vh`).
- **Toggle:** a **Preview / Source** control. Selecting Source hides the
  iframe and shows a `<pre>` that lazily fetches the raw text and highlights
  it with the same highlight.js CDN setup used by `render_text_preview`. This
  highlight.js block is **duplicated**, not extracted into a shared helper —
  two call sites is measured duplication, which the project prefers over a
  premature abstraction.

### 4. Listing — `src/neev/html_entries.py`

**No change.** HTML is already `is_previewable_type`, so the directory listing
already emits the `data-preview-href="...?preview"` affordance for HTML files.
Stated explicitly so a reader does not go looking for a change here.

## Security Model

The iframe is **non-sandboxed**, so scripts in a shared or uploaded HTML file
execute at neev's origin when previewed. This is the **same exposure** that
already exists when a user opens the raw HTML link directly — opening the file
already executes its scripts same-origin, and the iframe grants no new
fetch/exfiltration capability. The only marginal addition is that a
same-origin iframe can touch its parent frame, which is negligible.

This was a deliberate, user-approved choice (full fidelity over a sandboxed,
possibly-broken render). Documented here so a future reviewer recognizes it as
intentional rather than an oversight.

## Testing — `tests/test_server_preview.py`

- **Strengthen** the existing `test_html_preview`. It currently only asserts
  the filename appears in the body and passes against *source* output, so it
  does not actually test rendering. Update it to assert the **rendered** path:
  an `<iframe>` whose `src` points at the raw file URL.
- **Add** a test asserting the **source-toggle** control is present in the
  preview page.
- Existing text/image/pdf/media/json preview tests remain unchanged and must
  keep passing (HTML must not regress them).

## Out of Scope

- `.xhtml` and other non-`text/html` markup (keeps source preview).
- Sandboxing options / per-file render policy.
- Any change to how raw files are served (`serve_file` is unchanged).
