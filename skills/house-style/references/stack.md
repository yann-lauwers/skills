# Stack

Which library draws which job, and how it loads in a published artifact. Every URL below sits on
a host the CSP admits, and every tag carries the hash of the bytes the CDN served when the row
was recorded, so a CDN that serves different bytes is refused rather than executed. A row records
no hash where none can hold — a URL that tracks the latest of a major, or an ESM import map, which
carries no integrity attribute — and its own note says which; those rows are what the audit
excuses. A repo
installs the same libraries through its bundler; the project column says what changes there.

## What an artifact may load

| Asset | Admitted from |
| --- | --- |
| script | `https://cdnjs.cloudflare.com/`, `https://cdn.jsdelivr.net/npm/`, `https://cdn.tailwindcss.com`, `https://code.jquery.com/` |
| stylesheet | `https://fonts.googleapis.com/` |
| font file | `https://fonts.gstatic.com/` |
| `fetch`, XHR, WebSocket | `same-origin`, `https://fonts.googleapis.com/`, `https://fonts.gstatic.com/` |
| image, media | nothing — inline it |

## Which library, for which job

| Job | Default | Escalation | When | In a repo |
| --- | --- | --- | --- | --- |
| Styling | Tailwind 4 | — | — | Tailwind v4 through the bundler |
| Components | House components | — | — | shadcn/ui on Base UI — the same spec, as React components |
| Icons | Lucide 1.39.0 | — | — | lucide-react |
| Motion | Motion 11.11.13 | GSAP 3.15.0 | staged multi-track scroll choreography — pinned, scrubbed, labelled, seekable; one pinned scrub takes native CSS scroll-timeline and no library | motion; gsap on the same trigger |
| Charts | Recharts 3.10.1 | ECharts 6.1.0 | sankey, treemap, geo, graph, candlestick, more than 50k points, or a page that carries no React | Recharts through shadcn's Chart; ECharts on the same trigger |
| 3D | three.js 0.160.0 | — | — | three through the bundler — the addons resolve, a .glb loads from public/, no import map |
| Physics | Matter.js 0.20.0 | — | — | matter-js |
| Designer-authored animation | Lottie 5.12.2 | Rive 2.19.4 | the asset is a .riv with a state machine rather than an After Effects export | the same players, bundled |
| Generative canvas | p5.js 1.9.0 | — | — | p5 |
| Slides | Hand-rolled slides | — | — | reveal.js |

An explicit instruction in the request outranks every row, and a project that already does
something different is followed.

## Tags, in load order

### Styling — Tailwind 4

```html
<script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
```
the URL tracks the latest 4.x, so its bytes move and no hash can hold.

### Icons — Lucide 1.39.0

```html
<script src="https://cdn.jsdelivr.net/npm/lucide@1.39.0/dist/umd/lucide.min.js" integrity="sha384-ueMZWsJB99p1SCMICHGDK/IL9ZKGuI1twYOPLoFlYI0sDz25ILSwq6W82/LsYvlt" crossorigin="anonymous"></script>
```
Then `lucide.createIcons()`.
absent from cdnjs; the stroke width is 2 on product surfaces and 1.5 on marketing ones, on one 24px grid.

### Motion — Motion 11.11.13

```html
<script src="https://cdn.jsdelivr.net/npm/motion@11.11.13/dist/motion.js" integrity="sha384-czaB7zH9slIhvFgUxhO8sSnYf4cnCeV2N3zOvDnNKFzRKu5AwqDKEZlCLsaQkoop" crossorigin="anonymous"></script>
```
cdnjs carries no motion UMD.

### Motion — GSAP 3.15.0 (escalation)

```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js" integrity="sha384-XmJ9SoHtVOHoQUcKvFAzVXwdkKo1Ie3bhmSoIAkcdsHGaIrVJIkmozyq0FJeb/Ly" crossorigin="anonymous"></script>
```
jsDelivr only; cdnjs carries neither ScrollTrigger nor Flip. SplitText, DrawSVG and MorphSVG are GSAP Club and load from no admitted host.

### Charts — Recharts 3.10.1

```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/react/18.3.1/umd/react.production.min.js" integrity="sha384-DGyLxAyjq0f9SPpVevD6IgztCFlnMF6oW/XQGmfe+IsZ8TqEiDrcHkMLKI6fiB/Z" crossorigin="anonymous"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.3.1/umd/react-dom.production.min.js" integrity="sha384-gTGxhz21lVGYNMcdJOyq01Edg0jhn/c22nsx0kyqP0TxaV5WVdsSH1fSDUf5YJj1" crossorigin="anonymous"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/react-is/18.3.1/umd/react-is.production.min.js" integrity="sha384-XYVQ7LtYqgha4ByzNRLR6NHo9p0yVDvmTNuQkiIweU0U8WqLWBkH1L771VlP6fYx" crossorigin="anonymous"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/recharts/3.10.1/Recharts.min.js" integrity="sha384-+A7g/u3B+gLbMJBvixOoipyvnsutGtptbgLWgAQkxNxY++X+G4X61dOYURF/Ff14" crossorigin="anonymous"></script>
```
renders SVG, so a var(--chart-1) stroke resolves in the document and both themes come free.

