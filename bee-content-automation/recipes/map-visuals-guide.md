# Map Visuals for True Crime YouTube Videos — Programmatic Guide

> Practical, CLI/API-only methods for generating map imagery.
> No GUI tools required. Case study: Alex Murdaugh / Lowcountry SC.

---

## Table of Contents

1. [Key Locations — Murdaugh Case](#1-key-locations--murdaugh-case)
2. [Mapbox Static Images API](#2-mapbox-static-images-api)
3. [Google Maps Static API](#3-google-maps-static-api)
4. [Google Earth Studio](#4-google-earth-studio)
5. [Open-Source Alternatives](#5-open-source-alternatives)
6. [Free Tile Sources (No API Key)](#6-free-tile-sources-no-api-key)
7. [Practical Recipe: Zoom-Into-Location Animation](#7-practical-recipe-zoom-into-location-animation)
8. [py-staticmaps — Full Python Recipe](#8-py-staticmaps--full-python-recipe)
9. [Quick Reference: Tile Coordinate Calculator](#9-quick-reference-tile-coordinate-calculator)

---

## 1. Key Locations — Murdaugh Case

| # | Location | Lat, Lon | Notes |
|---|----------|----------|-------|
| 1 | Moselle Hunting Estate, Islandton, SC | 32.836, -80.846 | 1,772-acre property; double murder scene |
| 2 | Colleton County Courthouse, Walterboro, SC | 32.9052, -80.6668 | Trial venue |
| 3 | Archers Creek Bridge, Beaufort County, SC | 32.3917, -80.6750 | Mallory Beach boat crash (Feb 2019) |
| 4 | Almeda, SC (Alex's mother's house area) | 32.6250, -81.1000 | Near Hampton; roadside shooting incident |
| 5 | Lowcountry region (5-county overview) | 32.65, -80.85 | Hampton, Colleton, Beaufort, Jasper, Allendale |

---

## 2. Mapbox Static Images API

### Getting a Free API Key

1. Go to https://account.mapbox.com/auth/signup/
2. Sign up with email (no credit card required for free tier)
3. Your default public token is on the account dashboard
4. Free tier: **100,000 Static Images API requests/month** (as of 2025)
5. Beyond free tier: ~$0.50 per 1,000 requests (varies by volume)

### URL Format

```
https://api.mapbox.com/styles/v1/{username}/{style_id}/static/{overlay}/{lon},{lat},{zoom},{bearing},{pitch}/{width}x{height}{@2x}?access_token={TOKEN}
```

### Available Styles

| Style | ID | Use Case |
|-------|----|----------|
| Satellite | `mapbox/satellite-v9` | Aerial views of properties/estates |
| Satellite + Streets | `mapbox/satellite-streets-v12` | Satellite with road labels |
| Dark | `mapbox/dark-v11` | Moody true-crime aesthetic |
| Streets | `mapbox/streets-v12` | Standard road map |
| Light | `mapbox/light-v11` | Clean, minimal |
| Outdoors | `mapbox/outdoors-v12` | Terrain for rural areas |

### Marker Overlay Syntax

```
pin-l-{label}+{hex_color}({lon},{lat})
```

- `pin-s` = small pin, `pin-l` = large pin
- Label: single letter/number (e.g., `1`, `a`, `+`)
- Color: 6-digit hex without `#` (e.g., `ff0000` for red)
- Multiple markers: separate with commas

### Example URLs for Murdaugh Locations

Replace `YOUR_TOKEN` with your Mapbox access token.

**1. Moselle Estate — Satellite, zoom 14 (property level)**
```
https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/pin-l-1+ff0000(-80.846,32.836)/-80.846,32.836,14,0/1280x720@2x?access_token=YOUR_TOKEN
```

**2. Moselle Estate — Dark style, zoom 12 (area context)**
```
https://api.mapbox.com/styles/v1/mapbox/dark-v11/static/pin-l-1+ff0000(-80.846,32.836)/-80.846,32.836,12,0/1280x720@2x?access_token=YOUR_TOKEN
```

**3. Colleton County Courthouse — Satellite Streets**
```
https://api.mapbox.com/styles/v1/mapbox/satellite-streets-v12/static/pin-l-2+ff4444(-80.6668,32.9052)/-80.6668,32.9052,16,0/1280x720@2x?access_token=YOUR_TOKEN
```

**4. Archers Creek Bridge — Satellite**
```
https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/pin-l-3+ffaa00(-80.675,32.3917)/-80.675,32.3917,15,0/1280x720@2x?access_token=YOUR_TOKEN
```

**5. Almeda / Mother's House Area — Dark**
```
https://api.mapbox.com/styles/v1/mapbox/dark-v11/static/pin-l-4+ff0000(-81.1,32.625)/-81.1,32.625,13,0/1280x720@2x?access_token=YOUR_TOKEN
```

**6. Lowcountry 5-County Overview — All markers**
```
https://api.mapbox.com/styles/v1/mapbox/dark-v11/static/pin-l-1+ff0000(-80.846,32.836),pin-l-2+ff4444(-80.6668,32.9052),pin-l-3+ffaa00(-80.675,32.3917),pin-l-4+ff0000(-81.1,32.625)/-80.85,32.65,9,0/1280x720@2x?access_token=YOUR_TOKEN
```

### Downloading via CLI

```bash
# Single image
curl -o moselle_satellite.png \
  "https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/pin-l-1+ff0000(-80.846,32.836)/-80.846,32.836,14,0/1280x720@2x?access_token=YOUR_TOKEN"

# Batch download at multiple zoom levels (for zoom animation)
for z in 6 8 10 12 14 16; do
  curl -o "moselle_z${z}.png" \
    "https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/-80.846,32.836,${z},0/1280x720@2x?access_token=YOUR_TOKEN"
done
```

### Constraints

- Max image size: 1280x1280 pixels (2560x2560 with @2x retina)
- Max URL length: 8,192 characters
- Rate limit: 1,250 requests/minute
- Overlay markers: up to ~100 before URL length becomes an issue

---

## 3. Google Maps Static API

### Setup & Pricing

1. Go to https://console.cloud.google.com/
2. Create a project, enable "Maps Static API"
3. Generate an API key under Credentials
4. Pricing: **$2.00 per 1,000 requests** (after $200/month free credit)
5. $200 free credit = **100,000 free static map requests/month**
6. Max image: 640x640 (or 1280x1280 with `scale=2`)

### URL Format

```
https://maps.googleapis.com/maps/api/staticmap?center={lat},{lon}&zoom={z}&size={w}x{h}&maptype={type}&markers={markers}&key={KEY}
```

### Map Types

| Type | Description |
|------|-------------|
| `roadmap` | Standard road map |
| `satellite` | Satellite imagery |
| `terrain` | Terrain with natural features |
| `hybrid` | Satellite + road/label overlay |

### Marker Syntax

```
markers=color:{color}|label:{letter}|{lat},{lon}
```

- Colors: `red`, `blue`, `green`, `purple`, `yellow`, `orange`, or `0xRRGGBB`
- Labels: single uppercase letter or digit (A-Z, 0-9)
- Size: `tiny`, `small`, `mid` (prepend `size:mid|` to marker def)

### Styling (Dark Theme)

Append style parameters for a dark map:
```
&style=element:geometry|color:0x212121
&style=element:labels.text.fill|color:0x757575
&style=element:labels.text.stroke|color:0x212121
&style=feature:road|element:geometry|color:0x383838
&style=feature:water|element:geometry|color:0x1a1a2e
```

Or use a Cloud-based Map ID for JSON-styled maps.

### Example URLs for Murdaugh Locations

**1. Moselle Estate — Satellite**
```
https://maps.googleapis.com/maps/api/staticmap?center=32.836,-80.846&zoom=14&size=640x360&scale=2&maptype=satellite&markers=color:red|label:M|32.836,-80.846&key=YOUR_KEY
```

**2. Courthouse — Hybrid**
```
https://maps.googleapis.com/maps/api/staticmap?center=32.9052,-80.6668&zoom=16&size=640x360&scale=2&maptype=hybrid&markers=color:red|label:C|32.9052,-80.6668&key=YOUR_KEY
```

**3. Archers Creek Bridge — Satellite**
```
https://maps.googleapis.com/maps/api/staticmap?center=32.3917,-80.675&zoom=15&size=640x360&scale=2&maptype=satellite&markers=color:orange|label:B|32.3917,-80.675&key=YOUR_KEY
```

**4. Lowcountry Overview — All markers on hybrid**
```
https://maps.googleapis.com/maps/api/staticmap?size=640x360&scale=2&maptype=hybrid&markers=color:red|label:1|32.836,-80.846&markers=color:red|label:2|32.9052,-80.6668&markers=color:orange|label:3|32.3917,-80.675&markers=color:red|label:4|32.625,-81.1&key=YOUR_KEY
```
(Omitting `center` and `zoom` auto-fits all markers.)

### Batch Download

```bash
for z in 6 8 10 12 14 16; do
  curl -o "google_moselle_z${z}.png" \
    "https://maps.googleapis.com/maps/api/staticmap?center=32.836,-80.846&zoom=${z}&size=640x360&scale=2&maptype=satellite&key=YOUR_KEY"
done
```

---

## 4. Google Earth Studio

### Can It Be Scripted/Automated?

**No.** Google Earth Studio is a browser-only tool (https://earth.google.com/studio/) with no API, no CLI, and no scripting interface. It requires a Google account and manual interaction through the Chrome browser.

### Manual Workflow (for reference)

1. Visit https://earth.google.com/studio/ and sign in
2. Create a new project → choose "Quick Start" → "Zoom To Point"
3. Enter coordinates (e.g., 32.836, -80.846 for Moselle)
4. Adjust start altitude (e.g., 50km), end altitude (e.g., 500m), duration
5. Preview the animation
6. Export → choose JPEG sequence or MP4
7. Render frames (can take minutes depending on quality)
8. Download the rendered frames

### Programmatic Alternatives to Earth Studio

Since Earth Studio cannot be automated, the best alternatives are:

1. **Mapbox Static Images at multiple zooms + FFmpeg** (see Section 7)
2. **py-staticmaps at multiple zooms + FFmpeg** (see Section 8)
3. **CesiumJS** (open-source 3D globe, can be automated with Puppeteer for screenshots)
4. **deck.gl** + headless Chrome for animated globe-to-ground flyovers

---

## 5. Open-Source Alternatives

### 5a. MapLibre GL JS

**What it is:** Open-source fork of Mapbox GL JS for rendering vector maps in the browser.

**Headless rendering:** MapLibre GL JS itself is browser-only. However:
- **mbgl-renderer** (https://github.com/consbio/mbgl-renderer) wraps MapLibre GL Native for Node.js server-side rendering
- Requires `xvfb` on headless Linux servers (virtual framebuffer)
- Can render styled maps to PNG from command line

**mbgl-renderer CLI usage:**
```bash
npm install -g mbgl-renderer

# Render a map image
mbgl-render style.json output.png 1280 720 \
  --center -80.846,32.836 \
  --zoom 14
```

**mbgl-renderer HTTP server:**
```bash
mbgl-static-server -p 8080

# Then request images via HTTP:
curl "http://localhost:8080/render?width=1280&height=720&zoom=14&center=-80.846,32.836" -o map.png
```

**Verdict:** Good for batch generation if you need custom vector styles. Heavier setup than static tile APIs.

### 5b. py-staticmaps (Python)

**Best option for free, no-API-key map generation.** See full recipe in Section 8.

- Pure Python library
- Uses free tile providers (OSM, ArcGIS satellite, Carto Dark) — no API key needed
- Generates PNG, SVG output
- Supports markers, lines, polygons, circles
- Auto-calculates optimal zoom/center

**Install:**
```bash
pip install py-staticmaps           # Basic (PIL rendering)
pip install "py-staticmaps[cairo]"  # Anti-aliased rendering (recommended)
```

### 5c. Mapnik

**What it is:** C++ map rendering toolkit (powers OpenStreetMap's tile server).

**Best for:** Rendering custom-styled tiles from raw OSM data in PostGIS.

**Python usage:**
```python
import mapnik

m = mapnik.Map(1280, 720)
mapnik.load_map(m, 'style.xml')
m.zoom_to_box(mapnik.Box2d(-81.5, 32.0, -80.0, 33.2))
mapnik.render_to_file(m, 'lowcountry.png', 'png')
```

**Verdict:** Extremely powerful but heavyweight. Requires importing OSM data into PostGIS and writing XML stylesheets. Overkill for generating a few map visuals — use py-staticmaps or Mapbox instead.

### 5d. Comparison Table

| Tool | Free? | API Key? | Satellite? | Dark Theme? | Headless? | Effort |
|------|-------|----------|------------|-------------|-----------|--------|
| Mapbox Static | 100K/mo free | Yes | Yes | Yes | curl | Low |
| Google Static | $200 credit/mo | Yes | Yes | Via styling | curl | Low |
| py-staticmaps | Unlimited | No* | Yes (ArcGIS) | Yes (Carto) | Python | Low |
| mbgl-renderer | Unlimited | Depends on tiles | Depends | Yes | Node.js | Medium |
| Mapnik | Unlimited | No | No (needs data) | Yes | Python/C++ | High |
| Google Earth Studio | Free | N/A | Yes | No | **No (GUI only)** | Manual |

*py-staticmaps uses free tile servers; no personal API key needed for OSM/ArcGIS/Carto.

---

## 6. Free Tile Sources (No API Key)

These tile URLs can be fetched directly with `curl` — no signup required.

### OpenStreetMap Standard
```
https://tile.openstreetmap.org/{z}/{x}/{y}.png
```
- Free, donation-funded
- Max zoom: 19
- Attribution required: "© OpenStreetMap contributors"
- Usage policy: https://operations.osmfoundation.org/policies/tiles/
- Rate limit: ~2 requests/second recommended for bulk

### ArcGIS World Imagery (Satellite)
```
https://server.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}
```
- Free to use (no API key)
- Max zoom: 23
- 256x256 pixel tiles
- Attribution: "Source: Esri, Earthstar Geographics, GIS User Community"
- **Best free satellite option for true crime visuals**

### Carto Dark (Dark Theme — No Labels)
```
https://{a|b|c|d}.basemaps.cartocdn.com/rastertiles/dark_nolabels/{z}/{x}/{y}.png
```
- Free tier available
- Max zoom: 20
- Moody, dark aesthetic perfect for true crime

### Carto Dark (With Labels)
```
https://{a|b|c|d}.basemaps.cartocdn.com/rastertiles/dark_all/{z}/{x}/{y}.png
```

### Stadia Alidade Smooth Dark
```
https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}.png
```
- Free for local/non-commercial development (no key needed locally)
- Commercial use requires API key

### Direct Tile Download Example

```bash
# Download a satellite tile of the Moselle Estate area (zoom 14)
# Tile coords for 32.836N, -80.846W at z=14: x=4474, y=6562
curl -o moselle_sat_z14.jpg \
  "https://server.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer/tile/14/6562/4474"

# Download the same area from Carto Dark (zoom 14)
curl -o moselle_dark_z14.png \
  "https://a.basemaps.cartocdn.com/rastertiles/dark_nolabels/14/4474/6562.png"
```

---

## 7. Practical Recipe: Zoom-Into-Location Animation

This creates a smooth "Google Earth-style" zoom from continent level down to property level using static images stitched with FFmpeg.

### Method A: Using Mapbox (Best Quality)

**Step 1: Download images at increasing zoom levels**

```bash
TOKEN="YOUR_MAPBOX_TOKEN"
LON="-80.846"
LAT="32.836"

for z in 4 6 8 10 12 14 16; do
  curl -o "frame_z${z}.png" \
    "https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/${LON},${LAT},${z},0/1280x720@2x?access_token=${TOKEN}"
  sleep 0.5  # Be polite to the API
done
```

This gives you 7 images from continental view (z4) to street level (z16).

**Step 2: Create smooth zoom animation with FFmpeg**

```bash
# Create a file list for FFmpeg
cat > filelist.txt << 'EOF'
file 'frame_z4.png'
duration 0.8
file 'frame_z6.png'
duration 0.8
file 'frame_z8.png'
duration 0.8
file 'frame_z10.png'
duration 0.8
file 'frame_z12.png'
duration 0.8
file 'frame_z14.png'
duration 0.8
file 'frame_z16.png'
duration 2.0
EOF

# Stitch into video with crossfade transitions
ffmpeg -f concat -safe 0 -i filelist.txt \
  -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,fps=30" \
  -c:v libx264 -pix_fmt yuv420p -crf 18 \
  zoom_moselle.mp4
```

**Step 3: Add zoompan effect for smooth Ken Burns zoom between levels**

```bash
# Apply zoompan to each frame for a smoother zoom-in feel
# This slowly zooms into the center of each image over 30 frames (1 second at 30fps)

for f in frame_z*.png; do
  base=$(basename "$f" .png)
  ffmpeg -loop 1 -i "$f" \
    -vf "zoompan=z='min(zoom+0.015,1.5)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=30:s=1920x1080:fps=30" \
    -t 1 -c:v libx264 -pix_fmt yuv420p \
    "${base}_zoomed.mp4"
done

# Concatenate all zoomed clips
cat > concat_list.txt << 'EOF'
file 'frame_z4_zoomed.mp4'
file 'frame_z6_zoomed.mp4'
file 'frame_z8_zoomed.mp4'
file 'frame_z10_zoomed.mp4'
file 'frame_z12_zoomed.mp4'
file 'frame_z14_zoomed.mp4'
file 'frame_z16_zoomed.mp4'
EOF

ffmpeg -f concat -safe 0 -i concat_list.txt \
  -c copy zoom_animation_smooth.mp4
```

### Method B: Using Free Tiles (No API Key)

**Step 1: Python script to download and stitch tiles into full images**

```python
#!/usr/bin/env python3
"""Download map tiles at multiple zoom levels and stitch into full images."""

import math
import urllib.request
import os

def deg2tile(lat_deg, lon_deg, zoom):
    """Convert lat/lon to tile x,y at given zoom."""
    lat_rad = math.radians(lat_deg)
    n = 1 << zoom
    x = int((lon_deg + 180.0) / 360.0 * n)
    y = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return x, y

def download_tile(z, x, y, provider="arcgis", outdir="tiles"):
    """Download a single tile."""
    os.makedirs(outdir, exist_ok=True)

    if provider == "arcgis":
        # Note: ArcGIS uses tile/{z}/{y}/{x} (y before x)
        url = f"https://server.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
        ext = "jpg"
    elif provider == "osm":
        url = f"https://tile.openstreetmap.org/{z}/{x}/{y}.png"
        ext = "png"
    elif provider == "carto-dark":
        shard = ["a", "b", "c", "d"][x % 4]
        url = f"https://{shard}.basemaps.cartocdn.com/rastertiles/dark_nolabels/{z}/{x}/{y}.png"
        ext = "png"
    else:
        raise ValueError(f"Unknown provider: {provider}")

    outpath = f"{outdir}/{provider}_z{z}_{x}_{y}.{ext}"
    if not os.path.exists(outpath):
        req = urllib.request.Request(url, headers={"User-Agent": "TrueCrimeMapGen/1.0"})
        with urllib.request.urlopen(req) as resp:
            with open(outpath, "wb") as f:
                f.write(resp.read())
    return outpath

def download_grid(lat, lon, zoom, provider="arcgis", grid=3, outdir="tiles"):
    """Download a grid of tiles centered on lat/lon.

    grid=3 means 3x3 = 9 tiles, producing a 768x768 image (256px tiles).
    grid=5 means 5x5 = 25 tiles, producing a 1280x1280 image.
    """
    cx, cy = deg2tile(lat, lon, zoom)
    half = grid // 2
    paths = []
    for dy in range(-half, half + 1):
        row = []
        for dx in range(-half, half + 1):
            path = download_tile(zoom, cx + dx, cy + dy, provider, outdir)
            row.append(path)
        paths.append(row)
    return paths


# === Murdaugh Case: Moselle Estate ===
LAT, LON = 32.836, -80.846

for z in [4, 6, 8, 10, 12, 14, 16]:
    print(f"\nZoom {z}:")
    cx, cy = deg2tile(LAT, LON, z)
    print(f"  Center tile: x={cx}, y={cy}")
    grid_size = 5 if z <= 10 else 3
    paths = download_grid(LAT, LON, z, provider="arcgis", grid=grid_size)
    print(f"  Downloaded {len(paths)}x{len(paths[0])} grid")
```

**Step 2: Stitch tiles into full images using PIL**

```python
from PIL import Image

def stitch_tiles(tile_paths, output_path, tile_size=256):
    """Stitch a grid of tile images into one image."""
    rows = len(tile_paths)
    cols = len(tile_paths[0])
    result = Image.new("RGB", (cols * tile_size, rows * tile_size))

    for r, row in enumerate(tile_paths):
        for c, path in enumerate(row):
            tile = Image.open(path)
            result.paste(tile, (c * tile_size, r * tile_size))

    result.save(output_path)
    print(f"Saved: {output_path} ({result.size[0]}x{result.size[1]})")
    return output_path
```

**Step 3: Apply FFmpeg zoom animation (same as Method A, Step 2-3)**

### Method C: FFmpeg Zoompan on a Single High-Res Image

If you have one very high-resolution satellite image (e.g., 4000x4000):

```bash
# Slow zoom into center over 5 seconds at 30fps
ffmpeg -loop 1 -i highres_moselle.png \
  -vf "zoompan=z='if(lte(zoom,1.0),1.5,max(1.001,zoom-0.0033))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=150:s=1920x1080:fps=30" \
  -t 5 -c:v libx264 -pix_fmt yuv420p -crf 18 \
  moselle_zoomin.mp4
```

**Zoompan parameter reference:**
| Parameter | Description | Example |
|-----------|-------------|---------|
| `z` (zoom) | Zoom factor expression (1.0 = no zoom) | `'min(zoom+0.01,2.0)'` |
| `x` | X position of zoom center | `'iw/2-(iw/zoom/2)'` (center) |
| `y` | Y position of zoom center | `'ih/2-(ih/zoom/2)'` (center) |
| `d` | Duration in frames per input frame | `150` (5s at 30fps) |
| `s` | Output size | `1920x1080` |
| `fps` | Output frame rate | `30` |

**Zoom expressions:**
- Zoom in: `z='min(zoom+0.003,2.0)'` (slowly increases zoom to 2x)
- Zoom out: `z='if(lte(zoom,1.0),2.0,max(1.001,zoom-0.003))'` (starts at 2x, zooms out)
- Hold then zoom: `z='if(lte(on,30),1,min(zoom+0.005,2.5))'` (hold 1s, then zoom)

---

## 8. py-staticmaps — Full Python Recipe

This is the **easiest fully-free method** — no API keys, no signup.

### Install

```bash
pip install py-staticmaps Pillow
# For anti-aliased output (recommended):
pip install "py-staticmaps[cairo]"
```

### Generate All Murdaugh Case Maps

```python
#!/usr/bin/env python3
"""Generate map visuals for Murdaugh case using py-staticmaps."""

import staticmaps

# --- Tile Providers ---
SATELLITE = staticmaps.TileProvider(
    name="arcgis-worldimagery",
    url_pattern="https://server.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer/tile/$z/$y/$x",
    attribution="Esri, Earthstar Geographics",
    max_zoom=20,
)

DARK = staticmaps.TileProvider(
    name="carto-dark",
    url_pattern="http://$s.basemaps.cartocdn.com/rastertiles/dark_all/$z/$x/$y.png",
    shards=["a", "b", "c", "d"],
    attribution="CartoDB",
    max_zoom=20,
)

DARK_NOLABELS = staticmaps.TileProvider(
    name="carto-dark-nolabels",
    url_pattern="http://$s.basemaps.cartocdn.com/rastertiles/dark_nolabels/$z/$x/$y.png",
    shards=["a", "b", "c", "d"],
    attribution="CartoDB",
    max_zoom=20,
)

# --- Locations ---
MOSELLE = staticmaps.create_latlng(32.836, -80.846)
COURTHOUSE = staticmaps.create_latlng(32.9052, -80.6668)
ARCHERS_CREEK = staticmaps.create_latlng(32.3917, -80.675)
ALMEDA = staticmaps.create_latlng(32.625, -81.1)

RED = staticmaps.parse_color("#ff0000")
ORANGE = staticmaps.parse_color("#ff8800")
WHITE = staticmaps.parse_color("#ffffff")


def make_map(tile_provider, locations, zoom=None, width=1920, height=1080, filename="map.png"):
    """Generate a single map image."""
    ctx = staticmaps.Context()
    ctx.set_tile_provider(tile_provider)

    for latlng, color, size in locations:
        ctx.add_object(staticmaps.Marker(latlng, color=color, size=size))

    if zoom is not None:
        # Force specific zoom by setting center
        center = locations[0][0] if len(locations) == 1 else None
        if center:
            ctx.set_center(center)
        ctx.set_zoom(zoom)

    image = ctx.render_pillow(width, height)
    image.save(filename)
    print(f"Saved: {filename}")


# === 1. Moselle Estate — Satellite Close-up ===
make_map(SATELLITE,
         [(MOSELLE, RED, 16)],
         zoom=14, filename="01_moselle_satellite.png")

# === 2. Moselle Estate — Dark Theme ===
make_map(DARK,
         [(MOSELLE, RED, 16)],
         zoom=12, filename="02_moselle_dark.png")

# === 3. Courthouse — Satellite ===
make_map(SATELLITE,
         [(COURTHOUSE, RED, 16)],
         zoom=16, filename="03_courthouse_satellite.png")

# === 4. Archers Creek — Satellite ===
make_map(SATELLITE,
         [(ARCHERS_CREEK, ORANGE, 16)],
         zoom=15, filename="04_archers_creek_satellite.png")

# === 5. Almeda Area — Dark ===
make_map(DARK,
         [(ALMEDA, RED, 16)],
         zoom=13, filename="05_almeda_dark.png")

# === 6. Lowcountry Overview — All Locations ===
make_map(DARK,
         [(MOSELLE, RED, 12),
          (COURTHOUSE, RED, 12),
          (ARCHERS_CREEK, ORANGE, 12),
          (ALMEDA, RED, 12)],
         zoom=9, filename="06_lowcountry_overview_dark.png")

# === 7. Lowcountry Overview — Satellite ===
make_map(SATELLITE,
         [(MOSELLE, RED, 12),
          (COURTHOUSE, RED, 12),
          (ARCHERS_CREEK, ORANGE, 12),
          (ALMEDA, RED, 12)],
         zoom=9, filename="07_lowcountry_overview_satellite.png")

# === 8. Zoom Animation Frames (for FFmpeg) ===
print("\n--- Generating zoom animation frames ---")
for z in [4, 6, 8, 10, 12, 14, 16]:
    make_map(SATELLITE,
             [(MOSELLE, RED, 12 if z < 10 else 16)],
             zoom=z,
             filename=f"anim_moselle_z{z:02d}.png")


print("\nDone! Run FFmpeg to create zoom animation:")
print("  See Section 7 of the guide for FFmpeg commands.")
```

### Run It

```bash
python3 murdaugh_maps.py
```

Output files:
```
01_moselle_satellite.png     — Moselle estate aerial view
02_moselle_dark.png          — Moselle on dark basemap
03_courthouse_satellite.png  — Colleton County Courthouse
04_archers_creek_satellite.png — Boat crash site
05_almeda_dark.png           — Alex's mother's house area
06_lowcountry_overview_dark.png — All locations on dark map
07_lowcountry_overview_satellite.png — All locations on satellite
anim_moselle_z04.png through anim_moselle_z16.png — Zoom animation frames
```

---

## 9. Quick Reference: Tile Coordinate Calculator

Use this to convert lat/lon to tile coordinates for direct tile downloads.

```python
import math

def deg2tile(lat_deg, lon_deg, zoom):
    """Convert latitude/longitude to tile x,y at given zoom level."""
    lat_rad = math.radians(lat_deg)
    n = 1 << zoom  # 2^zoom
    x = int((lon_deg + 180.0) / 360.0 * n)
    y = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return x, y

# Murdaugh case tile coordinates at key zoom levels:
locations = {
    "Moselle Estate":    (32.836, -80.846),
    "Courthouse":        (32.9052, -80.6668),
    "Archers Creek":     (32.3917, -80.675),
    "Almeda":            (32.625, -81.1),
}

for name, (lat, lon) in locations.items():
    print(f"\n{name} ({lat}, {lon}):")
    for z in [6, 8, 10, 12, 14, 16]:
        x, y = deg2tile(lat, lon, z)
        esri = f"https://server.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
        print(f"  z{z:2d}: tile({x}, {y})  {esri}")
```

**Pre-computed tiles for Moselle Estate (32.836, -80.846):**

| Zoom | Tile X | Tile Y | ArcGIS Satellite URL |
|------|--------|--------|---------------------|
| 6 | 17 | 25 | `.../tile/6/25/17` |
| 8 | 70 | 102 | `.../tile/8/102/70` |
| 10 | 280 | 410 | `.../tile/10/410/280` |
| 12 | 1121 | 1640 | `.../tile/12/1640/1121` |
| 14 | 4484 | 6562 | `.../tile/14/6562/4484` |
| 16 | 17937 | 26250 | `.../tile/16/26250/17937` |

Full URL example (zoom 14):
```
https://server.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer/tile/14/6562/4484
```

---

## Appendix: Recommended Workflow for a True Crime Video

1. **Overview shot:** Lowcountry 5-county map on dark basemap (Carto Dark) with all location pins — zoom 8-9
2. **Location intros:** Each location on satellite at zoom 14-16 with red marker
3. **Zoom animation:** Download satellite tiles at z4 through z16 → FFmpeg zoompan → 5-second zoom-in clip
4. **Transition style:** Crossfade between dark overview and satellite close-up
5. **Text overlays:** Add location names with FFmpeg drawtext filter:

```bash
ffmpeg -i moselle_satellite.png \
  -vf "drawtext=text='Moselle Estate, Islandton SC':fontsize=36:fontcolor=white:borderw=2:bordercolor=black:x=(w-text_w)/2:y=h-60" \
  -frames:v 1 moselle_labeled.png
```

### Cost Summary

| Method | Monthly Free | Per Video (est. 20 images) | API Key? |
|--------|-------------|---------------------------|----------|
| py-staticmaps + ArcGIS/Carto tiles | Unlimited | $0 | No |
| Mapbox Static | 100K requests | $0 | Yes (free) |
| Google Maps Static | ~100K requests ($200 credit) | $0 | Yes (free credit) |
| Direct tile download + PIL stitch | Unlimited | $0 | No |
