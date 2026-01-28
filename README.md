# 🐟 Pittsburgh Fish Fry Finder

Find Lenten fish fries in the Pittsburgh area. Search by location, filter by features (homemade pierogies, wheelchair accessible, alcohol, takeout), check schedules, and get venue details.

An [Agent Skill](https://skills.sh) — works with Claude Code, Cursor, Windsurf, Cline, Goose, and any agent that supports the open skills format.

## Installation

```bash
npx skills add ianpcook/fishfry
```

## Features

- 🔍 **Search** by zip code, neighborhood, or address
- 🥟 **Filter** by pierogies, accessibility, alcohol, takeout
- 📅 **Schedule** check for specific dates
- 📍 **351 venues** across the Pittsburgh region

## Quick Examples

```bash
# Search near a location
fishfry.py search "15217"
fishfry.py search "Squirrel Hill"

# Filter by features
fishfry.py search "South Side" --pierogies --takeout

# List all fish fries
fishfry.py list --pierogies

# Get venue details
fishfry.py details "St. Alphonsus"

# Check what's open on a specific date
fishfry.py schedule friday
```

## Commands

| Command | Description |
|---------|-------------|
| `search <location>` | Find fish fries near a location |
| `list` | List all fish fries |
| `details <venue>` | Get details for a specific venue |
| `schedule <day/date>` | Check what's happening on a date |
| `update` | Refresh the local data cache |

## Filter Options

| Flag | Description |
|------|-------------|
| `--pierogies` | Homemade pierogies |
| `--accessible` | Wheelchair accessible |
| `--alcohol` | Serves alcohol |
| `--takeout` | Has takeout |

## Data Source

Data is maintained by volunteers at [Code for Pittsburgh](https://github.com/CodeForPittsburgh/fishfrymap) and published through the [Western PA Regional Data Center](https://data.wprdc.org/dataset/pittsburgh-fish-fry-map).

## Seasonal Note

Fish fries run during Lent (typically late February through mid-April). Outside of Lent season, data reflects the previous year's schedule.

## Links

- [Code for Pittsburgh Fish Fry Map](https://codeforpittsburgh.github.io/fishfrymap/)
- [WPRDC Dataset](https://data.wprdc.org/dataset/pittsburgh-fish-fry-map)
- [skills.sh](https://skills.sh) — The open agent skills ecosystem

---

*Made with ❤️ in Pittsburgh*
