# Encode a month of hours

1. See what the month already holds: `billit time list --from <date> --to <date>`.
2. Find the project: `billit projects list`.
3. Add up each day from its segments, never from a total written beside them; tell the user about every day where the two disagree.
4. Add the days: `billit time add --project <id> <date>=<hours>…`. A blank day gets nothing; a day already holding hours on the project is left out and named to the user. A description only when the entity's Billit block `time_registration_descriptions` allows it.
5. Check: `billit time list --from <date> --to <date> --project <id>`. Done when the count and the hours match what was added.
