# Rendered HTML Preview Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the **Preview** action on `.html`/`.htm` files render the page (full-fidelity iframe) inside neev's preview chrome, with a toggle to view syntax-highlighted source.

**Architecture:** A new `html_render.py` template module builds a preview page (modeled on the existing `html_markdown.py`): an `<iframe>` pointing at the raw file URL for the rendered view, plus a hidden source view that lazily fetches the raw text and highlights it with highlight.js. A new `serve_html_preview` handler in `server_preview.py` serves it, wired into `server.py`'s `do_GET` with a `text/html` MIME branch placed before the generic previewable-type branch.

**Tech Stack:** Python 3 stdlib (`http.server`, `string.Template`), Tailwind utility classes (existing `neev.css`), highlight.js via CDN. Zero new dependencies. Tooling: `uv`, `pytest`, `ruff`.

---

## File Structure

- **Create** `src/neev/html_render.py` — `render_html_preview()`: builds the full preview page (iframe + source toggle). New module, mirroring the `html_markdown.py` precedent, to keep `html_preview.py` under the 300-line limit.
- **Modify** `src/neev/server_preview.py` — add `serve_html_preview()` handler.
- **Modify** `src/neev/server.py` — import `serve_html_preview`; add the `text/html` routing branch in `do_GET`.
- **Modify** `tests/test_server_preview.py` — strengthen `test_html_preview`; add a source-toggle test.

`html_entries.py` is intentionally **unchanged** — HTML is already `is_previewable_type`, so the listing already emits the `?preview` affordance.

---

### Task 1: HTML render preview template (`html_render.py`)

**Files:**
- Create: `src/neev/html_render.py`
- Test: `tests/test_server_preview.py` (exercised end-to-end in Task 3)

- [ ] **Step 1: Create the template module**

Create `src/neev/html_render.py` with this exact content:

