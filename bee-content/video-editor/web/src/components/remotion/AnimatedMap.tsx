import { useEffect, useRef, useCallback, useState } from 'react';
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig, continueRender, delayRender } from 'remotion';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import type { OverlayProps } from './overlays';

// --- Types ---

interface Waypoint {
  lat: number;
  lng: number;
  zoom?: number;
  bearing?: number;
  pitch?: number;
}

interface MapMetadata {
  lat?: number;
  lng?: number;
  zoom?: number;
  animation?: 'fly_to' | 'zoom_in' | 'zoom_out' | 'pulse' | 'orbit' | 'route';
  style?: 'satellite' | 'dark' | 'tactical';
  waypoints?: Waypoint[];
  route?: { lat: number; lng: number }[];
}

// --- Tile sources ---

const TILE_STYLES: Record<string, maplibregl.StyleSpecification> = {
  satellite: {
    version: 8,
    sources: {
      'esri-satellite': {
        type: 'raster',
        tiles: [
          'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        ],
        tileSize: 256,
        attribution: '© Esri',
      },
    },
    layers: [{ id: 'satellite', type: 'raster', source: 'esri-satellite' }],
  },
  dark: {
    version: 8,
    sources: {
      'carto-dark': {
        type: 'raster',
        tiles: [
          'https://basemaps.cartocdn.com/dark_all/{z}/{x}/{y}@2x.png',
        ],
        tileSize: 256,
        attribution: '© CARTO © OpenStreetMap',
      },
    },
    layers: [{ id: 'dark', type: 'raster', source: 'carto-dark' }],
  },
  tactical: {
    version: 8,
    sources: {
      'carto-dark': {
        type: 'raster',
        tiles: [
          'https://basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}@2x.png',
        ],
        tileSize: 256,
        attribution: '© CARTO © OpenStreetMap',
      },
      'carto-labels': {
        type: 'raster',
        tiles: [
          'https://basemaps.cartocdn.com/dark_only_labels/{z}/{x}/{y}@2x.png',
        ],
        tileSize: 256,
      },
    },
    layers: [
      { id: 'dark-base', type: 'raster', source: 'carto-dark' },
      { id: 'labels', type: 'raster', source: 'carto-labels', paint: { 'raster-opacity': 0.8 } },
    ],
  },
};

// --- Helpers ---

function lerp(a: number, b: number, t: number): number {
  return a + (b - a) * t;
}

function interpolateWaypoints(waypoints: Waypoint[], progress: number): Waypoint {
  if (waypoints.length === 1) return waypoints[0];
  const idx = progress * (waypoints.length - 1);
  const i = Math.floor(idx);
  const t = idx - i;
  const a = waypoints[Math.min(i, waypoints.length - 1)];
  const b = waypoints[Math.min(i + 1, waypoints.length - 1)];
  return {
    lat: lerp(a.lat, b.lat, t),
    lng: lerp(a.lng, b.lng, t),
    zoom: lerp(a.zoom ?? 14, b.zoom ?? 14, t),
    bearing: lerp(a.bearing ?? 0, b.bearing ?? 0, t),
    pitch: lerp(a.pitch ?? 0, b.pitch ?? 0, t),
  };
}

// --- Component ---

export interface AnimatedMapProps {
  content: string;
  metadata?: Record<string, any> | null;
  durationInFrames: number;
  mode?: 'visual' | 'overlay';
}

export const AnimatedMap: React.FC<AnimatedMapProps> = ({
  content, metadata, durationInFrames, mode = 'visual',
}) => {
  const frame = useCurrentFrame();
  useVideoConfig(); // required by Remotion context
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const [mapReady, setMapReady] = useState(false);
  const [handle] = useState(() => delayRender('Loading map tiles'));

  const meta: MapMetadata = (metadata as MapMetadata) || {};
  const lat = meta.lat ?? 32.84;
  const lng = meta.lng ?? -80.78;
  const targetZoom = meta.zoom ?? 14;
  const animation = meta.animation ?? 'fly_to';
  const mapStyle = meta.style ?? 'satellite';
  const waypoints = meta.waypoints;
  const route = meta.route;

  const label = content || '';

  // Initialize map
  useEffect(() => {
    if (!mapContainerRef.current) return;

    const style = TILE_STYLES[mapStyle] || TILE_STYLES.satellite;

    // Start position depends on animation type
    let startZoom = targetZoom;
    let startLat = lat;
    let startLng = lng;
    if (animation === 'fly_to') startZoom = 3;
    else if (animation === 'zoom_out') startZoom = targetZoom + 4;
    else if (animation === 'zoom_in') startZoom = targetZoom - 3;

    if (waypoints && waypoints.length > 0) {
      startLat = waypoints[0].lat;
      startLng = waypoints[0].lng;
      startZoom = waypoints[0].zoom ?? 4;
    }

    const map = new maplibregl.Map({
      container: mapContainerRef.current,
      style,
      center: [startLng, startLat],
      zoom: startZoom,
      bearing: waypoints?.[0]?.bearing ?? 0,
      pitch: waypoints?.[0]?.pitch ?? 0,
      interactive: false,
      attributionControl: false,
      fadeDuration: 0,
    });

    map.on('load', () => {
      // Add route line source if needed
      if (route && route.length >= 2) {
        map.addSource('route', {
          type: 'geojson',
          data: {
            type: 'Feature',
            properties: {},
            geometry: {
              type: 'LineString',
              coordinates: route.map(p => [p.lng, p.lat]),
            },
          },
        });
        map.addLayer({
          id: 'route-line',
          type: 'line',
          source: 'route',
          layout: { 'line-cap': 'round', 'line-join': 'round' },
          paint: { 'line-color': '#DC3232', 'line-width': 4, 'line-opacity': 0.9 },
        });
      }

      mapRef.current = map;
      setMapReady(true);
      continueRender(handle);
    });

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  // Update camera per frame
  const updateCamera = useCallback(() => {
    const map = mapRef.current;
    if (!map || !mapReady) return;

    const progress = interpolate(frame, [0, durationInFrames - 15], [0, 1], {
      extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
    });

    if (waypoints && waypoints.length > 0) {
      // Cinematic waypoint path
      const wp = interpolateWaypoints(waypoints, progress);
      map.jumpTo({
        center: [wp.lng, wp.lat],
        zoom: wp.zoom ?? 14,
        bearing: wp.bearing ?? 0,
        pitch: wp.pitch ?? 0,
      });
    } else if (animation === 'fly_to') {
      const z = interpolate(progress, [0, 1], [3, targetZoom]);
      map.jumpTo({ center: [lng, lat], zoom: z });
    } else if (animation === 'zoom_in') {
      const z = interpolate(progress, [0, 1], [targetZoom - 3, targetZoom]);
      map.jumpTo({ center: [lng, lat], zoom: z });
    } else if (animation === 'zoom_out') {
      const z = interpolate(progress, [0, 1], [targetZoom + 4, targetZoom]);
      map.jumpTo({ center: [lng, lat], zoom: z });
    } else if (animation === 'orbit') {
      const bearing = interpolate(progress, [0, 1], [0, 360]);
      map.jumpTo({ center: [lng, lat], zoom: targetZoom, bearing, pitch: 45 });
    } else if (animation === 'route' && route && route.length >= 2) {
      // Follow the route
      const routeIdx = progress * (route.length - 1);
      const i = Math.floor(routeIdx);
      const t = routeIdx - i;
      const a = route[Math.min(i, route.length - 1)];
      const b = route[Math.min(i + 1, route.length - 1)];
      const cLat = lerp(a.lat, b.lat, t);
      const cLng = lerp(a.lng, b.lng, t);
      map.jumpTo({ center: [cLng, cLat], zoom: targetZoom });
    } else {
      // pulse — static
      map.jumpTo({ center: [lng, lat], zoom: targetZoom });
    }
  }, [frame, mapReady, durationInFrames, animation, lat, lng, targetZoom, waypoints, route]);

  useEffect(() => {
    updateCamera();
  }, [updateCamera]);

  // Exit fade
  const exitOpacity = interpolate(frame, [durationInFrames - 15, durationInFrames], [1, 0], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });

  // Pulsing marker
  const pulseScale = 1 + Math.sin(frame * 0.15) * 0.3;
  const pulseOpacity = 0.6 + Math.sin(frame * 0.15) * 0.3;
  const showMarker = animation === 'pulse' || animation === 'fly_to' || animation === 'zoom_in';
  const markerAppear = interpolate(frame, [durationInFrames * 0.3, durationInFrames * 0.4], [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill style={{ opacity: exitOpacity }}>
      {/* Map container */}
      <div
        ref={mapContainerRef}
        style={{
          position: 'absolute',
          inset: mode === 'overlay' ? '10% 15%' : 0,
          borderRadius: mode === 'overlay' ? 12 : 0,
          overflow: 'hidden',
        }}
      />

      {/* Marker overlay */}
      {showMarker && markerAppear > 0 && (
        <div style={{
          position: 'absolute',
          top: '50%', left: '50%',
          transform: 'translate(-50%, -50%)',
          display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8,
          opacity: markerAppear,
        }}>
          {/* Pulsing ring */}
          <div style={{
            width: 40, height: 40,
            borderRadius: '50%',
            border: '3px solid #DC3232',
            transform: `scale(${pulseScale})`,
            opacity: pulseOpacity,
            boxShadow: '0 0 20px rgba(220, 50, 50, 0.5)',
          }} />
          {/* Center dot */}
          <div style={{
            position: 'absolute',
            top: '50%', left: '50%',
            transform: 'translate(-50%, -50%)',
            width: 12, height: 12,
            borderRadius: '50%',
            backgroundColor: '#DC3232',
            boxShadow: '0 0 10px rgba(220, 50, 50, 0.8)',
          }} />
        </div>
      )}

      {/* Location label */}
      {label && (
        <div style={{
          position: 'absolute',
          bottom: mode === 'overlay' ? 'calc(10% + 20px)' : 40,
          left: '50%',
          transform: 'translateX(-50%)',
          opacity: interpolate(frame, [durationInFrames * 0.3, durationInFrames * 0.4], [0, 1], {
            extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
          }),
        }}>
          <div style={{
            background: 'rgba(0,0,0,0.7)',
            padding: '8px 20px',
            borderRadius: 6,
            color: '#fff',
            fontSize: 18,
            fontWeight: 600,
            fontFamily: 'Arial',
            whiteSpace: 'nowrap',
          }}>
            📍 {label}
          </div>
        </div>
      )}
    </AbsoluteFill>
  );
};

// Overlay wrapper
export const AnimatedMapOverlay: React.FC<OverlayProps> = (props) => (
  <AnimatedMap {...props} mode="overlay" />
);
