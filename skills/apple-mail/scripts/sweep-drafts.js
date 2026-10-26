// Moves every Drafts message whose subject is $MAIL_NONCE to its account's trash.
//
// Mail autosaves an open compose window every few seconds, so a window that wore
// the nonce across two autosaves leaves more than one copy behind — the multi-target
// case is the normal one, not the edge.
//
// Two rules this obeys:
//   - Removal is assigning `mailbox`, the way mail-trash.sh does, matching the
//     trash by name across providers. Mail.sdef does carry a `delete` command, but
//     `delete message i of box` does not compile, and the variable form is untested.
//   - Decide first, act second, re-fetching each target by id. One pass against a
//     Drafts mailbox holding live autosaves raised "Can't get object" partway
//     through; planted drafts moved inside the scan loop did not reproduce it, so
//     the cause is unconfirmed. Re-fetching by id means a reference that went stale
//     is skipped instead of aborting every target after it.
ObjC.import('Foundation')

const trashRaw = $.NSProcessInfo.processInfo.environment.objectForKey('MAIL_TRASH_NAMES')
const TRASH_NAMES = trashRaw && !trashRaw.isNil() ? ObjC.unwrap(trashRaw).split('\n').filter(Boolean) : []

function run() {
  const raw = $.NSProcessInfo.processInfo.environment.objectForKey('MAIL_NONCE')
  const nonce = raw && !raw.isNil() ? ObjC.unwrap(raw) : ''
  if (!nonce) return 'no nonce given'

  const Mail = Application('Mail')
  const moved = []

  for (const account of Mail.accounts()) {
    let trash = null
    try {
      trash = account.mailboxes().find((b) => TRASH_NAMES.includes(b.name().toLowerCase()))
    } catch (e) {
      continue
    }
    if (!trash) continue

    for (const box of account.mailboxes()) {
      let name = ''
      try {
        name = box.name()
      } catch (e) {
        continue
      }
      if (!/draft|brouillon/i.test(name)) continue

      const ids = []
      try {
        for (const m of box.messages.whose({ subject: nonce })()) ids.push(m.id())
      } catch (e) {
        continue
      }

      for (const id of ids) {
        try {
          const m = box.messages.whose({ id: id })()[0]
          if (!m) continue
          m.mailbox = trash
          moved.push(id)
        } catch (e) {
          /* already gone, or the account refused the move */
        }
      }
    }
  }
  return moved.length ? 'trashed ' + moved.length + ': ' + moved.join(',') : 'nothing matched'
}