```python
"""HTML template for rendering .html file previews with a source toggle.

Renders the page in a full-fidelity iframe (no sandbox; runs scripts at the
neev origin, the same exposure as opening the raw file directly) and offers a
toggle to view the syntax-highlighted source.
"""

from string import Template


_RENDER_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en" class="antialiased">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>$filename &mdash; neev</title>
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="/_neev/static/neev.css">
  <link rel="stylesheet"
    href="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.11.1/build/styles/github.min.css"
    integrity="sha384-eFTL69TLRZTkNfYZOLM+G04821K1qZao/4QLJbet1pP4tcF+fdXq/9CdqAbWRl/L"
    crossorigin="anonymous">
  <script defer
    src="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.11.1/build/highlight.min.js"
    integrity="sha384-RH2xi4eIQ/gjtbs9fUXM68sLSi99C7ZWBRX1vDrVv6GQXRibxXLbwO2NGZB74MbU"
    crossorigin="anonymous"></script>
</head>
<body class="bg-surface-0 text-ink-700 font-sans min-h-screen
  flex flex-col">

  <header class="bg-surface-1/80 backdrop-blur-lg border-b
    border-surface-3 sticky top-0 z-10">
    <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8
      h-14 flex items-center justify-between">
      <div class="flex items-center gap-3 min-w-0">
        <a href="$parent_url" class="flex items-center gap-2
          text-ink-400 hover:text-sage-500 transition-colors
          duration-150 shrink-0" title="Back to folder">
          <svg class="w-4 h-4" aria-hidden="true" fill="none"
            stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round"
            stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
        </a>
        <span class="text-sm text-ink-800 font-semibold
          truncate">$filename</span>
      </div>
      <div class="flex items-center gap-2">
        <button id="source-toggle" type="button"
          class="inline-flex items-center gap-2
            px-3.5 py-2 bg-surface-1 text-ink-700 text-sm
            font-semibold rounded-lg border border-surface-3
            hover:bg-surface-2 active:bg-surface-3
            transition-colors duration-150 whitespace-nowrap">
          <svg class="w-4 h-4" aria-hidden="true" fill="none"
            stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round"
              stroke-width="2"
              d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"/>
          </svg>
          <span id="source-toggle-label"
            class="hidden sm:inline">Source</span>
        </button>
        <a href="$download_url"
          class="inline-flex items-center gap-2
            px-3.5 py-2 bg-surface-1 text-ink-700 text-sm
            font-semibold rounded-lg border border-surface-3
            hover:bg-surface-2 active:bg-surface-3
            transition-colors duration-150 whitespace-nowrap">
          <svg class="w-4 h-4" aria-hidden="true" fill="none"
            stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round"
              stroke-width="2"
              d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4
                M7 10l5 5 5-5 M12 15V3"/>
          </svg>
          <span class="hidden sm:inline">Download</span>
        </a>
      </div>
    </div>
  </header>

  <main class="max-w-5xl mx-auto w-full px-4 sm:px-6
    lg:px-8 py-8 flex-1">
    <div id="rendered" class="bg-surface-1 shadow-card
      rounded-xl overflow-hidden" style="height:85vh">
      <iframe src="$iframe_src" title="$filename"
        class="w-full h-full border-0 bg-white"></iframe>
    </div>
    <div id="source-view" class="bg-surface-1 shadow-card
      rounded-xl overflow-hidden hidden">
      <pre id="source-content"
        class="p-6 sm:p-10 text-sm text-ink-700 font-mono
          leading-relaxed overflow-x-auto whitespace-pre-wrap
          break-words"><span class="text-ink-400">Loading\\u2026</span></pre>
    </div>
  </main>

  <footer class="max-w-5xl mx-auto w-full px-4 sm:px-6
    lg:px-8 py-4">
    <p class="text-xs text-ink-300 text-center tracking-wide">
      served by
      <span class="font-medium text-ink-400">neev</span>
    </p>
  </footer>

  <script>
  (function () {
    var btn = document.getElementById('source-toggle');
    var label = document.getElementById('source-toggle-label');
    var rendered = document.getElementById('rendered');
    var sourceView = document.getElementById('source-view');
    var pre = document.getElementById('source-content');
    var loaded = false;
    var showingSource = false;
    btn.addEventListener('click', function () {
      showingSource = !showingSource;
      if (showingSource) {
        rendered.classList.add('hidden');
        sourceView.classList.remove('hidden');
        label.textContent = 'Preview';
        if (!loaded) {
          loaded = true;
          fetch($raw_url_js)
            .then(function (r) { return r.text(); })
            .then(function (text) {
              pre.textContent = text;
              if (window.hljs) hljs.highlightElement(pre);
            })
            .catch(function () {
              pre.textContent = 'Failed to load file content.';
            });
        }
      } else {
        sourceView.classList.add('hidden');
        rendered.classList.remove('hidden');
        label.textContent = 'Source';
      }
    });
  })();
  </script>
</body>
</html>"""


_RENDER_TEMPLATE_OBJ = Template(_RENDER_TEMPLATE)


def render_html_preview(
    filename: str,
    iframe_src: str,
    raw_url_js: str,
    parent_url: str,
    download_url: str,
) -> str:
    """Render an HTML page that previews an .html file.

    Args:
        filename: Display name of the file (pre-escaped for HTML).
        iframe_src: URL to the raw file for the iframe (pre-escaped for HTML
            attributes). Must have no query string so it renders inline.
        raw_url_js: URL to fetch raw source (JSON-encoded string literal).
        parent_url: URL of the parent directory (pre-escaped for HTML).
        download_url: URL for forced download (pre-escaped for HTML).

    Returns:
        Complete HTML page as a string.
    """
    return _RENDER_TEMPLATE_OBJ.safe_substitute(
        filename=filename,
        iframe_src=iframe_src,
        raw_url_js=raw_url_js,
        parent_url=parent_url,
        download_url=download_url,
    )
```

Note on `\\u2026`: in the file this is a literal backslash-u-2026 inside a Python string, which `string.Template` passes through verbatim into the HTML as the JS/HTML escape `…`? No — it is plain text inside a `<pre>`; write it as the literal characters you want shown. Use `&hellip;` instead to avoid confusion. **When typing the file, replace `Loading\\u2026` with `Loading&hellip;`.**

