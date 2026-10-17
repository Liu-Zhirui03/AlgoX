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
under the frame explanation. Only the three working library entries link to
playgrounds; both searches remain planned.