### Charts — ECharts 6.1.0 (escalation)

```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/echarts/6.1.0/echarts.min.js" integrity="sha384-C2iskrW/uPW46KzOjrvJIQo4YkV8lkD+QS0CrDN18IIPIpT/g2USu8bTP3nvmIAD" crossorigin="anonymous"></script>
```
renders to canvas, where no custom property reaches: its colours go into a JS theme object, one per theme.

### 3D — three.js 0.160.0

```html
<script type="importmap">
{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
"three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"}}
</script>
```
ESM through an import map, because the addons ship only as ESM under examples/jsm/ (examples/js/ answers 404 since r150) and a module graph carries no integrity attribute. The UMD build at build/three.min.js defines window.THREE and reaches no addon.

### Physics — Matter.js 0.20.0

```html
<script src="https://cdn.jsdelivr.net/npm/matter-js@0.20.0/build/matter.min.js" integrity="sha384-ZRKYEXtLBVeqs9z1WxyeKutCqnkqolS/r1EUWuoUpG4ZKbnRAIXnHhHdnNuiB6CL" crossorigin="anonymous"></script>
```

### Designer-authored animation — Lottie 5.12.2

```html
<script src="https://cdn.jsdelivr.net/npm/lottie-web@5.12.2/build/player/lottie.min.js" integrity="sha384-J8C0MvgX4WP58J4N2W99vCKd2J6z99ynOJ5bEfE6jeP7kVTW1drYtv/jzrxM5jbm" crossorigin="anonymous"></script>
```
a player: it needs an After Effects export, inlined as animationData.

### Designer-authored animation — Rive 2.19.4 (escalation)

```html
<script src="https://cdn.jsdelivr.net/npm/@rive-app/canvas@2.19.4/rive.js" integrity="sha384-LhiDr0ZHU97AhxmsVlxyDZQoc1PDFzs67VdZ281CqTjYHabu3GuSdlrcZYeWJUu0" crossorigin="anonymous"></script>
```
a player: it needs a .riv a designer made, inlined as a data: URI.

### Generative canvas — p5.js 1.9.0

```html
<script src="https://cdn.jsdelivr.net/npm/p5@1.9.0/lib/p5.min.js" integrity="sha384-bOv+b6RV+dlZvdQAx6+cJ+FK9ab8JCSVWyJ1JPhMVQjPW+4C8V2cOKK+qZDfnRnx" crossorigin="anonymous"></script>
```

## Also admitted

### Tailwind play CDN 3

```html
<script src="https://cdn.tailwindcss.com"></script>
```
the v3 play CDN, with ?plugins=typography when the prose plugin is wanted; floating like the v4 URL, so no hash. Catalogued, not a job default.

### D3 7.9.0

```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js" integrity="sha384-CjloA8y00+1SDAUkjs099PVfnY2KmDC2BZnws9kh8D/lX1s46w6EPhpXdqMfjK6i" crossorigin="anonymous"></script>
```
a custom mark no chart library draws; catalogued, not a job default.

### Observable Plot 0.6.17

```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js" integrity="sha384-CjloA8y00+1SDAUkjs099PVfnY2KmDC2BZnws9kh8D/lX1s46w6EPhpXdqMfjK6i" crossorigin="anonymous"></script>
<script src="https://cdn.jsdelivr.net/npm/@observablehq/plot@0.6.17/dist/plot.umd.min.js" integrity="sha384-JUpn2GgRr0gxU0xOBd8D8P634jhRCwobtG8G2MMEkX1RnGJ7/FJNnuukpfT+H2w1" crossorigin="anonymous"></script>
```
catalogued, not a job default.

### GSAP ScrollTrigger 3.15.0

```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js" integrity="sha384-XmJ9SoHtVOHoQUcKvFAzVXwdkKo1Ie3bhmSoIAkcdsHGaIrVJIkmozyq0FJeb/Ly" crossorigin="anonymous"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/ScrollTrigger.min.js" integrity="sha384-wl5TeDVvOWt30Pbf8aSo2ZrzsOjddu3avOBvHe+p+OhJt9gP6w9YXmDkN5DK2/dF" crossorigin="anonymous"></script>
```
Then `gsap.registerPlugin(ScrollTrigger)`.

### GSAP Flip 3.15.0

```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js" integrity="sha384-XmJ9SoHtVOHoQUcKvFAzVXwdkKo1Ie3bhmSoIAkcdsHGaIrVJIkmozyq0FJeb/Ly" crossorigin="anonymous"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/Flip.min.js" integrity="sha384-LY8cG/IUULu4u3V3AhwWBt01HIuO/hlekjkqgBx0DOJ/oquEL0Qk2L6qy+1QeRZM" crossorigin="anonymous"></script>
```
Then `gsap.registerPlugin(Flip)`.
