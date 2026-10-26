# House — Design System

## 1. Visual Theme & Atmosphere

A quiet, precise system for pages people read in under a minute beside a code editor —
reports, dashboards, handoffs, the occasional landing page — and for the apps built on the
same tokens. Density is a feature: a table and a status badge are the proving ground, not a
hero. Both themes are complete and equal; neither is the "real" one.

Colour is scarce and it means something. One brand hue carries the primary action and the
selected state; four status hues carry success, warning, danger and information; everything
else is a cool neutral scale. Identity lives in the tokens and the components — recognisable
with the content removed — never in decoration.

## 2. Color Palette & Roles

Every colour is a step on a 12-step perceptual scale, and every step has one job:
1 page ground · 2 subtle ground · 3 element · 4 element hover · 5 element active ·
6 separator · 7 element border · 8 border hover · 9 solid · 10 solid hover ·
11 low-contrast text · 12 high-contrast text.

| Token | Light | Dark | Role |
| --- | --- | --- | --- |
| `--background` | `#f6f9fd` | `#14181b` | page ground |
| `--foreground` | `#1d2125` | `#e8edf4` | body text |
| `--card` | `#fbfdff` | `#1a1e22` | raised surface — lifts off the page in both themes |
| `--muted-foreground` | `#565b61` | `#b8bec5` | secondary text |
| `--primary` | `#008282` | `#009393` | brand solid — primary button, link, the one selected thing |
| `--primary-foreground` | `#fbfdff` | `#14181b` | text on primary |
| `--accent` | `#e7ecf1` | `#292d32` | hover and selected surface — **not** the brand colour |
| `--border` | `#d6dce3` | `#3a3f44` | decorative separator |
| `--input` | `#8b9198` | `#6a7076` | form-control edge, solved to 3:1 |
| `--ring` | `#008282` | `#009393` | focus ring, solved to 3:1 |
| `--destructive` | `#c13c3b` | `#da534f` | danger solid |
| `--success` | `#3b834e` | `#4a925c` | success solid |
| `--warning` | `#f5ae39` | `#f5ae39` | warning solid — takes dark text |
| `--info` | `#3772bb` | `#4682cc` | information solid |

Each status also has `-subtle` (step 3, a tinted ground) and `-text` (step 11, text on that
ground or on a card). A badge takes the soft form — `-subtle` under `-text` — everywhere
by default; the solid form is kept for the one verdict a page exists to state.

`--accent` is the hover and selected **surface**, never the brand colour — an "accent button"
filled with it is a grey button. The brand is `--primary`.

`--input` is a solved value, never a lighter `--border`: an input's edge identifies it, so it
clears 3:1 against every ground (WCAG 2.2 § 1.4.11); `--border` separates, and need not.

**Chart series** — eight slots, one hue per slot in both themes, each stepped for its own
ground. Solved inside each theme's
lightness band against the same gates the data-visualisation validator runs. Worst adjacent pair,
OKLab ΔE×100, light / dark: colour-blind 10.8 / 14.9 (target 8, floor 6),
normal vision 22.7 / 25.9 (floor 15). The first three also clear both on every
pair, so a scatter, bubble chart or map may use them; past three, those forms fold or facet.
Take the slots in order and never drop one from the middle; slots 7 and 8 ship with a shape
encoding alongside the colour.

Light: `#009b9b` · `#9239cf` · `#e84700` · `#0079a4` · `#9e7300` · `#407fff` · `#548d2e` · `#a94777`
Dark: `#009090` · `#b560f6` · `#e74700` · `#009dd4` · `#b88700` · `#3d67bb` · `#458800` · `#ed439d`

**Sequential** `--chart-seq-1…5` — the brand hue, from near the ground to far from it, for
magnitude; in light that runs light to dark, in dark it runs dark to light. Its first step sits
too close to the ground to stand alone as a mark.
**Ordinal** `--chart-ord-1…5` — five ranks on the brand hue, from the solid step to the strong-text
step, every one of which clears the non-text floor against a card, for a funnel, a ranked bar, a
podium. Rank 1 is the solid step and rank 5 the strong-text step, so the ranks read as rising contrast against the ground — lightest first in light, darkest first in dark. **Diverging** `--chart-div-1…5` — danger through a neutral
midpoint to information, for above and below a baseline. Status colours are reserved for status
and never stand in for a series.

## 3. Typography Rules

