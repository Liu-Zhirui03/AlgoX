# Frontend

Browser HTML, CSS, and JavaScript belong here.
Keep styles, rendering, and playback logic in separate files as they are added.

`index.html` displays the algorithm library and connection status.
`assets/example.js` loads the sample input/output and source, and handles copy
and reload actions. It inserts code as text; no generated code is executed. `assets/styles.css` styles it and
`assets/status.js` fetches the status and handles retries. All assets are local.

Open the page through FastAPI using the [startup instructions](../Setup.md).
`bubble-sort.html` is the dedicated algorithm page. `renderer.js` draws Canvas
snapshots, `playback.js` owns timing and navigation, and `visualization.js` connects
them to the controls. Model generation remains planned.

The interface uses locally hosted Pixelify Sans for pixel-style headings and
larger VT323 terminal-style text for body copy and controls, with dark blue
backgrounds and light purple text. Font provenance and license
are in `assets/fonts/`. Code retains a monospace font to preserve alignment.

The playground uses a purple terminal-inspired layout: an ASCII wordmark,
dotted frame, Python editor, custom-input/results panel, and local connection
card. The editor and controls sit side by side on desktop and stack on mobile.
All fonts and assets remain locally hosted.

The home page is an algorithm library. The Bubble Sort library tile
navigates to `/algorithms/bubble-sort`. Its visualization block is below the
input/code playground; it uses the same submitted numbers. Layouts and controls
were checked in a browser down to 320px wide.

Connection status is shown only at the bottom of the home page. Algorithm
playgrounds do not load the connection-status script or render its panel.

The shared header icon is `assets/icons/algox-mark.svg`: a locally served vector
pixel monogram with a green A, blue X, shared junction, light gray tile, and
two accent pixels. The alternative graph icon is retained in
`assets/icons/algox-node-path.svg`.

The playground declares `data-algorithm-id`, `data-algorithm-title`, and
`data-renderer` on its input/code panel. `assets/example.js` requests
`/api/algorithms/{id}` and checks that the result matches the selected algorithm
and renderer. Default numbers come from the page input. This controller is for
integer-array input; other data structures need suitable controls and renderers.

`quick-sort.html` and `merge-sort.html` share the input, code, and playback scripts.
Quick Sort uses pivot and active-range overlays. Merge Sort enables a Canvas
buffer row with `data-show-buffer="true"`; its operation counter counts buffer
appends via `data-metric-action="take"`. Buffer contents are also shown as text
under the frame explanation. All five first-library entries link to working playgrounds.

`binary-search.html` and `hash-search.html` use `assets/search.js` for number,
target, and bucket-count validation, requests, results, and copying. They share
`visualization.js` and `playback.js` with the sorts. `assets/search-renderer.js`
draws binary bounds/midpoint/candidate cells or hash buckets and collision chains.
A text summary mirrors each frame, and long inputs scroll inside the Canvas frame.
Changing any search input pauses playback. Missing targets remain replayable.

`dijkstra.html` and `minimum-spanning-tree.html` share graph controls in
`assets/graph.js`, Canvas rendering in `assets/graph-renderer.js`, and playback
wiring in `assets/graph-visualization.js`. The latter reuses `TracePlayer`.
The MST page can be opened at `/algorithms/kruskal` or `/algorithms/prim`, with
the corresponding selector default. The first Greedy library entries link to
these playgrounds; remaining Greedy entries stay non-interactive and planned.

Graph input uses a node-label list and one weighted edge per line, such as
`A B 4`. The start input is hidden for Kruskal. Nodes keep a fixed circular
layout through playback, edges display input IDs and weights, and current,
selected, and rejected edges have distinct styles. Dijkstra adds distance labels;
text summaries mirror distances/predecessors or forest components and candidates.
Long graph drawings scroll inside their own frame on narrow screens.

The remaining Greedy pages are `huffman.html`, `activity-selection.html`, and
`fractional-knapsack.html`. They share custom-row parsing and code/result handling
in `assets/greedy.js`, a mode-specific renderer in `assets/greedy-renderer.js`, and
playback wiring in `assets/greedy-visualization.js` using the existing TracePlayer.

Huffman renders a forest and its 0/1 branches as minimum roots merge; assigned
codes appear beneath leaves. Activity Selection displays interval lanes ordered
by finish, with a last-finish guide and selected/rejected colors. Knapsack shows
a capacity bar and fractions taken for each item in ratio order. Frame summaries
mirror all three visuals as text. Editing inputs pauses playback. The library
keeps categories closed by default, omits counts and feature summaries, and links
to all completed Greedy entries.
