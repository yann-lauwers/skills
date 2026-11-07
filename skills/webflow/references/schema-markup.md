# Schema markup

- The Pages API rejects schema markup that doesn't parse as JSON; the Designer's stored binding fails it twice — the `\}` escape, and an unquoted token where a number goes.
- The form that validates and renders keeps the `&quot;` entities, closes with a plain `}`, and sits inside a JSON string, so a bound Number renders as a string (`"5"`): `"numberOfBedrooms":"{{wf {&quot;path&quot;:&quot;<field-slug>&quot;,&quot;type&quot;:&quot;Number&quot;} }}"`.