- **Sans:** Geist — every surface. Weights 400, 500, 600, 700.
- **Mono:** Geist Mono — code, numeric table columns, identifiers, timestamps, a figure a reader compares down a column.
- **Editorial:** Instrument Serif italic — report and deck title cards only; never on a product surface.

All three resolve on Google Fonts — `https://fonts.googleapis.com/`, the stylesheet host a published artifact
admits. The sans is neutral: the palette and the density carry the character, never the
letterforms.

| Step | Size | Leading | Tracking | Weight | Carries |
| --- | --- | --- | --- | --- | --- |
| `2xs` | 11px | 1.4 | `0.04em`, uppercase | 500 | eyebrow, tile label, capture label |
| `xs` | 12px | 1.45 | `0.02em` | 400 | caption, footnote, legend, timestamp |
| `sm` | 13px | 1.5 | `0` | 400 | dense table cell, button label, secondary meta |
| `base` | 15px | 1.6 | `-0.011em` | 400 | body |
| `lg` | 17px | 1.55 | `-0.011em` | 400 | lead paragraph, standfirst |
| `xl` | 20px | 1.3 | `-0.02em` | 600 | section heading |
| `2xl` | 24px | 1.25 | `-0.02em` | 600 | panel heading |
| `3xl` | 30px | 1.1 | `-0.025em` | 600 | stat value, page heading |
| `display` | `clamp(2.75rem, 6vw, 4.5rem)` | 1.02 | `-0.03em` | 600 | hero, deck title |

A label sits two steps below the text it labels — a badge beside body copy takes `xs` while
the copy takes `base`. Uppercase with wide tracking belongs to `2xs` alone, and only where the
text is a structural marker rather than something read: an eyebrow, a stat tile's label, the
label over a code capture. A table header runs `xs` sentence case, and every other step runs
sentence case with the tracking its token carries. A step sets the type; the component sets the
box, so a label growing or shrinking leaves the box where it was.

Body copy caps at 68ch — on `p`, `li` and the standfirst, never on the column that holds
cards and tables.

## 4. Component Stylings

