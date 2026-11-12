# The item spec

Written in the reply for the user to act on, no value anywhere in it.

- Item → a Login item titled `<entity>-<tool>`, lowercase-hyphenated; `<entity>` owns the account: a project, a business or a person.
- The credential itself → the password field; anything else → username, or a custom field with a lowercase name.
- Per field → where its value comes from: the app's generator with the length and character set the consumer needs, a vendor console page, an existing item, a local file by path.
- A rotation or a retitle lists only the fields that change.
- Done when the user says it exists and one read of the title returns a value of the spec's length; no length known → non-empty plus one authenticated call to the service.
