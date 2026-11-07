# The entity register

`docs/agents/integrations/billit.md` holds `register`; every key but `index` is a dotted path inside an entity's file.

| Key | Holds |
| --- | --- |
| `index` | the entity index's path in the repo |
| `block` | the entity's Billit details: `party_id`; `secret` when the vault item isn't `<entity>-billit`; optionally `reinvoiced_expenses` and `time_registration_descriptions` |
| `reads_codes` | whether the entity's books read Billit's codes |
| `numbering` · `prefix` · `payment_terms_days` | the sales invoice's number, its prefix and its due date's offset, for invoicing |
