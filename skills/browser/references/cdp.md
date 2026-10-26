# CDP — the route that reaches a signed-in tab here

## Reaching it

- `pw --live` attaches to `profile_browser` over CDP at `cdp_endpoint`, and answers only when the browser was launched with the debugging port:

```
curl -s <cdp_endpoint>/json/version       # a Browser field → pw --live works
open -a "<profile_browser>" --args --remote-debugging-port=<cdp_endpoint's port>   # ⌘Q first: macOS ignores --args for a running app
```

- Ask before quitting the browser: relaunching closes every window the person has open; the tabs restore on relaunch.
- `pw --live` times out while `/json/version` answers → `connectOverCDP` hangs attaching to every target a busy browser holds; drive one page over raw CDP: `GET /json/list`, pick the target whose `url` you want, open its `webSocketDebuggerUrl` with Node's global `WebSocket`, and send `Runtime.evaluate` with `returnByValue: true`.

## The session's tab

- **Read the signed-in account from the site's own account menu with `pw --live snapshot` before acting; a different account than the identity named → stop, ask the person to bring that identity's profile window forward, and re-attach; never proceed under the other account.**
- This session's tab → the index each attach names on stderr (`pw: this session's tab is <index>: …`), or `tab-list`'s `(current)` mark while attached; never its URL, often a page the person already has open.
- Never navigate, reload or close a tab that was already open: `pw --live tab-close <index>` can reach one, so `tab-list` first, and close only the tab you opened.
- Finish while still attached: `pw --live tab-close` with no index closes this session's tab, then `pw --live detach`; any command after the close lands in a tab the person owns.
- A tab an earlier attach left open → close it only when no tab the person had open shares its URL; otherwise leave it and name it in the reply.

## Reading

- A live authenticated page → `innerText` and a bounded link list over raw HTML, since a portal's own links routinely carry session tokens in their query strings; treat any token that surfaces as spent.