| Component | Spec |
| --- | --- |
| Button | 36px tall (32 small, 44 large), radius `--radius-control` (`--radius-md`), 16px padding-x. Variants: primary, secondary, outline, ghost, destructive, link. A solid button carries `--shadow-control` — a lit top edge, and in light a 1px ground shadow — never a gradient; outline carries `--shadow-outline`, ghost and link none. Press scales to 0.97; hover colours apply only under `@media (hover: hover)`. |
| Input | 36px, radius `--radius-control` (`--radius-md`), 1px `--input` edge on `--card`, placeholder in `--muted-foreground`. Focus adds the ring and swaps the edge to `--ring`. Invalid: `--destructive` edge **plus** a message in `--destructive-text` — never hue alone. |
| Card | `--card` fill, 1px `--border` on all four sides, `--radius`, 24px padding, `--shadow-card` (none in dark, where the border carries the separation). **No coloured edge** — no accent bar, no tinted top, no left rail, whatever the colour encodes. Encode the difference inside — a badge under the heading where the label is two or three words, the heading's own wording where it is longer; a label that wraps to a second line is a caption at `2xs` uppercase in `--muted-foreground` with no fill. A card inside a card takes `--layer-2`, one inside that `--layer-3`, and neither takes a shadow. |
| Badge | fully round, 20 / 24 / 28px tall, sentence-case label weight 500 at `xs` (`sm` on the large size), never an uppercase tracked label. **Every small labelled box is this component** — a verdict, a status, a tag, a count, a pill, a chip, a metadata label — one rule, three sizes, never a second name. Three small boxes are not badges because they are not labels: a keyboard key is Kbd, a person is Avatar, a hover hint is a tooltip. Soft by default — `-subtle` ground, `-text` label, a hairline ring in the same hue so the edge holds on a card. Solid only for the one verdict a page exists to state; never two solid badges on one screen. A 6px `currentColor` dot before the label states the status in form as well as hue; a badge with no status takes `--muted` under `--muted-foreground`. Small inside a table cell or a sentence; default beside body copy, in a header row, on a card; large once per page. |
| Table | header on `--muted` at `xs` weight 500 in `--muted-foreground`; 12px × 16px cell padding; 1px `--border` between rows, no vertical rules; rows hover on `--accent`; numeric columns right-aligned in mono with tabular numerals. |
| Stat tile and strip | tile: `2xs` uppercase label, value at `3xl` weight 600 with tabular numerals, delta at `sm` in `--success-text` / `--destructive-text` with an arrow. A strip is several tiles reading as one object — equal fractions across the content width, up to 6 cells; seven or more figures is a table. One hairline between cells running the cell's full height, the strip's own border and radius closing it; the cells carry 20px padding and nothing else. |
| Focus | 2px `--ring`, 2px offset, on every interactive element. |
| Empty state | 32px Lucide icon in `--muted-foreground`, `lg` heading at weight 500, one line of body copy, at most one action. It names what is missing and the one action that fills it. |
| Code capture | a block on `--term-bg` in `--term-ink` at `sm` mono, `--radius` corners, its own horizontal scroll, no border — the ground is the separation. Its label sits above, outside the object, as `2xs` mono in `--muted-foreground` naming the command or path, the outcome pushed right. A highlight tints the run in `--primary` under unchanged ink with `box-decoration-break: clone`, padding at or under 1px vertical and 3px horizontal so the monospace columns stay aligned. |
| Callout | the one place a coloured ground is right, because it encodes a type — info, success, warning, danger: that status's `-subtle` ground under its `-text`, a 16px icon, no border. |
| Select, textarea | the input's edge, ground, radius, focus ring and invalid state, on a native `<select>` (its chevron drawn in `--muted-foreground`, never an image) and a `<textarea>` at least 96px tall, resizable vertically. Same `.field` label, hint and error as an input. |
| Checkbox, radio, switch | 16px boxes on `--card` with the `--input` edge, filling `--primary` when checked with a `--primary-foreground` mark; a radio is round. A switch is a 36×20 pill track — `--input` off, `--primary` on — with a `--card` thumb 4px inside it; its label sits to the right. Every one carries the 2px ring on focus, and a disabled control fades to 0.5 with its label. |
| Tabs | a list on `--muted` at the control radius, each tab 28px tall at `sm` weight 500 in `--muted-foreground`; the selected tab lifts onto `--card` in `--foreground` with `--shadow-outline`. Tabs switch views inside one page; they never stand in for a caller's pages. |
| Breadcrumb | `sm` links in `--muted-foreground`, a small chevron between, the current page in `--foreground` and not a link. It shows where a page sits, never where to go next. |
| Side navigation | the sidebar tokens: `--sidebar` ground, a 1px `--sidebar-border` on its right, `sm` items `--control-sm` tall with a 16px icon in `--muted-foreground`; the current item on `--sidebar-accent` at weight 500. An eyebrow groups sections. |
| Dialog | a `--popover` panel at most 440px wide on a scrim of `--term-bg` at 60% — dark in both themes —, 1px `--border`, `--radius-lg`, `--shadow-popover`, card padding: a `lg` weight-600 title, a `sm` muted description, actions right-aligned in the footer with the primary action last. One dialog at a time, and it is in the markup, shown by state. |
| Popover, menu, tooltip | a popover is the same surface at `--radius-md`, at most 320px wide, with 12px padding; a menu is one with 4px padding holding items at `sm`, `--control-sm` tall less the padding, an optional `2xs` uppercase label, a hairline separator, a shortcut in a `kbd` on the right, `--accent` under the active item, `--destructive-text` on a destructive one. A tooltip inverts — `--foreground` ground, `--background` text at `xs`, `--radius-sm` — so it reads over anything, and holds one line or two. A chart's hover tooltip is a popover, drawn per the Charts reference, never this inverted one. |
| Progress | a 8px `--muted` track, fully round, with a `--primary` fill whose width is the value; a status fill when the bar reports a status. The number sits beside it as text — the bar alone is never the only reading. |
| Skeleton | a `--muted` block the shape of the content it stands for, pulsing opacity alone over `--duration-pulse` — the one loop the system carries; it is shown before data, never as decoration, and `prefers-reduced-motion` stops the pulse. |
| Toast | a popover surface at most 380px wide: an 18px icon, a weight-500 title, one muted line, one action. It reports something that just happened and holds no verdict a page exists to state — that is the solid badge's. |
| Avatar | a fully round `--muted` disc at a control height — `--control-sm`, `-md`, `-lg` — carrying initials in mono at `xs`, or an image; stacked avatars overlap by 8px with a 2px `--card` ring so each edge reads. |
| Kbd | a keyboard key: `2xs` mono on `--muted`, a 1px `--border` with a 2px bottom, `--radius-sm`. |
| Separator | a 1px `--border` line, horizontal with 16px above and below, or vertical at 20px tall inline — rung 2 of § 5, and only where whitespace was not enough. |

Icons are Lucide, stroke 1.5 on marketing surfaces and 2 on product ones.