- [ ] **Step 2: Verify the module imports cleanly**

Run: `uv run python -c "from neev.html_render import render_html_preview; print(render_html_preview('a.html', '/a.html', '\"/a.html\"', '/', '/a.html?download')[:15])"`
Expected: prints `<!DOCTYPE html>` (no import or syntax error).

- [ ] **Step 3: Lint**

Run: `uv run ruff check src/neev/html_render.py`
Expected: PASS (no errors).

- [ ] **Step 4: Commit**

```bash
git add src/neev/html_render.py
git commit -m "feat(preview): add rendered HTML preview template"
```

---

### Task 2: Serve handler (`server_preview.py`)

**Files:**
- Modify: `src/neev/server_preview.py`

- [ ] **Step 1: Add the import**

In `src/neev/server_preview.py`, add this import alongside the existing
`from neev.html_preview import (...)` and `from neev.html_markdown import ...`
lines (keep imports sorted/grouped as ruff expects):

```python
from neev.html_render import render_html_preview
```

- [ ] **Step 2: Add the handler**

Append this function to `src/neev/server_preview.py` (after
`serve_markdown_preview`, before or after `serve_generic_preview` — placement
among siblings does not matter):

```python
def serve_html_preview(
    handler: "BaseHTTPRequestHandler", path: Path, request_path: str
) -> None:
    """Serve a page that renders an HTML file in an iframe, with source toggle.

    Args:
        handler: The HTTP request handler.
        path: Resolved filesystem path to the HTML file.
        request_path: The original URL path from the request.
    """
    filename = html.escape(path.name)
    raw_path = request_path.rstrip("/")
    iframe_src = encode_attr_url(raw_path)
    raw_url_js = script_safe_json(raw_path)
    download_url = encode_attr_url(raw_path) + "?download"
    parent = _parent_url(request_path)
    page = render_html_preview(filename, iframe_src, raw_url_js, parent, download_url)
    body = page.encode()
    handler.send_response(200)
    handler.send_header("Content-Type", "text/html; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)
```

`html`, `Path`, `encode_attr_url`, `script_safe_json`, and `_parent_url` are
already imported/defined in this module — no new imports beyond Step 1.

- [ ] **Step 3: Verify import wiring**

Run: `uv run python -c "from neev.server_preview import serve_html_preview; print('ok')"`
Expected: prints `ok`.

- [ ] **Step 4: Lint**

Run: `uv run ruff check src/neev/server_preview.py`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/neev/server_preview.py
git commit -m "feat(preview): add serve_html_preview handler"
```

---

### Task 3: Route HTML previews and test (`server.py`, tests)

**Files:**
- Modify: `src/neev/server.py:23` (import) and `src/neev/server.py:208-216` (routing)
- Test: `tests/test_server_preview.py`

- [ ] **Step 1: Write/strengthen the failing tests**

In `tests/test_server_preview.py`, replace the existing `test_html_preview`
method with these two methods (same `TestFilePreview`-style class the other
preview tests live in — match the surrounding indentation and `server`
fixture usage):

```python
    def test_html_preview_renders_in_iframe(self, server):
        """HTML preview renders the page in an iframe, not as source."""
        status, _, body = _get(server, "/page.html?preview")
        assert status == 200
        assert b"page.html" in body
        assert b"<iframe" in body
        assert b'src="/page.html"' in body

    def test_html_preview_has_source_toggle(self, server):
        """HTML preview offers a control to view the source."""
        _, _, body = _get(server, "/page.html?preview")
        assert b'id="source-toggle"' in body
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run pytest tests/test_server_preview.py -k html_preview -v`
Expected: FAIL — `test_html_preview_renders_in_iframe` fails because the
current text preview output contains `id="code-content"`, not `<iframe`.

- [ ] **Step 3: Add the import in `server.py`**

Change the existing line (`src/neev/server.py:23`):

```python
from neev.server_preview import serve_generic_preview, serve_markdown_preview
```

to:

```python
from neev.server_preview import (
    serve_generic_preview,
    serve_html_preview,
    serve_markdown_preview,
)
```

- [ ] **Step 4: Add the routing branch in `do_GET`**

In `src/neev/server.py`, the current block is:

```python
        if "preview" in query and is_markdown_file(resolved):
            serve_markdown_preview(self, resolved, request_path)
            return

        if "preview" in query:
            mime = get_mime_type(resolved)
            if is_previewable_type(mime):
                serve_generic_preview(self, resolved, request_path, mime)
                return
