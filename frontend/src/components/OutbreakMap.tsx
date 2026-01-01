/*
 * Outbreak Map Component
 * Renders MapLibre map with markers and risk zones (colored circles)
 */

import React, { useEffect, useRef, useState } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { SymptoMapAPI } from '../services/api';
import { useWebSocket } from '../hooks/useWebSocket';

interface OutbreakMapProps {
  outbreaks?: any[];
  onOutbreakClick?: (outbreak: any) => void;
}

const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000/api/v1';
const WS_URL = API_BASE_URL.replace('http', 'ws').replace('/api/v1', '') + '/api/v1/ws';

export const OutbreakMap: React.FC<OutbreakMapProps> = ({ onOutbreakClick = () => { } }) => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const [mapLoaded, setMapLoaded] = useState(false);
  const [outbreaks, setOutbreaks] = useState<any[]>([]);
  const markersRef = useRef<maplibregl.Marker[]>([]);
  const [_userLocation, setUserLocation] = useState<{ lat: number, lng: number } | null>(null);
  const [currentZone, setCurrentZone] = useState<string>('');
  const [selectedOutbreak, setSelectedOutbreak] = useState<any | null>(null);
  const [isPanelOpen, setIsPanelOpen] = useState(false);


  // Real-time WebSocket connection
  const { lastMessage } = useWebSocket(WS_URL);

  // Fetch outbreaks on mount
  const loadOutbreaks = async () => {
    try {
      const data = await SymptoMapAPI.getOutbreaks({ days: 30 });
      setOutbreaks(data || []);
    } catch (error) {
      console.error('Failed to load outbreaks:', error);
    }
  };

  useEffect(() => {
    loadOutbreaks();
    const interval = setInterval(loadOutbreaks, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, []);

  // Listen for real-time outbreak events
  useEffect(() => {
    if (lastMessage?.type === 'NEW_OUTBREAK' || lastMessage?.type === 'NEW_ALERT') {
      console.log('🔄 Map: Refreshing due to real-time event');
      loadOutbreaks();
    }
  }, [lastMessage]);

  useEffect(() => {
    // Prevent double init
    if (map.current) return;
    if (!mapContainer.current) return;

    try {
      console.log('Initializing map...');
      map.current = new maplibregl.Map({
        container: mapContainer.current,
        style: {
          version: 8,
          sources: {
            'osm-tiles': {
              type: 'raster',
              tiles: [
                'https://a.tile.openstreetmap.org/{z}/{x}/{y}.png',
                'https://b.tile.openstreetmap.org/{z}/{x}/{y}.png',
                'https://c.tile.openstreetmap.org/{z}/{x}/{y}.png'
              ],
              tileSize: 256,
              attribution: '&copy; OpenStreetMap Contributors',
            }
          },
          layers: [
            {
              id: 'osm-tiles-layer',
              type: 'raster',
              source: 'osm-tiles',
              minzoom: 0,
              maxzoom: 19
            }
          ],
        },
        center: [78.9629, 20.5937], // Center on India (longitude, latitude)
        zoom: 5 // Zoom level to show Mumbai, Pune, Delhi region
      });

      map.current.on('load', () => {
        console.log('✅ Map initialized successfully');
        setMapLoaded(true);
        map.current?.resize();
      });

      map.current.on('error', (e) => {
        console.error('Map error:', e);
      });

      map.current.on('moveend', () => {
        // Map position updated
      });
    } catch (err) {
      console.error("Map initialization failed:", err);
    }

    return () => {
      // Cleanup markers on unmount
      markersRef.current.forEach(marker => marker.remove());
    };
  }, []);



  // Update map layers when outbreaks change
  useEffect(() => {
    if (!map.current || !mapLoaded) return;

    // Remove legacy markers if any exist in the ref
    if (markersRef.current.length > 0) {
      markersRef.current.forEach(marker => marker.remove());
      markersRef.current = [];
    }

    const sourceId = 'outbreaks-source';
    const zoneLayerId = 'outbreaks-zones';
    const centerLayerId = 'outbreaks-centers';

    // 1. Setup Data Source and Layers (only once)
    if (!map.current.getSource(sourceId)) {
      map.current.addSource(sourceId, {
        type: 'geojson',
        data: {
          type: 'FeatureCollection',
          features: []
        }
      });

      // Layer 1: Large semi-transparent Risk Zones (Circles)
      map.current.addLayer({
        id: zoneLayerId,
        type: 'circle',
        source: sourceId,
        paint: {
          // Radius based on cases: 10->50px, 500->100px
          'circle-radius': [
            'interpolate', ['linear'], ['get', 'cases'],
            1, 40,
            50, 60,
            100, 80,
            500, 120
          ],
          // Color based on severity property
          'circle-color': ['get', 'color'],
          'circle-opacity': 0.35,
          'circle-stroke-width': 1,
          'circle-stroke-color': ['get', 'strokeColor'],
          'circle-stroke-opacity': 0.6
        }
      });

      // Layer 2: Center Dots (Solid indicators)
      map.current.addLayer({
        id: centerLayerId,
        type: 'circle',
        source: sourceId,
        paint: {
          'circle-radius': 6,
          'circle-color': ['get', 'color'],
          'circle-opacity': 1,
          'circle-stroke-width': 2,
          'circle-stroke-color': '#FFFFFF'
        }
      });

      // Click Interaction
      map.current.on('click', zoneLayerId, (e) => {
        if (!e.features || e.features.length === 0) return;
        const feature = e.features[0];
        const props = feature.properties;

        // Construct simplified outbreak info for panel
        const outbreakInfo = {
          ...props,
          // MapLibre flattens properties, use them directly
          riskLevel: props.severity === 'Critical' ? 'Severe' : props.severity,
          riskColor: props.color,
          lat: (feature.geometry as any).coordinates[1],
          lng: (feature.geometry as any).coordinates[0]
        };

        setSelectedOutbreak(outbreakInfo);
        setIsPanelOpen(true);
      });

      // Cursor pointer on hover
      map.current.on('mouseenter', zoneLayerId, () => {
        if (map.current) map.current.getCanvas().style.cursor = 'pointer';
      });
      map.current.on('mouseleave', zoneLayerId, () => {
        if (map.current) map.current.getCanvas().style.cursor = '';
      });
    }

    // 2. Process Data into GeoJSON features
    const features = outbreaks.map(outbreak => {
      // Coordinate handling
      const lat = outbreak.location?.latitude || outbreak.location?.lat || outbreak.latitude || outbreak.hospital?.location?.lat;
      const lng = outbreak.location?.longitude || outbreak.location?.lng || outbreak.longitude || outbreak.hospital?.location?.lng;

      if (!lat || !lng) return null;

      // Determine Colors (Red, Yellow, Green)
      const severity = outbreak.severity || 'moderate';
      let color = '#EAB308'; // Yellow/Moderate default
      let strokeColor = '#CA8A04';

      const s = severity.toLowerCase();
      if (s === 'severe' || s === 'critical' || s === 'high') {
        color = '#DC2626'; // Red
        strokeColor = '#991B1B';
      } else if (s === 'mild' || s === 'low' || s === 'minimal') {
        color = '#22C55E'; // Green
        strokeColor = '#16A34A';
      }

      return {
        type: 'Feature',
        geometry: {
          type: 'Point',
          coordinates: [parseFloat(lng), parseFloat(lat)]
        },
        properties: {
          id: outbreak.id,
          disease: outbreak.disease || outbreak.disease_type || 'Unknown Disease',
          cases: parseInt(outbreak.cases || outbreak.patient_count || 1),
          severity: severity,
          locationName: outbreak.location?.name || outbreak.location_name || '',
          city: outbreak.location?.city || outbreak.city || '',
          state: outbreak.location?.state || outbreak.state || '',
          reportedDate: outbreak.reported_date || outbreak.date_reported || new Date().toISOString(),
          color: color,
          strokeColor: strokeColor,
          verified: outbreak.verified ? 1 : 0
        }
      };
    }).filter(f => f !== null);

    // 3. Update the Source Data
    const source = map.current.getSource(sourceId) as maplibregl.GeoJSONSource;
    if (source) {
      source.setData({
        type: 'FeatureCollection',
        features: features as any
      });
      console.log(`✅ map: Loaded ${features.length} zones into layer`);
    }

    // 4. Fit Map Bounds
    if (features.length > 0) {
      const bounds = new maplibregl.LngLatBounds();
      features.forEach(f => {
        const coords = (f.geometry as any).coordinates;
        bounds.extend(coords);
      });
      map.current.fitBounds(bounds, {
        padding: 80,
        maxZoom: 12 // Don't zoom in too close
      });
    }

  }, [outbreaks, mapLoaded, onOutbreakClick]);

  // Calculate distance between two points (Haversine formula)
  const calculateDistance = (lat1: number, lon1: number, lat2: number, lon2: number) => {
    const R = 6371000; // Earth's radius in meters
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
      Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  };

  // Function to get user's location
  const getUserLocation = () => {
    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          setUserLocation({ lat: latitude, lng: longitude });

          // Add user location marker
          if (map.current) {
            const userMarker = document.createElement('div');
            userMarker.innerHTML = `
              <svg width="30" height="30" viewBox="0 0 30 30">
                <circle cx="15" cy="15" r="12" fill="#3b82f6" stroke="white" stroke-width="3"/>
                <circle cx="15" cy="15" r="4" fill="white"/>
              </svg>
            `;
            new maplibregl.Marker({ element: userMarker })
              .setLngLat([longitude, latitude])
              .addTo(map.current);

            // Zoom to user location
            map.current.flyTo({ center: [longitude, latitude], zoom: 10 });

            // Detect which zone user is in
            const zones = [
              { name: 'Delhi Severe Zone', center: [77.2100, 28.5672], radius: 15000 },
              { name: 'Pune Moderate Zone', center: [73.8567, 18.5204], radius: 12000 },
              { name: 'Uttarakhand Mild Zone', center: [78.0322, 30.3165], radius: 10000 },
              { name: 'Bangalore Moderate Zone', center: [77.5980, 12.9443], radius: 12000 }
            ];

            let foundZone = 'No outbreak zone detected';
            zones.forEach(zone => {
              const distance = calculateDistance(latitude, longitude, zone.center[1], zone.center[0]);
              if (distance <= zone.radius) {
                foundZone = zone.name;
              }
            });
            setCurrentZone(foundZone);
          }
        },
        (error) => {
          console.error('Error getting location:', error);
          alert('Unable to get your location. Please enable location services.');
        }
      );
    }
  };

  // Auto-trigger location on map load
  useEffect(() => {
    if (mapLoaded && map.current) {
      // Wait a bit for map to be fully ready
      const timer = setTimeout(() => {
        getUserLocation();
      }, 1500);
      return () => clearTimeout(timer);
    }
  }, [mapLoaded]);

  return (
    <div className="relative w-full h-full">
      <div ref={mapContainer} className="w-full h-full rounded-lg overflow-hidden" />

      {/* Zoom Controls */}
      <div className="absolute top-4 right-4 flex flex-col gap-2 z-10">
        <button
          onClick={() => map.current?.zoomIn()}
          className="w-10 h-10 bg-white hover:bg-gray-100 rounded-lg shadow-lg flex items-center justify-center font-bold text-2xl text-gray-700 transition-all"
          title="Zoom In"
        >
          +
        </button>
        <button
          onClick={() => map.current?.zoomOut()}
          className="w-10 h-10 bg-white hover:bg-gray-100 rounded-lg shadow-lg flex items-center justify-center font-bold text-2xl text-gray-700 transition-all"
          title="Zoom Out"
        >
          −
        </button>
      </div>

      {/* Location Button */}
      <div className="absolute top-4 left-4 z-10">
        <button
          onClick={getUserLocation}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg shadow-lg flex items-center gap-2 font-semibold transition-all"
          title="Get My Location"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          My Location
        </button>
      </div>

      {/* Current Zone Indicator - Bottom Right Corner, Small Size */}
      {currentZone && (
        <div className="absolute bottom-4 right-4 z-10 bg-white/95 backdrop-blur-sm rounded-lg shadow-lg px-3 py-2 border border-gray-200">
          <div className="flex items-center gap-2">
            <svg className="w-3 h-3 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
            </svg>
            <div className="text-[10px] text-gray-500 font-semibold uppercase">Zone</div>
          </div>
          <div className="text-xs font-bold text-gray-900 mt-1">{currentZone}</div>
        </div>
      )}

      {/* Updated Legend - 3 Zones Only */}
      <div className="absolute bottom-4 left-4 bg-white/95 backdrop-blur-sm p-3 rounded-lg shadow-lg border border-gray-200">
        <div className="text-xs font-bold text-gray-800 mb-2">🎯 Risk Zones</div>
        <div className="space-y-1.5">
          <div className="flex items-center gap-2">
            <div className="w-5 h-5 rounded-full bg-gradient-to-br from-red-500 to-red-600 shadow-md"></div>
            <span className="text-xs text-gray-700 font-medium">Severe</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-5 h-5 rounded-full bg-gradient-to-br from-yellow-400 to-amber-500 shadow-md"></div>
            <span className="text-xs text-gray-700 font-medium">Moderate</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-5 h-5 rounded-full bg-gradient-to-br from-green-400 to-green-500 shadow-md"></div>
            <span className="text-xs text-gray-700 font-medium">Mild</span>
          </div>
        </div>
        <div className="mt-2 pt-2 border-t border-gray-200">
          <div className="text-[10px] text-gray-500">
            Total Zones: <span className="font-bold text-gray-700">{outbreaks.length}</span>
          </div>
        </div>
      </div>

      {/* Slide-in Zone Details Panel */}
      <div
        className={`absolute top-0 right-0 h-full w-80 bg-white shadow-2xl transform transition-transform duration-300 ease-out z-40 ${isPanelOpen ? 'translate-x-0' : 'translate-x-full'
          }`}
      >
        {selectedOutbreak && (
          <div className="h-full flex flex-col">
            {/* Panel Header */}
            <div
              className="p-4 text-white"
              style={{ background: `linear-gradient(135deg, ${selectedOutbreak.riskColor}, ${selectedOutbreak.riskColor}dd)` }}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold uppercase tracking-wide opacity-80">
                  {selectedOutbreak.riskLevel} Risk Zone
                </span>
                <button
                  onClick={() => setIsPanelOpen(false)}
                  className="w-7 h-7 rounded-full bg-white/20 hover:bg-white/30 flex items-center justify-center transition-colors"
                >
                  ✕
                </button>
              </div>
              <h2 className="text-xl font-bold">{selectedOutbreak.disease}</h2>
              <p className="text-sm opacity-90 mt-1">
                📍 {selectedOutbreak.locationName}{selectedOutbreak.city ? `, ${selectedOutbreak.city}` : ''}
              </p>
            </div>

            {/* Panel Content */}
            <div className="flex-1 p-4 overflow-y-auto">
              {/* Stats Grid */}
              <div className="grid grid-cols-2 gap-3 mb-4">
                <div className="bg-gray-50 rounded-lg p-3 text-center">
                  <div className="text-2xl font-bold" style={{ color: selectedOutbreak.riskColor }}>
                    {selectedOutbreak.cases}
                  </div>
                  <div className="text-xs text-gray-500">Total Cases</div>
                </div>
                <div className="bg-gray-50 rounded-lg p-3 text-center">
                  <div className="text-2xl font-bold text-gray-700">
                    {selectedOutbreak.riskLevel}
                  </div>
                  <div className="text-xs text-gray-500">Risk Level</div>
                </div>
              </div>

              {/* Details */}
              <div className="space-y-3">
                <div className="flex items-center gap-3 p-2 bg-gray-50 rounded-lg">
                  <span className="text-lg">🗺️</span>
                  <div>
                    <div className="text-xs text-gray-500">State</div>
                    <div className="text-sm font-semibold text-gray-800">{selectedOutbreak.state || 'N/A'}</div>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-2 bg-gray-50 rounded-lg">
                  <span className="text-lg">📅</span>
                  <div>
                    <div className="text-xs text-gray-500">Reported Date</div>
                    <div className="text-sm font-semibold text-gray-800">
                      {new Date(selectedOutbreak.reportedDate).toLocaleDateString('en-IN', {
                        day: 'numeric',
                        month: 'short',
                        year: 'numeric'
                      })}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-2 bg-gray-50 rounded-lg">
                  <span className="text-lg">📍</span>
                  <div>
                    <div className="text-xs text-gray-500">Coordinates</div>
                    <div className="text-sm font-semibold text-gray-800">
                      {selectedOutbreak.lat?.toFixed(4)}, {selectedOutbreak.lng?.toFixed(4)}
                    </div>
                  </div>
                </div>
                {selectedOutbreak.verified && (
                  <div className="flex items-center gap-2 p-2 bg-green-50 rounded-lg text-green-700">
                    <span>✓</span>
                    <span className="text-sm font-semibold">Verified & Approved</span>
                  </div>
                )}
              </div>
            </div>

            {/* Panel Footer */}
            <div className="p-4 border-t border-gray-100">
              <button
                onClick={() => {
                  if (map.current && selectedOutbreak.lat && selectedOutbreak.lng) {
                    map.current.flyTo({
                      center: [selectedOutbreak.lng, selectedOutbreak.lat],
                      zoom: 10,
                      duration: 1500
                    });
                  }
                }}
                className="w-full py-2.5 bg-gray-900 hover:bg-gray-800 text-white rounded-lg font-medium text-sm transition-colors"
              >
                🔍 Zoom to Zone
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Panel Backdrop */}
      {isPanelOpen && (
        <div
          className="absolute inset-0 bg-black/20 z-30"
          onClick={() => setIsPanelOpen(false)}
        />
      )}

      {!mapLoaded && (
        <div className="absolute inset-0 bg-gray-100 flex items-center justify-center z-50">
          <div className="text-center">
            <div className="inline-block w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full animate-spin mb-2"></div>
            <p className="text-gray-600 font-medium">Loading map...</p>
          </div>
        </div>
      )}
    </div>
  );
};
