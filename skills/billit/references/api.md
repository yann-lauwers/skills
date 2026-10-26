# Calls no command covers

- `billit api <METHOD> <path>` reaches the JSON API, `billit portal <METHOD> <path>` the web portal; both handle the key and the login. Anything but `GET` is a write: ask the user first, with `--dry-run`.
- Billit's docs: `https://docs.billit.be/llms.txt` indexes every page; append `.md` to a page's URL for its text. The JSON API's spec: `https://api.billit.be/swagger/docs/v1`.
- A route in neither → try it live with `GET` before calling it unavailable.
- A route that works twice and recurs → it becomes a `billit` command.
