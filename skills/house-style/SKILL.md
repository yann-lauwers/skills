---
name: house-style
description: "Gives a generated page, chart, deck, dashboard or published Artifact the house look — one brand, the house tokens by CSS variable name — and changes the house system itself. Use on 'house style', 'house palette', 'brand colour', before writing any standalone HTML page or stylesheet. Not for an unbuilt screen's look or judging a shipped interface — /impeccable ."
allowed-tools: Read, Grep, Glob, Write(**/*.html), Write(**/*.css), Edit(**/*.html), Edit(**/*.css)
---

# House Style

A page this setup generates wears one brand: the house tokens, referenced by CSS variable name. The caller decides content, order, page count and behaviour; house-style decides look only, and a restyle keeps the structure it found.

## Whose brand

Route on the output's subject, never on cwd.

- A published Artifact, an analysis, a report, scratch work → house.
- A project's own product screens or mockups → the project's brand, read from its repo; published as an Artifact → house chrome around it, the project's values inside a `[data-theme]` scope under the same variable names; the project's own token file replaces the house block whole, never merged; look in the request, then its canon, then a tokens or theme file.
- No project brand resolves → house, and the reply says so.

## In a house page

1. Paste `css/tokens.css` whole into a `<style>` at the top; pasted, never linked: nothing serves a local file beside a published page. It carries light, dark and the OS preference.
2. Components wanted → paste the files under `css/components/` they need beneath it: `controls` (button, input, badge), `surfaces` (card, table, stat, empty state, code, callout), `forms`, `navigation` (tabs, breadcrumb, side nav, overlays), `feedback` (progress, toast, avatar, prose, page rail); `controls.css` first, since it carries the box-sizing reset.
3. Faces → `<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&family=Geist+Mono:wght@400;500&family=Instrument+Serif:ital@0;1&display=swap" rel="stylesheet">`; remote stylesheets only from hosts `references/stack.md` admits.
4. Write only layout: every colour, size, radius and duration is `var(--…)`, names in `references/tokens.md`. A hex outside the pasted block is a departure.
5. One world → stamp `data-theme="dark"` (or `light`) on `<html>`; the stamp beats the viewer's setting.

Rules in prose: `references/design.md`. Libraries, script tags and what an Artifact may load: `references/stack.md`. An app with Tailwind v4 and shadcn/ui imports `css/tokens.css` and `css/theme.css` in place of shadcn's generated blocks.

## Traps

- Rename no variable; a colour the set lacks is added beside the set.
- Several caller pages in one published file → one view each.
- Standalone HTML opens with `<!doctype html>`, charset and viewport, or it renders in quirks mode.
- No image from an external host: the CSP renders the slot empty. Use inline SVG, CSS or a `data:` URI.

## Changing the system

1. Edit `css/tokens.css` for a value, a file under `css/components/` for a component, `references/design.md` for a rule; a token renamed or added updates `references/tokens.md` in the same change.
2. A text colour changed → its pair still clears WCAG 2.2 AA in both modes; `references/contrast.md` records each pair's measured ratio and takes the new one.
3. Publish a test page with the edited files and look at both themes before committing.