## 5. Layout Principles

Tailwind's 4px scale is the spacing scale. Named rhythms: card padding 24px, tile
padding 20px, product section 32px, marketing section 96px.

Spend separation from the cheapest rung that works; reach a rung only when the one below it
fails:

| Rung | Device | Reach for it when |
| --- | --- | --- |
| 1 | whitespace | siblings sit in a flow and read as a list |
| 2 | a hairline between siblings | the run is long enough that the eye loses the row |
| 3 | a change of ground — a fill, or a dark block on a light page | the content is of a different kind from the prose around it |
| 4 | a closed 1px border | the object holds several kinds of content at once |
| 5 | a tint across the whole surface | exactly one object on the page is exceptional |

An element that already carries a ground carries its separation, and takes no border on top.
A coloured edge on one side of a container encodes a **type** — warning against note, added
against removed — and appears where that type exists and varies between siblings; every other
block takes its separation from the rungs above. Marking one object as exceptional uses a
device that says what it is: a label, a badge, an icon, or rung 5.

## 6. Depth & Elevation

Three layers, named by role: `--layer-1` on the page, `--layer-2` on a surface,
`--layer-3` on a surface on a surface. Light uses `--shadow-card` on layer 1 and `--shadow-popover`
on overlays; dark drops shadow and lets the border separate.

## 7. Do's and Don'ts

- Do address colour only through a token. A hex typed into a rule renders right in one theme and wrong in the other two.
- Do keep the variable names. Values are the identity's to change; `--background` is never renamed, and a colour the palette needs and the set does not name is added beside it, never instead of part of it.
- Do encode state in form as well as hue — a dot, an icon, a word in a box.
- Do ship the token block whole. It carries three theme states: an explicit choice stamps `data-theme` on the root, the viewer's own setting is answered by the media query, and an explicit light choice wins over it. `[data-theme]` also scopes — any element carrying it re-themes its own subtree.
- Do commit to one world by stamping the root and saying so. A page built dark still pastes the whole block; `<html data-theme="dark">` is what commits it.
- Don't put a coloured edge on a card.
- Don't use `--accent` as the brand colour; it is the hover surface. The brand is `--primary`.
- Don't load an image from a remote host inside a published artifact — it renders blank. Name the gap.
- Don't animate layout. Motion moves transform and opacity; a state change may cross-fade colour, border or shadow over `--duration-fast`, and nothing else moves. Enter and exit run `--duration-fast` to `--duration-base` on `--ease-out`; anything past `--duration-slow` (300ms) is a scroll-linked sequence rather than a transition. Exits run about 20% faster than entrances, and repeated keyboard actions animate nothing. The loading skeleton's `--duration-pulse` is the one loop, and `prefers-reduced-motion` stops it.

## 8. Responsive Behavior

Content columns are fluid; prose caps at 68ch. Tables scroll inside their own container;
the page never scrolls sideways. Touch targets hold 44px.

A table of contents lists the headings of the page it sits on, and nothing else. It appears only
when the page has four or more headings at the levels it carries — `h2`, and `h3` where the `h2`
sections are themselves long — runs past about three screens at its reading width, and the
page's author neither opted out nor built contents of its own. At ≥1024px it is a sticky rail on
the **right** of the content with the section being read marked; the left is where a document's
own outline lives. Under that it is one closed "On this page" disclosure in the flow under the
title, never sticky, below any parts list or step indicator the page already shows. A page with
no headings gets no contents and no empty toggle. It never replaces, merges with or restyles the
page's own paging: an outline, a parts list, previous/next links and a step indicator move
between pages, a table of contents moves within one, and they coexist as separate controls.

## 9. Agent Prompt Guide

> Style this with the House design system. Use only its CSS variables (`--background`,
> `--foreground`, `--card`, `--primary`, `--muted-foreground`, `--border`, `--ring`, and the
> status and chart tokens). Geist for text, Geist Mono for numbers and code. Both
> themes. Cards have a 1px border on all four sides and no coloured edge. Badges are fully round
> and soft — a tinted ground under that status's text colour; solid only for the page's one verdict.

> Build a dashboard in the House system: stat tiles in a strip, a table with a status-badge
> column, one chart on `--chart-1`…`--chart-4`, an empty state for the no-data case.

> Build a settings form in the House system: a select, two switches, a textarea, a tabs
> list over three panels, and a confirm dialog on the destructive action — shown open in the
> markup for the capture.

Measured contrast for every text pair: `contrast.md`.
