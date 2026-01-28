---
name: fishfry
description: Find Pittsburgh-area Lenten fish fries. Search by location, filter by features (homemade pierogies, wheelchair accessible, alcohol, takeout), check schedules, and get venue details. Uses data from Code for Pittsburgh's Fish Fry Map.
version: 1.0.0
homepage: https://codeforpittsburgh.github.io/fishfrymap/
metadata:
  emoji: 🐟
  tags:
    - pittsburgh
    - local
    - food
    - lent
    - civic-data
---

# Pittsburgh Fish Fry Finder

Find Lenten fish fries in the Pittsburgh area. Data sourced from [Code for Pittsburgh's Fish Fry Map](https://codeforpittsburgh.github.io/fishfrymap/).

## Usage

```bash
# Search near a location (zip code, neighborhood, or address)
<skill>/fishfry.py search "15213"
<skill>/fishfry.py search "Squirrel Hill"
<skill>/fishfry.py search "4400 Forbes Ave, Pittsburgh"

# Filter by features
<skill>/fishfry.py search "15217" --pierogies        # Homemade pierogies
<skill>/fishfry.py search "15217" --accessible       # Wheelchair accessible
<skill>/fishfry.py search "15217" --alcohol          # Serves alcohol
<skill>/fishfry.py search "15217" --takeout          # Has takeout

# Combine filters
<skill>/fishfry.py search "South Side" --pierogies --takeout

# List all fish fries
<skill>/fishfry.py list
<skill>/fishfry.py list --pierogies

# Get details for a specific venue
<skill>/fishfry.py details "St. Alphonsus"
<skill>/fishfry.py details "Our Lady of Joy"

# Check what's happening on a specific date
<skill>/fishfry.py schedule friday
<skill>/fishfry.py schedule 2026-03-06

# Update the local data cache
<skill>/fishfry.py update
```

## Output

Results include:
- Venue name and type (Church, Fire Hall, VFW, etc.)
- Address and distance from search location
- Hours of operation
- Menu highlights
- Features (pierogies, accessible, alcohol, takeout)
- Contact info (phone, website)

## Data Source

Data is maintained by volunteers at [Code for Pittsburgh](https://github.com/CodeForPittsburgh/fishfrymap) and published through the [Western PA Regional Data Center](https://data.wprdc.org/dataset/pittsburgh-fish-fry-map).

The skill caches data locally and can be updated with `fishfry.py update`.

## Seasonal Note

Fish fries run during Lent (typically late February through mid-April). Outside of Lent season, the data reflects the previous year's schedule. Check venue websites for current year confirmation.

## Example Queries

**"Find fish fries near me with homemade pierogies"**
```bash
fishfry.py search "15232" --pierogies
```

**"What fish fries are in the South Hills?"**
```bash
fishfry.py search "South Hills"
```

**"Tell me about the fish fry at St. Basil's"**
```bash
fishfry.py details "St. Basil"
```

**"Which places have takeout and are wheelchair accessible?"**
```bash
fishfry.py list --takeout --accessible
```
