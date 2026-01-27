# Fish Fry Data Schema

The fish fry data is sourced from Code for Pittsburgh's GeoJSON file.

## Venue Properties

| Field | Type | Description |
|-------|------|-------------|
| `venue_name` | string | Name of the venue |
| `venue_type` | string | Type: Church, Fire Department, VFW, Restaurant, etc. |
| `venue_address` | string | Full address |
| `venue_notes` | string | Additional venue-specific notes |
| `phone` | string | Contact phone number |
| `email` | string | Contact email |
| `website` | string | Website URL |
| `events` | array | List of event times (see below) |
| `menu.text` | string | Menu description |
| `menu.url` | string | Link to full menu |
| `homemade_pierogies` | boolean | Has homemade pierogies |
| `handicap` | boolean | Wheelchair accessible |
| `alcohol` | boolean | Serves alcohol |
| `take_out` | boolean | Offers takeout |
| `lunch` | boolean | Open for lunch |
| `etc` | string | Hours and additional info |
| `publish` | boolean | Whether venue should be shown |

## Event Object

Each venue may have multiple events:

```json
{
  "dt_start": "2024-02-16T16:00:00",
  "dt_end": "2024-02-16T19:00:00"
}
```

## Geometry

Each venue has GPS coordinates:

```json
{
  "type": "Point",
  "coordinates": [-79.9519, 40.4406]  // [longitude, latitude]
}
```

## Data Sources

- **Primary**: GitHub raw file (updated by maintainers)
  `https://raw.githubusercontent.com/CodeForPittsburgh/fishfrymap/master/data/fishfrymap.geojson`

- **WPRDC**: Western PA Regional Data Center
  `https://data.wprdc.org/dataset/pittsburgh-fish-fry-map`

## Venue Types

Common venue types in the dataset:
- Church
- Fire Department
- VFW
- American Legion
- Restaurant
- Community Organization
- Market
- School
