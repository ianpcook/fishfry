#!/usr/bin/env python3
"""
Pittsburgh Fish Fry Finder

Find Lenten fish fries in the Pittsburgh area using data from Code for Pittsburgh.

Usage:
    fishfry.py search <location> [--pierogies] [--accessible] [--alcohol] [--takeout]
    fishfry.py list [--pierogies] [--accessible] [--alcohol] [--takeout]
    fishfry.py details <venue_name>
    fishfry.py schedule [<date>]
    fishfry.py update

Data source: https://codeforpittsburgh.github.io/fishfrymap/
"""

import argparse
import json
import math
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from urllib.parse import quote_plus

# Data source
GEOJSON_URL = "https://raw.githubusercontent.com/CodeForPittsburgh/fishfrymap/master/data/fishfrymap.geojson"

# Cache location
CACHE_DIR = Path(__file__).parent / ".cache"
CACHE_FILE = CACHE_DIR / "fishfry_data.json"
CACHE_MAX_AGE_DAYS = 7


def get_cache_path() -> Path:
    """Get the cache file path, creating directory if needed."""
    CACHE_DIR.mkdir(exist_ok=True)
    return CACHE_FILE


def load_data(force_update: bool = False) -> list[dict]:
    """Load fish fry data from cache or fetch fresh."""
    cache_path = get_cache_path()
    
    # Check if cache exists and is fresh
    if not force_update and cache_path.exists():
        cache_age = datetime.now().timestamp() - cache_path.stat().st_mtime
        if cache_age < CACHE_MAX_AGE_DAYS * 24 * 60 * 60:
            try:
                with open(cache_path) as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
    
    # Fetch fresh data
    print("Fetching fresh fish fry data...", file=sys.stderr)
    try:
        req = Request(GEOJSON_URL, headers={"User-Agent": "FishFry-Skill/1.0"})
        with urlopen(req, timeout=30) as response:
            geojson = json.loads(response.read().decode())
            
        # Extract and normalize features
        venues = []
        for feature in geojson.get("features", []):
            props = feature.get("properties", {})
            geom = feature.get("geometry", {})
            coords = geom.get("coordinates", [None, None])
            
            venue = {
                "id": feature.get("id"),
                "name": props.get("venue_name", "Unknown"),
                "type": props.get("venue_type", "Unknown"),
                "address": props.get("venue_address", ""),
                "phone": props.get("phone"),
                "email": props.get("email"),
                "website": props.get("website"),
                "notes": props.get("venue_notes"),
                "events": props.get("events", []),
                "menu_text": props.get("menu", {}).get("text") if props.get("menu") else None,
                "menu_url": props.get("menu", {}).get("url") if props.get("menu") else None,
                "homemade_pierogies": props.get("homemade_pierogies"),
                "handicap": props.get("handicap"),
                "alcohol": props.get("alcohol"),
                "take_out": props.get("take_out"),
                "lunch": props.get("lunch"),
                "etc": props.get("etc"),
                "lon": coords[0],
                "lat": coords[1],
                "publish": props.get("publish", True),
            }
            venues.append(venue)
        
        # Cache the data
        with open(cache_path, "w") as f:
            json.dump(venues, f)
        
        print(f"Loaded {len(venues)} fish fry venues.", file=sys.stderr)
        return venues
        
    except (HTTPError, URLError, json.JSONDecodeError) as e:
        print(f"Error fetching data: {e}", file=sys.stderr)
        # Try to use stale cache
        if cache_path.exists():
            print("Using cached data.", file=sys.stderr)
            with open(cache_path) as f:
                return json.load(f)
        return []


