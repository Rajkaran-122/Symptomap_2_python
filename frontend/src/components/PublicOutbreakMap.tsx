/*
 * Public Outbreak Map Component
 * Renders MapLibre map with markers and risk zones (colored circles)
 * Uses public API endpoint and polling (no WebSockets)
 */

import React, { useEffect, useRef, useState } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';

interface PublicOutbreakMapProps {
    outbreaks: any[];
    activeLayer: 'heatmap' | 'clusters';
    onMapLoad: (map: maplibregl.Map) => void;
}

export const PublicOutbreakMap: React.FC<PublicOutbreakMapProps> = ({ outbreaks, activeLayer, onMapLoad }) => {
    const mapContainer = useRef<HTMLDivElement>(null);
    const map = useRef<maplibregl.Map | null>(null);
    const [mapLoaded, setMapLoaded] = useState(false);
    const markersRef = useRef<maplibregl.Marker[]>([]);

    useEffect(() => {
        // Prevent double init
        if (map.current) return;
        if (!mapContainer.current) return;

        try {
            console.log('Initializing public map...');
            map.current = new maplibregl.Map({
                container: mapContainer.current,
                style: {
                    version: 8,
                    sources: {
                        'carto-light': {
                            type: 'raster',
                            tiles: [
                                'https://a.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}@2x.png',
                                'https://b.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}@2x.png',
                                'https://c.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}@2x.png'
                            ],
                            tileSize: 256,
                            attribution: '', // We display it externally in the footer
                        }
                    },
                    layers: [
                        {
                            id: 'carto-light-layer',
                            type: 'raster',
                            source: 'carto-light',
                            minzoom: 0,
                            maxzoom: 19
                        }
                    ],
                },
                center: [78.9629, 20.5937], // Center on India
                zoom: 4.5,
                attributionControl: false // Hide default attribution
            });

            map.current.on('load', () => {
                console.log('✅ Public Map initialized successfully');
                setMapLoaded(true);
                if (map.current) {
                    map.current.resize();
                    onMapLoad(map.current);
                }
            });

            map.current.on('error', (e) => {
                console.error('Map error:', e);
            });

        } catch (err) {
            console.error("Map initialization failed:", err);
        }

        return () => {
            markersRef.current.forEach(marker => marker.remove());
        };
    }, []);

    // Helper function to get color based on severity
    const getSeverityColor = (severity: string) => {
        switch (severity?.toLowerCase()) {
            case 'severe': return { bg: '#DC2626', border: '#991B1B', text: 'Severe' };
            case 'moderate': return { bg: '#F59E0B', border: '#D97706', text: 'Moderate' };
            case 'mild': return { bg: '#10B981', border: '#059669', text: 'Mild' };
            default: return { bg: '#6B7280', border: '#4B5563', text: 'Unknown' };
        }
    };

    // Update markers or clusters when outbreaks change or mode changes
    useEffect(() => {
        if (!map.current || !mapLoaded) return;

        // Cleanup
        markersRef.current.forEach(marker => marker.remove());
        markersRef.current = [];
        if (map.current.getLayer('clusters')) map.current.removeLayer('clusters');
        if (map.current.getLayer('cluster-count')) map.current.removeLayer('cluster-count');
        if (map.current.getLayer('unclustered-point')) map.current.removeLayer('unclustered-point');
        if (map.current.getSource('outbreaks')) map.current.removeSource('outbreaks');

        // Aggregate outbreaks by city/region (Common logic)
        const cityZones: { [key: string]: any } = {};

        outbreaks.forEach(outbreak => {
            const loc = outbreak.location || {};
            const lat = loc.latitude;
            const lng = loc.longitude;
            const city = loc.city || loc.name || 'Unknown Zone';
            if (lat === undefined || lng === undefined || lat === 0 || lng === 0) return;

            if (!cityZones[city]) {
                cityZones[city] = {
                    city: city,
                    lat: lat,
                    lng: lng,
                    totalCases: 0,
                    severityScore: 0,
                    hospitals: [],
                    maxSeverity: 'moderate'
                };
            }

            const patientCount = outbreak.cases || outbreak.patient_count || 0;
            cityZones[city].totalCases += patientCount;
            cityZones[city].hospitals.push({ severity: outbreak.severity });

            let score = 1;
            if (outbreak.severity === 'severe') score = 3;
            else if (outbreak.severity === 'moderate') score = 2;

            if (score > cityZones[city].severityScore) {
                cityZones[city].severityScore = score;
                cityZones[city].maxSeverity = outbreak.severity;
            }
        });

        const aggregatedZones = Object.values(cityZones);

        if (activeLayer === 'heatmap') { // "Visual" Mode - Custom Markers
            aggregatedZones.forEach(zone => {
                const { lat, lng, totalCases, maxSeverity, city, hospitals } = zone;
                const severity = maxSeverity || 'moderate';
                const severityInfo = getSeverityColor(severity);

                // Original Colors as requested
                const severityColors = {
                    severe: { fill: '#fca5a5', stroke: '#ef4444', shadow: 'rgba(239, 68, 68, 0.4)' },
                    moderate: { fill: '#fde68a', stroke: '#f59e0b', shadow: 'rgba(245, 158, 11, 0.4)' },
                    mild: { fill: '#86efac', stroke: '#22c55e', shadow: 'rgba(34, 197, 94, 0.4)' }
                };
                const colors = severityColors[severity as keyof typeof severityColors] || severityColors.moderate;

                const el = document.createElement('div');
                el.className = 'outbreak-marker';
                el.innerHTML = `
                    <div class="relative w-10 h-10 flex items-center justify-center group">
                    <div class="absolute inset-0 rounded-full opacity-20" style="background-color: ${colors.stroke}"></div>
                    <svg width="40" height="40" viewBox="0 0 40 40" style="filter: drop-shadow(0 2px 4px ${colors.shadow});">
                        <circle cx="20" cy="20" r="14" fill="${colors.fill}" stroke="${colors.stroke}" stroke-width="3" opacity="1"/>
                        ${hospitals.length > 1 ? `<circle cx="30" cy="8" r="9" fill="white" stroke="${colors.stroke}" stroke-width="2"/><text x="30" y="12" text-anchor="middle" font-size="10" font-weight="900" fill="#1e293b">${hospitals.length}</text>` : ''}
                    </svg>
                    </div>
                `;
                el.style.cursor = 'pointer';

                const popupHTML = `
                    <div class="p-3 min-w-[200px]">
                    <div class="flex items-center gap-2 mb-2">
                        <div class="w-3 h-3 rounded-full" style="background-color: ${severityInfo.bg};"></div>
                        <h3 class="font-bold text-gray-900 text-base">${city}</h3>
                    </div>
                    <div class="space-y-1 text-sm text-gray-600">
                        <p><strong>Severity:</strong> <span style="color: ${severityInfo.border}">${severityInfo.text}</span></p>
                        <p><strong>Active Cases:</strong> ${totalCases}</p>
                        <p><strong>Locations:</strong> ${hospitals.length}</p>
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

        } else if (activeLayer === 'clusters') { // "Data Clusters" Mode
            const geojsonFeatures = aggregatedZones.map(zone => ({
                type: 'Feature',
                geometry: { type: 'Point', coordinates: [zone.lng, zone.lat] },
                properties: {
                    city: zone.city,
                    cases: zone.totalCases,
                    severity: zone.maxSeverity
                }
            }));

            map.current.addSource('outbreaks', {
                type: 'geojson',
                data: { type: 'FeatureCollection', features: geojsonFeatures } as any,
                cluster: true,
                clusterMaxZoom: 14,
                clusterRadius: 50
            });

            // Clusters Layer - Color by count
            map.current.addLayer({
                id: 'clusters',
                type: 'circle',
                source: 'outbreaks',
                filter: ['has', 'point_count'],
                paint: {
                    'circle-color': [
                        'step', ['get', 'point_count'],
                        '#93C5FD', 3,  // Blue for small clusters
                        '#FCD34D', 7,  // Yellow for medium
                        '#F87171'     // Red for large
                    ],
                    'circle-radius': [
                        'step', ['get', 'point_count'],
                        20, 10,
                        30, 30,
                        40
                    ],
                    'circle-opacity': 0.8,
                    'circle-stroke-width': 2,
                    'circle-stroke-color': '#fff'
                }
            });

            map.current.addLayer({
                id: 'cluster-count',
                type: 'symbol',
                source: 'outbreaks',
                filter: ['has', 'point_count'],
                layout: {
                    'text-field': '{point_count_abbreviated}',
                    'text-font': ['DIN Offc Pro Medium', 'Arial Unicode MS Bold'],
                    'text-size': 12
                }
            });

            // Unclustered Points Layer
            map.current.addLayer({
                id: 'unclustered-point',
                type: 'circle',
                source: 'outbreaks',
                filter: ['!', ['has', 'point_count']],
                paint: {
                    'circle-color': [
                        'match', ['get', 'severity'],
                        'severe', '#ef4444',
                        'moderate', '#f59e0b',
                        '#10b981' // mild/default
                    ],
                    'circle-radius': 10,
                    'circle-stroke-width': 2,
                    'circle-stroke-color': '#fff'
                }
            });
        }

    }, [outbreaks, mapLoaded, activeLayer]);

    return (
        <div className="relative w-full h-full">
            <div ref={mapContainer} className="w-full h-full rounded-lg overflow-hidden" />

            {/* Loading Overlay - Only internal UI remaining */}
            {!mapLoaded && (
                <div className="absolute inset-0 bg-slate-50 flex items-center justify-center z-50">
                    <div className="text-center">
                        <div className="inline-block w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mb-2"></div>
                    </div>
                </div>
            )}
        </div>
    );
};
