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
  // const [userLocation, setUserLocation] = useState<{ lat: number, lng: number } | null>(null);
  const [currentZone, setCurrentZone] = useState<string>('');

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

  // Helper function to get color based on severity
  const getSeverityColor = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case 'severe': return { bg: '#DC2626', border: '#991B1B', text: 'Severe' }; // Red
      case 'moderate': return { bg: '#F59E0B', border: '#D97706', text: 'Moderate' }; // Orange
      case 'mild': return { bg: '#10B981', border: '#059669', text: 'Mild' }; // Green
      default: return { bg: '#6B7280', border: '#4B5563', text: 'Unknown' }; // Gray
    }
  };

  // Update markers when outbreaks change
  useEffect(() => {
    if (!map.current || !mapLoaded) return;

    // Clear existing markers
    markersRef.current.forEach(marker => marker.remove());
    markersRef.current = [];

    // Aggregate outbreaks by city/region
    const cityZones: { [key: string]: any } = {};

    outbreaks.forEach(outbreak => {
      const loc = outbreak.hospital?.location || outbreak.location || {};
      const lat = loc.lat || loc.latitude;
      const lng = loc.lng || loc.longitude;
      const city = loc.city || outbreak.city || outbreak.location_name || 'Unknown Zone';

      // Strict validation: must be numbers and non-zero (unless actually 0,0 which is likely invalid for India but technically a coord)
      // Actually 0,0 is off coast of Africa. Let's filter out invalid/missing.
      if (lat === undefined || lng === undefined || lat === null || lng === null) return;

      if (!cityZones[city]) {
        cityZones[city] = {
          city: city,
          state: loc.state || outbreak.state,
          lat: lat, // Use first outbreak loc as center (simple arg rep)
          lng: lng,
          totalCases: 0,
          severityScore: 0, // for calc max severity
          hospitals: [],
          diseases: new Set()
        };
      }

      // Add data
      const patientCount = outbreak.patient_count || outbreak.cases || 0;
      cityZones[city].totalCases += patientCount;
      cityZones[city].hospitals.push({
        name: outbreak.hospital?.name || outbreak.location_name || 'Unknown Hospital',
        cases: patientCount,
        disease: outbreak.disease_type || outbreak.disease,
        severity: outbreak.severity,
        date: outbreak.date_started || outbreak.reported_date
      });
      cityZones[city].diseases.add(outbreak.disease_type || outbreak.disease);

      // Severity scoring: severe=3, moderate=2, mild=1
      let score = 1;
      if (outbreak.severity === 'severe') score = 3;
      else if (outbreak.severity === 'moderate') score = 2;

      // Keep max severity
      if (score > cityZones[city].severityScore) {
        cityZones[city].severityScore = score;
        cityZones[city].maxSeverity = outbreak.severity;
      }
    });

    const aggregatedZones = Object.values(cityZones);

    console.log(`✅ Map: Aggregated ${outbreaks.length} reports into ${aggregatedZones.length} zones per area.`);

    aggregatedZones.forEach(zone => {
      const { lat, lng, totalCases, maxSeverity, city, hospitals, diseases } = zone;

      const severity = maxSeverity || 'moderate';
      const severityInfo = getSeverityColor(severity);
      const diseaseList = Array.from(diseases as Set<string>).join(", ");

      // Professional light colors
      const severityColors = {
        severe: { fill: '#fca5a5', stroke: '#ef4444', shadow: 'rgba(239, 68, 68, 0.4)' },
        moderate: { fill: '#fde68a', stroke: '#f59e0b', shadow: 'rgba(245, 158, 11, 0.4)' },
        mild: { fill: '#86efac', stroke: '#22c55e', shadow: 'rgba(34, 197, 94, 0.4)' }
      };

      const colors = severityColors[severity as keyof typeof severityColors] || severityColors.moderate;

      // Create marker element
      const el = document.createElement('div');
      el.className = 'outbreak-marker';
      el.innerHTML = `
        <svg width="40" height="40" viewBox="0 0 40 40" style="filter: drop-shadow(0 2px 6px ${colors.shadow});">
          <circle cx="20" cy="20" r="16" 
                  fill="${colors.fill}" 
                  stroke="${colors.stroke}" 
                  stroke-width="3"
                  opacity="0.9"/>
          <!-- Optional: Number badge for # of hospitals if > 1 -->
          ${hospitals.length > 1 ? `<circle cx="30" cy="10" r="8" fill="white" stroke="#666" stroke-width="1"/><text x="30" y="14" text-anchor="middle" font-size="10" font-weight="bold" fill="#333">${hospitals.length}</text>` : ''}
        </svg>
      `;

      el.style.cursor = 'pointer';
      el.style.cursor = 'pointer';
      el.title = `${city} Zone - ${totalCases} Total Cases`;

      // Popup HTML with aggregated list
      let hospitalListHTML = hospitals.map((h: any) => `
        <div class="border-b border-gray-100 py-2 last:border-0">
          <div class="flex justify-between items-start">
            <span class="font-medium text-gray-800 text-xs">${h.name}</span>
            <span class="text-[10px] px-1.5 py-0.5 rounded-full ${h.severity === 'severe' ? 'bg-red-100 text-red-700' : h.severity === 'moderate' ? 'bg-yellow-100 text-yellow-700' : 'bg-green-100 text-green-700'}">${h.severity}</span>
          </div>
          <div class="flex justify-between text-[10px] text-gray-500 mt-0.5">
            <span>${h.disease}</span>
            <span class="font-bold">${h.cases} cases</span>
          </div>
        </div>
      `).join('');

      const popupHTML = `
        <div class="p-0 min-w-[240px] max-h-[300px] overflow-y-auto custom-scrollbar">
          <div class="sticky top-0 bg-white border-b border-gray-200 p-3 z-10 pb-2">
            <div class="flex items-center gap-2 mb-1">
              <div class="w-3 h-3 rounded-full" style="background-color: ${severityInfo.bg};"></div>
              <h3 class="font-bold text-gray-900 text-base">${city} Zone</h3>
            </div>
            <p class="text-xs text-gray-500">Combining reports from <span class="font-bold">${hospitals.length} hospitals</span></p>
            <div class="flex gap-2 mt-2">
               <div class="text-xs bg-gray-50 px-2 py-1 rounded border border-gray-200">
                 👥 <span class="font-bold">${totalCases}</span> Cases
               </div>
               <div class="text-xs bg-gray-50 px-2 py-1 rounded border border-gray-200">
                 🦠 ${diseaseList.split(',')[0]} ${diseaseList.includes(',') ? '...' : ''}
               </div>
            </div>
          </div>
          <div class="p-3 bg-gray-50/50">
            <h4 class="text-[10px] uppercase font-bold text-gray-400 mb-1">Detailed Reports</h4>
            ${hospitalListHTML}
          </div>
        </div>
      `;

      const popup = new maplibregl.Popup({ offset: 25, closeButton: true, maxWidth: '300px' }).setHTML(popupHTML);

      const marker = new maplibregl.Marker({ element: el })
        .setLngLat([lng, lat])
        .setPopup(popup)
        .addTo(map.current!);

      markersRef.current.push(marker);
    });



    console.log(`✅ Map: Added ${outbreaks.length} outbreak markers`);

    // Add dynamic data-driven zones from actual data
    if (map.current) {
      const sourceId = 'outbreak-zones-source';
      const layerId = 'outbreak-zones-layer';

      // Clean up existing
      if (map.current.getLayer(`${layerId}-core`)) map.current.removeLayer(`${layerId}-core`);
      if (map.current.getLayer(layerId)) map.current.removeLayer(layerId);
      if (map.current.getSource(sourceId)) map.current.removeSource(sourceId);

      if (outbreaks.length > 0) {
        // Create GeoJSON features from AGGREGATED ZONES
        const features = aggregatedZones.map(zone => {
          // Mapping aggregated data to feature
          const { lat, lng, totalCases, maxSeverity, city } = zone;

          if (!lat || !lng) return null;

          let color = '#fde68a';
          let radius = 10;

          if (maxSeverity === 'severe') {
            color = '#fca5a5';
            radius = 15;
          } else if (maxSeverity === 'mild') {
            color = '#86efac';
            radius = 8;
          }

          return {
            type: 'Feature',
            geometry: {
              type: 'Point',
              coordinates: [lng, lat]
            },
            properties: {
              severity: maxSeverity,
              color: color,
              radius: radius,
              count: totalCases,
              description: `Risk Zone: ${city}`
            }
          };
        }).filter(Boolean);

        // Add a source for the risk zones
        map.current.addSource(sourceId, {
          type: 'geojson',
          data: {
            type: 'FeatureCollection',
            features: features as any[]
          }
        });

        // Add "Pro" Heatmap/risk zone layer using interpolate for smooth gradients
        map.current.addLayer({
          id: layerId,
          type: 'circle',
          source: sourceId,
          paint: {
            // Dynamic radius based on zoom AND count (cases)
            // At zoom 5: 1 case=20px, 100 cases=50px
            // At zoom 10: 1 case=40px, 100 cases=100px
            // Dynamic radius based on patient count (aggregated)
            // Scale: 10px (small) -> 60px (large)
            'circle-radius': [
              'interpolate',
              ['linear'],
              ['sqrt', ['get', 'count']],
              0, 10,
              100, 60
            ],
            // Heatmap gradient color based on severity
            'circle-color': [
              'match',
              ['get', 'severity'],
              'severe', '#ef4444',   // Red-500
              'moderate', '#f59e0b', // Amber-500
              'mild', '#3b82f6',     // Blue-500
              '#cccccc'
            ],
            // Opacity for "glow" effect
            'circle-opacity': 0.5,
            // Blur to make it look like a heatmap/cloud
            'circle-blur': 0.4,
            'circle-stroke-width': 1,
            'circle-stroke-color': '#ffffff',
            'circle-stroke-opacity': 0.3
          }
        });

        // Add a "Core" layer for precise center points
        map.current.addLayer({
          id: `${layerId}-core`,
          type: 'circle',
          source: sourceId,
          paint: {
            'circle-radius': 4,
            'circle-color': '#ffffff',
            'circle-opacity': 0.9,
            'circle-stroke-width': 2,
            'circle-stroke-color': [
              'match',
              ['get', 'severity'],
              'severe', '#ef4444',
              'moderate', '#f59e0b',
              'mild', '#3b82f6',
              '#999'
            ]
          }
        });  // Actually DOM markers are on top of canvas. The layer order matters for other map layers.
      }
    }

    // Auto-zoom map to show all outbreaks
    if (outbreaks.length > 0 && map.current) {
      const bounds = new maplibregl.LngLatBounds();

      outbreaks.forEach(outbreak => {
        const loc = outbreak.hospital?.location || outbreak.location || {};
        const lat = loc.lat || loc.latitude;
        const lng = loc.lng || loc.longitude;

        if (typeof lat === 'number' && typeof lng === 'number') {
          bounds.extend([lng, lat]);
        }
      });

      // Fit map to show all markers
      map.current.fitBounds(bounds, {
        padding: { top: 80, bottom: 80, left: 80, right: 80 },
        maxZoom: 6,
        duration: 1500
      });

      console.log(`🗺️ Map: Zoomed to show ${outbreaks.length} outbreak zones`);
    } else {
      console.log('ℹ️ Map: No outbreak data - showing default view');
    }
  }, [outbreaks, mapLoaded, onOutbreakClick]);



  // Function to get user's location
  const getUserLocation = () => {
    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          // const { latitude, longitude } = position.coords;
          // setUserLocation({ lat: latitude, lng: longitude });
          const { latitude, longitude } = position.coords;

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

            // Just update text
            setCurrentZone("Monitoring active outbreaks...");
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

  // Calculate counts for render
  const severeCount = outbreaks.filter(o => o.severity === 'severe').length;
  const moderateCount = outbreaks.filter(o => o.severity === 'moderate').length;
  const mildCount = outbreaks.filter(o => o.severity === 'mild').length;

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
            <div className="text-[10px] text-gray-500 font-semibold uppercase">Status</div>
          </div>
          <div className="text-xs font-bold text-gray-900 mt-1">{currentZone}</div>
        </div>
      )}

      {/* Legend */}
      <div className="absolute bottom-4 left-4 bg-white/95 backdrop-blur-sm p-3 rounded-lg shadow-lg border border-gray-200">
        <div className="text-xs font-bold text-gray-800 mb-2">🎯 Risk Zones</div>
        <div className="space-y-1.5">
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded-full bg-red-400 border border-red-500 shadow-sm opacity-80"></div>
              <span className="text-xs text-gray-700 font-medium">Severe</span>
            </div>
            <span className="text-xs font-bold text-gray-900">{severeCount}</span>
          </div>

          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded-full bg-yellow-300 border border-yellow-500 shadow-sm opacity-80"></div>
              <span className="text-xs text-gray-700 font-medium">Moderate</span>
            </div>
            <span className="text-xs font-bold text-gray-900">{moderateCount}</span>
          </div>

          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded-full bg-green-300 border border-green-500 shadow-sm opacity-80"></div>
              <span className="text-xs text-gray-700 font-medium">Mild</span>
            </div>
            <span className="text-xs font-bold text-gray-900">{mildCount}</span>
          </div>
        </div>
        <div className="mt-2 pt-2 border-t border-gray-200">
          <div className="text-[10px] text-gray-500 flex justify-between items-center">
            <span>Total Zones:</span>
            <span className="font-bold text-gray-700">{outbreaks.length}</span>
          </div>
        </div>
      </div>

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
