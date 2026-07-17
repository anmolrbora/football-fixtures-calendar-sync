# football-fixtures-calendar-sync

Auto-updating calendar feeds of football fixtures, one `.ics` file per team,
built from ESPN's public schedule API. A GitHub Action regenerates the feeds
every 6 hours, so rescheduled kick-offs and newly drawn cup ties flow into
your calendar automatically.

Each event's UID is the stable ESPN match id, so a rescheduled fixture updates
the existing calendar entry in place — no duplicates.

Current feeds:

| Team | Feed |
|---|---|
| Liverpool FC | [`liverpool.ics`](liverpool.ics) |

## Subscribe (do this once)

The feed URL for a team is:

```
https://raw.githubusercontent.com/YOUR_GITHUB_USERNAME/football-fixtures-calendar-sync/main/<team>.ics
```

**iPhone / iPad:** Settings → Apps → Calendar → Calendar Accounts → Add Account →
Other → Add Subscribed Calendar → paste the URL.

**Mac:** Calendar → File → New Calendar Subscription → paste the URL →
set **Location: iCloud** (this makes it sync to all your devices and lets
Apple's servers refresh it even when your Mac is off) → set Auto-refresh
to "Every hour".

## How fixture changes are handled

- **Rescheduled kick-off** — same UID, new `DTSTART`; the event moves.
- **New cup ties** — every competition a team can play in is queried each
  run; fixtures appear as soon as draws are made.
- **TBC kick-off times** — flagged "(time TBC)" in the event title until
  the broadcast schedule confirms them.

## Adding a team

Find the team's ESPN id in the URL of its espn.com club page (e.g.
`espn.com/soccer/club/_/id/364/liverpool` → id `364`), then add an entry to
`TEAMS` in `generate_ics.py` with the competitions it can play in. The next
workflow run writes `<slug>.ics`.

## Run locally

```sh
python3 generate_ics.py   # writes one .ics per team (stdlib only, no deps)
```
