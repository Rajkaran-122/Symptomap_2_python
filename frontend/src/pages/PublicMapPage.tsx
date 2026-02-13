import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { PublicOutbreakMap } from '../components/PublicOutbreakMap';
import { ArrowLeft, Layers, Map as MapIcon, Navigation, Plus, Minus, ShieldAlert, Activity, Wifi } from 'lucide-react';
import axios from 'axios';
import maplibregl from 'maplibre-gl';

const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000/api/v1';

const PublicMapPage: React.FC = () => {
    const [activeLayer, setActiveLayer] = useState<'heatmap' | 'clusters'>('heatmap');
    const [outbreaks, setOutbreaks] = useState<any[]>([]);
    const mapRef = useRef<maplibregl.Map | null>(null);

    // Fetch outbreaks with polling
    const loadOutbreaks = async () => {
        try {
            const response = await axios.get(`${API_BASE_URL}/outbreaks/all`);
            const data = response.data?.outbreaks || [];
            setOutbreaks(data);
        } catch (error) {
            console.error('Failed to load public outbreaks:', error);
        }
    };

    useEffect(() => {
        loadOutbreaks();
        const interval = setInterval(loadOutbreaks, 60000);
        return () => clearInterval(interval);
    }, []);

    const severeCount = outbreaks.filter(o => o.severity === 'severe').length;
    const moderateCount = outbreaks.filter(o => o.severity === 'moderate').length;

    const handleZoomIn = () => mapRef.current?.zoomIn();
    const handleZoomOut = () => mapRef.current?.zoomOut();

    const handleLocation = () => {
        if ('geolocation' in navigator) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const { latitude, longitude } = position.coords;
                    if (mapRef.current) {
                        mapRef.current.flyTo({ center: [longitude, latitude], zoom: 10 });

                        // Add temporary marker
                        const userMarker = document.createElement('div');
                        userMarker.innerHTML = `
                          <svg width="30" height="30" viewBox="0 0 30 30">
                            <circle cx="15" cy="15" r="12" fill="#3b82f6" stroke="white" stroke-width="3"/>
                            <circle cx="15" cy="15" r="4" fill="white"/>
                          </svg>
                        `;
                        new maplibregl.Marker({ element: userMarker })
                            .setLngLat([longitude, latitude])
                            .addTo(mapRef.current);
                    }
                },
                (error) => {
                    console.error("Location error:", error);
                    alert('Location access denied.');
                }
            );
        }
    };

    return (
        <div className="min-h-screen bg-slate-50 flex flex-col p-3 overflow-hidden font-sans">

            {/* Top Bar: Brand & Mode */}
            <header className="flex justify-between items-center mb-3 px-1">
                <div className="flex items-center gap-3">
                    <Link to="/user/dashboard" className="w-10 h-10 bg-white rounded-xl flex items-center justify-center text-slate-400 hover:text-indigo-600 hover:shadow-md transition-all border border-slate-200">
                        <ArrowLeft className="w-5 h-5" />
                    </Link>
                    <div>
                        <h1 className="text-lg font-black text-slate-800 flex items-center gap-2">
                            SymptoMap <span className="px-1.5 py-0.5 bg-indigo-100 text-indigo-700 text-[9px] font-bold uppercase tracking-widest rounded-md">Public</span>
                        </h1>
                        <div className="flex items-center gap-2 text-[10px] font-medium text-slate-500">
                            <span className="relative flex h-1.5 w-1.5">
                                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                                <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-emerald-500"></span>
                            </span>
                            Live Surveillance Grid
                        </div>
                    </div>
                </div>

                <div className="flex bg-white p-1 rounded-xl border border-slate-200 shadow-sm">
                    {[
                        { id: 'heatmap', icon: MapIcon, label: 'Visual' },
                        { id: 'clusters', icon: Layers, label: 'Clusters' }
                    ].map((mode) => (
                        <button
                            key={mode.id}
                            onClick={() => setActiveLayer(mode.id as any)}
                            className={`flex items-center gap-1.5 px-4 py-1.5 rounded-lg text-[10px] font-bold transition-all
                                ${activeLayer === mode.id
                                    ? 'bg-slate-800 text-white shadow-md'
                                    : 'text-slate-400 hover:text-slate-900 hover:bg-slate-50'}`}
                        >
                            <mode.icon className="w-3 h-3" />
                            {mode.label}
                        </button>
                    ))}
                </div>
            </header>

            {/* Main Workspace */}
            <div className="flex-1 flex gap-4 min-h-0">

                {/* Left Panel: Legend & Stats */}
                <div className="w-56 flex flex-col gap-3">
                    {/* Active Outbreaks Card */}
                    <div className="bg-white rounded-3xl p-5 border border-slate-200 shadow-sm flex flex-col items-center text-center">
                        <div className="w-10 h-10 bg-indigo-50 rounded-xl flex items-center justify-center mb-2">
                            <Activity className="w-5 h-5 text-indigo-600" />
                        </div>
                        <h3 className="text-2xl font-black text-slate-800">{outbreaks.length}</h3>
                        <p className="text-[9px] text-slate-400 font-bold uppercase tracking-widest">Active Zones</p>
                    </div>

                    {/* Risk Legend */}
                    <div className="bg-white rounded-3xl p-5 border border-slate-200 shadow-sm flex-1">
                        <h4 className="flex items-center gap-2 font-black text-slate-800 text-xs mb-4">
                            <ShieldAlert className="w-3.5 h-3.5 text-slate-400" />
                            Risk Level
                        </h4>
                        <div className="space-y-3">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                    <div className="w-2.5 h-2.5 bg-red-500 rounded-full ring-2 ring-red-100" />
                                    <span className="text-xs font-bold text-slate-600">Severe</span>
                                </div>
                                <span className="text-xs font-black text-slate-800">{severeCount}</span>
                            </div>
                            <div className="w-full bg-slate-100 h-1 rounded-full overflow-hidden">
                                <div className="h-full bg-red-500" style={{ width: `${(severeCount / outbreaks.length) * 100}%` }} />
                            </div>

                            <div className="flex items-center justify-between mt-1">
                                <div className="flex items-center gap-2">
                                    <div className="w-2.5 h-2.5 bg-amber-400 rounded-full ring-2 ring-amber-100" />
                                    <span className="text-xs font-bold text-slate-600">Moderate</span>
                                </div>
                                <span className="text-xs font-black text-slate-800">{moderateCount}</span>
                            </div>
                            <div className="w-full bg-slate-100 h-1 rounded-full overflow-hidden">
                                <div className="h-full bg-amber-400" style={{ width: `${(moderateCount / outbreaks.length) * 100}%` }} />
                            </div>

                            <div className="pt-4 mt-2 border-t border-slate-100">
                                <p className="text-[9px] text-slate-400 leading-relaxed">
                                    Zones classified by patient density vectors.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Center: The Map Box */}
                <div className="flex-1 relative bg-white rounded-[2.5rem] border-[6px] border-white shadow-xl shadow-slate-200/50 overflow-hidden isolate ring-1 ring-slate-900/5">
                    <PublicOutbreakMap
                        outbreaks={outbreaks}
                        activeLayer={activeLayer}
                        onMapLoad={(map) => {
                            mapRef.current = map;
                        }}
                    />
                </div>

                {/* Right Panel: Controls */}
                <div className="w-16 flex flex-col gap-3">
                    <div className="bg-white rounded-[1.5rem] p-1.5 border border-slate-200 shadow-sm flex flex-col items-center gap-1.5">
                        <button onClick={handleZoomIn} className="w-10 h-10 hover:bg-slate-50 rounded-xl flex items-center justify-center text-slate-600 font-bold transition-colors">
                            <Plus className="w-4 h-4" />
                        </button>
                        <div className="w-6 h-px bg-slate-100" />
                        <button onClick={handleZoomOut} className="w-10 h-10 hover:bg-slate-50 rounded-xl flex items-center justify-center text-slate-600 font-bold transition-colors">
                            <Minus className="w-4 h-4" />
                        </button>
                    </div>

                    <button onClick={handleLocation} className="w-14 h-14 bg-blue-600 hover:bg-blue-700 text-white rounded-[1.5rem] flex items-center justify-center shadow-lg shadow-blue-200 transition-all hover:scale-105 active:scale-95 group" title="My Location">
                        <Navigation className="w-5 h-5 fill-current group-hover:rotate-45 transition-transform" />
                    </button>

                    <div className="mt-auto flex flex-col gap-2">
                        <div className="w-14 h-20 bg-white rounded-[1.5rem] border border-slate-200 shadow-sm flex flex-col items-center justify-center gap-2 p-1" title="System Status">
                            <div className="relative">
                                <div className="w-2.5 h-2.5 bg-emerald-500 rounded-full animate-ping absolute inset-0 opacity-75" />
                                <div className="w-2.5 h-2.5 bg-emerald-500 rounded-full relative border-2 border-white" />
                            </div>
                            <span className="text-[8px] font-bold text-slate-400 rotate-180" style={{ writingMode: 'vertical-rl' }}>ONLINE</span>
                        </div>
                    </div>
                </div>

            </div>

            {/* Footer */}
            <footer className="mt-3 flex justify-between items-center text-[9px] font-bold text-slate-400 uppercase tracking-widest px-2">
                <div className="flex items-center gap-3">
                    <span>v2.4.0</span>
                    <span className="w-1 h-1 bg-slate-300 rounded-full" />
                    <span>© OpenStreetMap</span>
                </div>
                <div className="flex items-center gap-1.5">
                    <Wifi className="w-2.5 h-2.5 text-emerald-500" />
                    Operational
                </div>
            </footer>
        </div>
    );
};

export default PublicMapPage;
