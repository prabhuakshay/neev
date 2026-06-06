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
          break-words"><span class="text-ink-400">Loading&hellip;</span></pre>
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
    window.addEventListener('load', function () {
      if (window.hljs && pre.textContent && !pre.querySelector('.hljs')) {
        hljs.highlightElement(pre);
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