def geocode_location(location: str) -> tuple[float, float] | None:
    """
    Convert a location string to coordinates.
    Uses Nominatim (OpenStreetMap) for geocoding.
    """
    # Check if it looks like a zip code
    if re.match(r"^\d{5}$", location.strip()):
        location = f"{location}, PA"
    
    # Add Pittsburgh context if it looks like a neighborhood
    if not any(x in location.lower() for x in ["pa", "pennsylvania", "pittsburgh", ","]):
        location = f"{location}, Pittsburgh, PA"
    
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={quote_plus(location)}&format=json&limit=1"
        req = Request(url, headers={"User-Agent": "FishFry-Skill/1.0"})
        with urlopen(req, timeout=10) as response:
            results = json.loads(response.read().decode())
            if results:
                return float(results[0]["lat"]), float(results[0]["lon"])
    except Exception as e:
        print(f"Geocoding failed: {e}", file=sys.stderr)
    
    return None


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points in miles."""
    R = 3959  # Earth's radius in miles
    
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c


def filter_venues(venues: list[dict], 
                  pierogies: bool = False,
                  accessible: bool = False,
                  alcohol: bool = False,
                  takeout: bool = False) -> list[dict]:
    """Filter venues by features."""
    filtered = venues
    
    if pierogies:
        filtered = [v for v in filtered if v.get("homemade_pierogies") == True]
    if accessible:
        filtered = [v for v in filtered if v.get("handicap") == True]
    if alcohol:
        filtered = [v for v in filtered if v.get("alcohol") == True]
    if takeout:
        filtered = [v for v in filtered if v.get("take_out") == True]
    
    return filtered


def format_venue(venue: dict, distance: float | None = None) -> str:
    """Format a venue for display."""
    lines = []
    
    # Header
    name = venue["name"]
    vtype = venue["type"]
    lines.append(f"🐟 {name}")
    lines.append(f"   Type: {vtype}")
    
    # Distance
    if distance is not None:
        lines.append(f"   Distance: {distance:.1f} miles")
    
    # Address
    if venue["address"]:
        lines.append(f"   Address: {venue['address']}")
    
    # Features
    features = []
    if venue.get("homemade_pierogies"):
        features.append("🥟 Homemade Pierogies")
    if venue.get("handicap"):
        features.append("♿ Wheelchair Accessible")
    if venue.get("alcohol"):
        features.append("🍺 Alcohol")
    if venue.get("take_out"):
        features.append("📦 Takeout")
    if venue.get("lunch"):
        features.append("☀️ Lunch")
    
    if features:
        lines.append(f"   Features: {', '.join(features)}")
    
    # Hours/Events
    if venue.get("etc"):
        lines.append(f"   Hours: {venue['etc']}")
    
    # Contact
    if venue.get("phone"):
        lines.append(f"   Phone: {venue['phone']}")
    if venue.get("website"):
        lines.append(f"   Web: {venue['website']}")
    
    return "\n".join(lines)


def format_venue_details(venue: dict) -> str:
    """Format detailed venue information."""
    lines = [format_venue(venue)]
    
    # Menu
    if venue.get("menu_text"):
        lines.append(f"\n   📋 Menu: {venue['menu_text']}")
    if venue.get("menu_url"):
        lines.append(f"   Menu URL: {venue['menu_url']}")
    
    # Notes
    if venue.get("notes"):
        lines.append(f"\n   📝 Notes: {venue['notes']}")
    
    # Events/Schedule
    events = venue.get("events", [])
    if events:
        lines.append("\n   📅 Schedule:")
        for event in events[:10]:  # Limit to 10
            start = event.get("dt_start", "")
            end = event.get("dt_end", "")
            if start:
                try:
                    dt_start = datetime.fromisoformat(start.replace("Z", "+00:00"))
                    dt_end = datetime.fromisoformat(end.replace("Z", "+00:00")) if end else None
                    date_str = dt_start.strftime("%a %b %d")
                    time_str = dt_start.strftime("%I:%M %p").lstrip("0")
                    if dt_end:
                        time_str += f" - {dt_end.strftime('%I:%M %p').lstrip('0')}"
                    lines.append(f"      {date_str}: {time_str}")
                except ValueError:
                    lines.append(f"      {start}")
    
    return "\n".join(lines)


def cmd_search(args):
    """Search for fish fries near a location."""
    venues = load_data()
    if not venues:
        print("No fish fry data available.")
        return 1
    
    # Geocode the location
    coords = geocode_location(args.location)
    if not coords:
        print(f"Could not find location: {args.location}")
        return 1
    
    lat, lon = coords
    print(f"Searching near: {args.location} ({lat:.4f}, {lon:.4f})\n", file=sys.stderr)
    
    # Filter by features
    filtered = filter_venues(
        venues,
        pierogies=args.pierogies,
        accessible=args.accessible,
        alcohol=args.alcohol,
        takeout=args.takeout
    )
    
    # Calculate distances and sort
    results = []
    for venue in filtered:
        if venue.get("lat") and venue.get("lon"):
            dist = haversine_distance(lat, lon, venue["lat"], venue["lon"])
            results.append((venue, dist))
    
    results.sort(key=lambda x: x[1])
    
    # Show results (limit to 15)
    limit = args.limit or 15
    if not results:
        print("No fish fries found matching your criteria.")
        return 0
    
    print(f"Found {len(results)} fish fries. Showing nearest {min(limit, len(results))}:\n")
    
    for venue, dist in results[:limit]:
        print(format_venue(venue, dist))
        print()
    
    return 0


def cmd_list(args):
    """List all fish fries."""
    venues = load_data()
    if not venues:
        print("No fish fry data available.")
        return 1
    
    # Filter by features
    filtered = filter_venues(
        venues,
        pierogies=args.pierogies,
        accessible=args.accessible,
        alcohol=args.alcohol,
        takeout=args.takeout
    )
    
    # Sort by name
    filtered.sort(key=lambda v: v["name"])
    
    if not filtered:
        print("No fish fries found matching your criteria.")
        return 0
    
    print(f"Found {len(filtered)} fish fries:\n")
    
    for venue in filtered:
        print(format_venue(venue))
        print()
    
    return 0


def cmd_details(args):
    """Get details for a specific venue."""
    venues = load_data()
    if not venues:
        print("No fish fry data available.")
        return 1
    
    # Search by name (fuzzy)
    query = args.venue_name.lower()
    matches = [v for v in venues if query in v["name"].lower()]
    
    if not matches:
        print(f"No venue found matching: {args.venue_name}")
        # Suggest similar
        suggestions = [v["name"] for v in venues if any(word in v["name"].lower() for word in query.split())][:5]
        if suggestions:
            print("\nDid you mean:")
            for s in suggestions:
                print(f"  - {s}")
        return 1
    
    if len(matches) > 1:
        print(f"Multiple venues match '{args.venue_name}':\n")
    
    for venue in matches[:5]:
        print(format_venue_details(venue))
        print()
    
    return 0


def cmd_schedule(args):
    """Show fish fries happening on a specific date."""
    venues = load_data()
    if not venues:
        print("No fish fry data available.")
        return 1
    
    # Parse date
    if args.date:
        date_str = args.date.lower()
        if date_str in ("today", "now"):
            target_date = datetime.now().date()
        elif date_str in ("tomorrow",):
            target_date = (datetime.now() + timedelta(days=1)).date()
        elif date_str in ("friday", "fri"):
            today = datetime.now()
            days_until_friday = (4 - today.weekday()) % 7
            if days_until_friday == 0:
                days_until_friday = 7  # Next Friday if today is Friday
            target_date = (today + timedelta(days=days_until_friday)).date()
        else:
            try:
                target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                print(f"Could not parse date: {args.date}")
                print("Use: today, tomorrow, friday, or YYYY-MM-DD")
                return 1
    else:
        # Default to next Friday
        today = datetime.now()
        days_until_friday = (4 - today.weekday()) % 7
        if days_until_friday == 0 and today.hour >= 20:
            days_until_friday = 7
        target_date = (today + timedelta(days=days_until_friday)).date()
    
    print(f"Fish fries on {target_date.strftime('%A, %B %d, %Y')}:\n")
    
    # Find venues with events on that date
    happening = []
    for venue in venues:
        for event in venue.get("events", []):
            try:
                start = datetime.fromisoformat(event["dt_start"].replace("Z", "+00:00"))
                if start.date() == target_date:
                    happening.append((venue, event))
                    break
            except (ValueError, KeyError):
                pass
    
    if not happening:
        print("No fish fries scheduled for this date in our data.")
        print("Note: Event data may be from a previous year. Check venue websites for current schedules.")
        return 0
    
    print(f"Found {len(happening)} fish fries:\n")
    
    for venue, event in happening:
        try:
            start = datetime.fromisoformat(event["dt_start"].replace("Z", "+00:00"))
            end = datetime.fromisoformat(event["dt_end"].replace("Z", "+00:00"))
            time_str = f"{start.strftime('%I:%M %p').lstrip('0')} - {end.strftime('%I:%M %p').lstrip('0')}"
        except:
            time_str = "Check venue"
        
        print(f"🐟 {venue['name']} ({venue['type']})")
        print(f"   Time: {time_str}")
        print(f"   Address: {venue['address']}")
        if venue.get("phone"):
            print(f"   Phone: {venue['phone']}")
        print()
    
    return 0


def cmd_update(args):
    """Update the local data cache."""
    venues = load_data(force_update=True)
    print(f"Updated cache with {len(venues)} venues.")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Pittsburgh Fish Fry Finder",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search near a location")
    search_parser.add_argument("location", help="Location (zip, neighborhood, or address)")
    search_parser.add_argument("--pierogies", action="store_true", help="Has homemade pierogies")
    search_parser.add_argument("--accessible", action="store_true", help="Wheelchair accessible")
    search_parser.add_argument("--alcohol", action="store_true", help="Serves alcohol")
    search_parser.add_argument("--takeout", action="store_true", help="Has takeout")
    search_parser.add_argument("--limit", "-n", type=int, default=15, help="Max results")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all fish fries")
    list_parser.add_argument("--pierogies", action="store_true", help="Has homemade pierogies")
    list_parser.add_argument("--accessible", action="store_true", help="Wheelchair accessible")
    list_parser.add_argument("--alcohol", action="store_true", help="Serves alcohol")
    list_parser.add_argument("--takeout", action="store_true", help="Has takeout")
    
    # Details command
    details_parser = subparsers.add_parser("details", help="Get venue details")
    details_parser.add_argument("venue_name", help="Venue name (partial match)")
    
    # Schedule command
    schedule_parser = subparsers.add_parser("schedule", help="Show schedule for a date")
    schedule_parser.add_argument("date", nargs="?", help="Date (today, tomorrow, friday, or YYYY-MM-DD)")
    
    # Update command
    subparsers.add_parser("update", help="Update local data cache")
    
    args = parser.parse_args()
    
    if args.command == "search":
        return cmd_search(args)
    elif args.command == "list":
        return cmd_list(args)
    elif args.command == "details":
        return cmd_details(args)
    elif args.command == "schedule":
        return cmd_schedule(args)
    elif args.command == "update":
        return cmd_update(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
