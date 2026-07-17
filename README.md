# Liverpool FC fixtures → iCloud calendar

Auto-updating calendar feed of Liverpool fixtures across all competitions
(Premier League, Champions League, FA Cup, Carabao Cup, …). A GitHub Action
regenerates [`liverpool.ics`](liverpool.ics) every 6 hours from ESPN's public
schedule API, so rescheduled kick-offs and newly drawn cup ties flow into your
calendar automatically.

Each event's UID is the stable ESPN match id, so a rescheduled fixture updates
the existing calendar entry in place — no duplicates.

## Subscribe (do this once)

The feed URL is:

```
https://raw.githubusercontent.com/YOUR_GITHUB_USERNAME/liverpool-fixtures/main/liverpool.ics
```

**iPhone / iPad:** Settings → Apps → Calendar → Calendar Accounts → Add Account →
Other → Add Subscribed Calendar → paste the URL.

**Mac:** Calendar → File → New Calendar Subscription → paste the URL →
set **Location: iCloud** (this makes it sync to all your devices and lets
Apple's servers refresh it even when your Mac is off) → set Auto-refresh
to "Every hour".

## How fixture changes are handled

- **Rescheduled kick-off** — same UID, new `DTSTART`; the event moves.
- **New cup ties** — competitions are queried every run; fixtures appear as
  soon as draws are made.
- **TBC kick-off times** — flagged "(time TBC)" in the event title until
  the broadcast schedule confirms them.

## Run locally

```sh
python3 generate_ics.py   # writes liverpool.ics (stdlib only, no deps)
```

To include pre-season friendlies or change competitions, edit the `LEAGUES`
list at the top of `generate_ics.py`.