```

Replace it with (HTML branch goes BEFORE the generic `is_previewable_type`
check, because `text/html` also passes that check and would otherwise be
served as source):

```python
        if "preview" in query and is_markdown_file(resolved):
            serve_markdown_preview(self, resolved, request_path)
            return

        if "preview" in query:
            mime = get_mime_type(resolved)
            if mime == "text/html":
                serve_html_preview(self, resolved, request_path)
                return
            if is_previewable_type(mime):
                serve_generic_preview(self, resolved, request_path, mime)
                return
```

- [ ] **Step 5: Run the new tests to verify they pass**

Run: `uv run pytest tests/test_server_preview.py -k html_preview -v`
Expected: PASS (both tests).

- [ ] **Step 6: Run the full preview test file (no regressions)**

Run: `uv run pytest tests/test_server_preview.py -v`
Expected: PASS — all tests, including text/image/pdf/media/json previews.

- [ ] **Step 7: Lint**

Run: `uv run ruff check src/neev/server.py`
Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git add src/neev/server.py tests/test_server_preview.py
git commit -m "feat(preview): render HTML files in preview with source toggle"
```

---

### Task 4: Full suite + manual smoke check

**Files:** none (verification only)

- [ ] **Step 1: Run the full test suite**

Run: `uv run pytest -q`
Expected: PASS — no regressions anywhere.

- [ ] **Step 2: Lint the whole tree**

Run: `uv run ruff check .`
Expected: PASS.

- [ ] **Step 3: Manual smoke test**

```bash
mkdir -p /tmp/neev-smoke && printf '<h1>Hello</h1><p>It renders.</p>' > /tmp/neev-smoke/page.html
uv run neev /tmp/neev-smoke --port 8765
```
In a browser open `http://127.0.0.1:8765/`, click **page.html**'s preview.
Expected: the `<h1>Hello</h1>` renders inside the framed preview (not source).
Click **Source** in the header: the highlighted HTML source appears; clicking
again (now labelled **Preview**) returns to the rendered view. Stop the server
with Ctrl-C.

- [ ] **Step 4: Verify file-length compliance**

Run: `wc -l src/neev/html_render.py src/neev/server_preview.py`
Expected: both under 300 lines (`html_render.py` ~210, `server_preview.py` ~115).

---

## Self-Review

**Spec coverage:**
- Routing (`text/html`, after markdown, before generic) → Task 3 Step 4. ✓
- Handler with no-query iframe src / `?download` / source-fetch URL → Task 2 Step 2. ✓
- New `html_render.py` module with iframe + source toggle → Task 1. ✓
- No `html_entries.py` change → noted in File Structure (no task needed). ✓
- Security model (non-sandboxed iframe) → docstring in Task 1 Step 1; behavior verified in Task 4 Step 3. ✓
- Strengthen `test_html_preview` to assert rendered path → Task 3 Step 1. ✓
- Add source-toggle test → Task 3 Step 1. ✓
- `.xhtml` out of scope → covered by matching `mime == "text/html"` only. ✓

**Placeholder scan:** No TBD/TODO/"handle edge cases". The one `\\u2026` ambiguity is called out with an explicit instruction to use `&hellip;`. ✓

**Type/name consistency:** `render_html_preview(filename, iframe_src, raw_url_js, parent_url, download_url)` defined in Task 1 is called with the same arg order/names in Task 2. `serve_html_preview(handler, path, request_path)` defined in Task 2 is imported and called identically in Task 3. Element ids `source-toggle`, `source-toggle-label`, `rendered`, `source-view`, `source-content` are consistent between template (Task 1) and tests (Task 3). ✓
