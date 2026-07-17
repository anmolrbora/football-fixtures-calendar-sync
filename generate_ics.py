#!/usr/bin/env python3
"""Generate liverpool.ics from ESPN's public schedule API.

Queries every competition Liverpool could play in; competitions whose
draws haven't happened yet simply return no events until they do.
Each event's UID is the stable ESPN match id, so when a fixture is
rescheduled the calendar entry updates in place instead of duplicating.

Output is deterministic (no run timestamps), so the file only changes
when the fixtures themselves change.
"""

import datetime
import json
import sys
import urllib.request
from urllib.error import URLError

TEAM_ID = "364"  # Liverpool
TEAM_NAME = "Liverpool"

LEAGUES = [
    ("eng.1", "Premier League"),
    ("uefa.champions", "Champions League"),
    ("uefa.europa", "Europa League"),
    ("uefa.europa.conf", "Conference League"),
    ("eng.fa", "FA Cup"),
    ("eng.league_cup", "Carabao Cup"),
    ("eng.charity", "Community Shield"),
    # ("club.friendly", "Friendly"),  # uncomment to include pre-season friendlies
]

API = (
    "https://site.api.espn.com/apis/site/v2/sports/soccer/"
    "{league}/teams/{team}/schedule?fixture=true"
)


def fetch_events(league_code):
    url = API.format(league=league_code, team=TEAM_ID)
    req = urllib.request.Request(url, headers={"User-Agent": "liverpool-fixtures-ics"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp).get("events", [])


def escape(text):
    """Escape text per RFC 5545."""
    return (
        text.replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\n", "\\n")
    )


def fold(line):
    """Fold lines longer than 75 octets per RFC 5545."""
    out = []
    while len(line.encode("utf-8")) > 75:
        # find a safe byte cut, backing off to a char boundary
        cut = 75
        while cut > 0:
            try:
                head = line.encode("utf-8")[:cut].decode("utf-8")
                break
            except UnicodeDecodeError:
                cut -= 1
        out.append(head)
        line = " " + line[len(head):]
    out.append(line)
    return "\r\n".join(out)


def to_utc_stamp(espn_date):
    # ESPN dates look like 2026-08-23T15:30Z (minutes precision, UTC)
    d = espn_date.rstrip("Z")
    date_part, time_part = d.split("T")
    hhmm = time_part.split(":")
    hh, mm = hhmm[0], hhmm[1] if len(hhmm) > 1 else "00"
    return date_part.replace("-", "") + "T" + hh + mm + "00Z"


def add_hours(stamp, hours):
    """Add hours to a UTC stamp like 20260823T153000Z (handles day rollover)."""
    dt = datetime.datetime.strptime(stamp, "%Y%m%dT%H%M%SZ")
    dt += datetime.timedelta(hours=hours)
    return dt.strftime("%Y%m%dT%H%M%SZ")


def build_event(event, competition_name):
    comp = event["competitions"][0]
    competitors = comp.get("competitors", [])
    home = next((c for c in competitors if c.get("homeAway") == "home"), None)
    away = next((c for c in competitors if c.get("homeAway") == "away"), None)
    if not home or not away:
        return None

    home_name = home["team"]["shortDisplayName"]
    away_name = away["team"]["shortDisplayName"]
    time_valid = event.get("timeValid", True)

    summary = f"⚽ {home_name} vs {away_name}"
    if not time_valid:
        summary += " (time TBC)"

    venue = comp.get("venue", {}).get("fullName", "")
    city = comp.get("venue", {}).get("address", {}).get("city", "")
    location = ", ".join(p for p in (venue, city) if p)

    start = to_utc_stamp(event["date"])
    end = add_hours(start, 2)

    description = competition_name
    if not time_valid:
        description += " — kickoff time not yet confirmed"

    lines = [
        "BEGIN:VEVENT",
        f"UID:espn-{event['id']}@liverpool-fixtures",
        f"DTSTAMP:{start}",
        f"DTSTART:{start}",
        f"DTEND:{end}",
        f"SUMMARY:{escape(summary)}",
        f"DESCRIPTION:{escape(description)}",
    ]
    if location:
        lines.append(f"LOCATION:{escape(location)}")
    lines.append("END:VEVENT")
    return start, lines


def main():
    all_events = {}
    failures = []
    for code, name in LEAGUES:
        try:
            for ev in fetch_events(code):
                all_events.setdefault(ev["id"], (ev, name))
        except (URLError, TimeoutError, json.JSONDecodeError, KeyError) as exc:
            failures.append((code, exc))
            print(f"warning: {code} failed: {exc}", file=sys.stderr)

    if failures and not all_events:
        print("error: every league query failed; keeping existing file", file=sys.stderr)
        sys.exit(1)

    built = []
    for ev, comp_name in all_events.values():
        result = build_event(ev, comp_name)
        if result:
            built.append(result)
    built.sort(key=lambda r: r[0])

    out = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//liverpool-fixtures//ESPN//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:Liverpool FC",
        "X-WR-CALDESC:Liverpool fixtures — auto-updated",
        "REFRESH-INTERVAL;VALUE=DURATION:PT6H",
        "X-PUBLISHED-TTL:PT6H",
    ]
    for _, lines in built:
        out.extend(lines)
    out.append("END:VCALENDAR")

    content = "\r\n".join(fold(line) for line in out) + "\r\n"
    with open("liverpool.ics", "w", encoding="utf-8", newline="") as f:
        f.write(content)
    print(f"wrote liverpool.ics with {len(built)} fixtures")


if __name__ == "__main__":
    main()
