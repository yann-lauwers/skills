# Encode a month of hours

1. See what the month already holds: `billit time list --from <date> --to <date>`.
2. Find the project: `billit projects list`.
3. Add up each day from its segments, never from a total written beside them; a day where the two disagree → ask the user before adding it.
4. Add the days: `billit time add --project <id> <date>=<hours>…`. A blank day gets nothing; a day already holding hours on the project is left out and named to the user. A description only when the entity's choices allow one.
5. Check: `billit time list --from <date> --to <date> --project <id>`. Done when the count and the hours match what was added.
