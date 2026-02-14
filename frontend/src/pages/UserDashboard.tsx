/**
 * User Dashboard - Professional Light Theme ("Genius Mode")
 * High-fidelity health surveillance portal for general public
 */

import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
    Activity, Bell, MapPin, AlertTriangle,
    ShieldCheck, LogOut, RefreshCw, Radio,
    Stethoscope, Users, Zap,
    ChevronRight, Search, Thermometer,
    MessageSquare
} from 'lucide-react';
import BroadcastFeed from '../components/broadcasts/BroadcastFeed';
import { API_BASE_URL } from '../config/api';
import Chatbot from '../components/Chatbot';
import { publicService } from '../services/public';
import { NotificationCenter } from '../components/user/NotificationCenter';

interface User {
    id: string;
    phone: string;
    email: string | null;
    role: string;
    region: string;
    full_name: string | null;
}

interface HealthStats {
    activeOutbreaks: number;
    activeBroadcasts: number;
    casesThisWeek: number;
    trendPercentage: number;
    regionsAffected: number;
    verifiedSources?: number;
}

interface Outbreak {
    id: string;
    disease_type: string;
    location: string;
    patient_count: number;
    status: string;
    severity: string;
    reported_at: string;
    city?: string;
    date_reported?: string;
}

const UserDashboard: React.FC = () => {
    const navigate = useNavigate();

    // User State
    const [user] = useState<User>(() => {
        const storedUser = localStorage.getItem('symptomap_user');
        if (storedUser) return JSON.parse(storedUser);
        return null; // No guest user, force login
    });

    useEffect(() => {
        if (!user) {
            navigate('/user/login');
        }
    }, [user, navigate]);

    // Prevent rendering if user is null (redirecting)
    if (!user) return null;

    // Dashboard State
    const [isNotificationsOpen, setIsNotificationsOpen] = useState(false);
    const [stats, setStats] = useState<HealthStats>({
        activeOutbreaks: 0,
        activeBroadcasts: 0,
        casesThisWeek: 0,
        trendPercentage: 0,
        regionsAffected: 0,
        verifiedSources: 0
    });
    const [gridStats, setGridStats] = useState({ visual_clusters: 0, active_zones: 0, risk_severe: 0, risk_moderate: 0 });
    const [hotspots, setHotspots] = useState<any[]>([]);
    const [recentOutbreaks, setRecentOutbreaks] = useState<Outbreak[]>([]);
    const [loading, setLoading] = useState(true);
    const [isChatOpen, setIsChatOpen] = useState(false);
    const [currentTime, setCurrentTime] = useState(new Date());

    useEffect(() => {
        loadDashboardData();
        const timer = setInterval(() => setCurrentTime(new Date()), 60000);
        return () => clearInterval(timer);
    }, []);

    const loadDashboardData = async () => {
        setLoading(true);
        try {
            const [statsData, hotspotsData, outbreaksData] = await Promise.all([
                publicService.getStats(),
                publicService.getHotspots(),
                fetch(`${API_BASE_URL}/outbreaks/all`).then(res => res.json())
            ]);

            setStats(statsData);
            setHotspots(hotspotsData);

            // Grid Stats
            try {
                const gridData = await publicService.getGridStats();
                setGridStats(gridData);
            } catch (e) {
                console.error("Grid stats error", e);
            }

            if (outbreaksData && outbreaksData.outbreaks) {
                setRecentOutbreaks(outbreaksData.outbreaks.slice(0, 5)); // Top 5 recent
            }
        } catch (err) {
            console.error('Failed to load dashboard data:', err);
        } finally {
            setLoading(false);
        }
    };

    // Weather & Location Logic
    const [weather, setWeather] = useState({
        temp: 28,
        city: 'Mumbai, India',
        aqi: 42,
        aqiLabel: 'Good'
    });

    useEffect(() => {
        fetchWeather();
    }, []);

    const fetchWeather = async () => {
        if (!navigator.geolocation) return;

        navigator.geolocation.getCurrentPosition(async (position) => {
            const { latitude, longitude } = position.coords;
            try {
                // 1. Get Weather
                const weatherRes = await fetch(
                    `https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&current=temperature_2m`
                );
                const weatherData = await weatherRes.json();

                // 2. Get AQI
                const aqiRes = await fetch(
                    `https://air-quality-api.open-meteo.com/v1/air-quality?latitude=${latitude}&longitude=${longitude}&current=european_aqi`
                );
                const aqiData = await aqiRes.json();

                // 3. Get Location Name (Reverse Geocode)
                const locRes = await fetch(
                    `https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=${latitude}&longitude=${longitude}&localityLanguage=en`
                );
                const locData = await locRes.json();

                // Update State
                setWeather({
                    temp: Math.round(weatherData.current.temperature_2m),
                    city: `${locData.city || locData.locality}, ${locData.countryCode}`,
                    aqi: aqiData.current.european_aqi,
                    aqiLabel: getAqiLabel(aqiData.current.european_aqi)
                });
            } catch (e) {
                console.error("Weather fetch failed", e);
            }
        }, (err) => {
            console.warn("Location denied, using default", err);
        });
    };

    const getAqiLabel = (aqi: number) => {
        if (aqi < 20) return 'Excellent';
        if (aqi < 40) return 'Good';
        if (aqi < 60) return 'Moderate';
        if (aqi < 80) return 'Poor';
        return 'Critical';
    };

    const handleLogout = () => {
        localStorage.clear();
        navigate('/user/login');
    };

    const getSeverityColor = (severity: string) => {
        switch (severity?.toLowerCase()) {
            case 'severe': return 'text-rose-600 bg-rose-50 border-rose-100';
            case 'moderate': return 'text-amber-600 bg-amber-50 border-amber-100';
            default: return 'text-emerald-600 bg-emerald-50 border-emerald-100';
        }
    };

    const formatDate = (dateStr: string) => {
        if (!dateStr) return 'Recently';
        return new Date(dateStr).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' });
    };

    return (
        <div className="min-h-screen bg-slate-50 font-sans selection:bg-indigo-100 selection:text-indigo-900">
            {/* ═══════════════════════════════════════════
                 HEADER
            ═══════════════════════════════════════════ */}
            <header className="bg-white/80 backdrop-blur-md border-b border-slate-200 sticky top-0 z-40">
                <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
                    <div className="flex items-center gap-8">
                        <Link to="/" className="flex items-center gap-2.5 group">
                            <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center shadow-lg shadow-indigo-500/20 transition-transform group-hover:scale-105">
                                <Activity className="w-5 h-5 text-white" />
                            </div>
                            <span className="font-bold text-slate-900 text-lg tracking-tight">SymptoMap</span>
                        </Link>

                        <nav className="hidden md:flex items-center gap-1">
                            <Link to="/user/map" className="px-4 py-2 text-sm font-medium text-slate-600 hover:text-indigo-600 hover:bg-slate-50 rounded-full transition-all">Live Map</Link>
                            <Link to="/user/chatbot" className="px-4 py-2 text-sm font-medium text-slate-600 hover:text-indigo-600 hover:bg-slate-50 rounded-full transition-all">Dr. AI</Link>
                        </nav>
                    </div>

                    <div className="flex items-center gap-4">
                        <div className="hidden sm:flex items-center bg-slate-100/50 border border-slate-200 rounded-full px-4 py-1.5 focus-within:bg-white focus-within:ring-2 focus-within:ring-indigo-500/10 transition-all">
                            <Search className="w-4 h-4 text-slate-400 mr-2" />
                            <input
                                type="text"
                                placeholder="Search zones..."
                                className="bg-transparent border-none text-sm w-48 focus:ring-0 placeholder:text-slate-400 text-slate-700"
                            />
                        </div>

                        <div className="h-8 w-px bg-slate-200 mx-2 hidden sm:block" />

                        <div className="flex items-center gap-3">
                            <button
                                onClick={loadDashboardData}
                                className="p-2 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-full transition-all"
                                title="Refresh Data"
                            >
                                <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
                            </button>

                            <button
                                onClick={() => setIsNotificationsOpen(true)}
                                className="p-2 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-full transition-all relative"
                            >
                                <Bell className="w-5 h-5" />
                                {stats.activeBroadcasts > 0 && (
                                    <span className="absolute top-2 right-2 w-2 h-2 bg-rose-500 rounded-full ring-2 ring-white" />
                                )}
                            </button>

                            <div className="relative group">
                                <button className="w-9 h-9 bg-slate-100 rounded-full flex items-center justify-center text-slate-700 font-bold border border-slate-200 hover:bg-indigo-50 hover:border-indigo-200 hover:text-indigo-600 transition-all">
                                    {(user.full_name || 'G')[0]}
                                </button>
                                {/* Dropdown Menu */}
                                <div className="absolute right-0 mt-2 w-48 bg-white rounded-xl shadow-xl border border-slate-100 py-1 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all transform origin-top-right">
                                    <div className="px-4 py-2 border-b border-slate-50">
                                        <p className="text-sm font-bold text-slate-800 truncate">{user.full_name}</p>
                                        <p className="text-xs text-slate-400 truncate">{user.email}</p>
                                    </div>
                                    <button onClick={handleLogout} className="w-full text-left px-4 py-2 text-sm text-rose-600 hover:bg-rose-50 flex items-center gap-2">
                                        <LogOut className="w-4 h-4" /> Sign Out
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </header>

            {/* ═══════════════════════════════════════════
                 MAIN CONTENT
            ═══════════════════════════════════════════ */}
            <main className="max-w-7xl mx-auto px-6 py-8">

                {/* HERO SECTION */}
                <section className="mb-10">
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        {/* Welcome Card */}
                        <div className="lg:col-span-2 bg-white rounded-[2rem] p-8 border border-slate-100 shadow-sm relative overflow-hidden group">
                            <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-50 rounded-full blur-3xl -mr-16 -mt-16 opacity-50 group-hover:opacity-75 transition-opacity" />

                            <div className="relative z-10">
                                <div className="flex items-center gap-3 mb-4">
                                    <span className="px-3 py-1 rounded-full bg-emerald-50 text-emerald-600 text-xs font-bold uppercase tracking-wider border border-emerald-100 flex items-center gap-1.5">
                                        <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                                        System Operational
                                    </span>
                                    <span className="text-slate-400 text-sm font-medium">
                                        {currentTime.toLocaleDateString('en-IN', { weekday: 'long', month: 'long', day: 'numeric' })}
                                    </span>
                                </div>
                                <h1 className="text-3xl md:text-4xl font-bold text-slate-900 mb-2">
                                    Good {currentTime.getHours() < 12 ? 'Morning' : currentTime.getHours() < 18 ? 'Afternoon' : 'Evening'}, {user.full_name?.split(' ')[0]}.
                                </h1>
                                <p className="text-slate-500 text-lg mb-8 max-w-lg">
                                    Monitoring <strong className="text-indigo-600">{stats.activeOutbreaks} active zones</strong> in your region. Your local risk index is currently <strong className="text-emerald-600">Low</strong>.
                                </p>

                                <div className="flex flex-wrap gap-4">
                                    <Link
                                        to="/user/chatbot"
                                        className="px-6 py-3 bg-indigo-600 text-white rounded-xl font-bold hover:bg-indigo-700 hover:shadow-lg hover:shadow-indigo-200 transition-all flex items-center gap-2.5 active:scale-95"
                                    >
                                        <MessageSquare className="w-5 h-5" />
                                        Consult Dr. AI
                                    </Link>
                                    <Link
                                        to="/user/map"
                                        className="px-6 py-3 bg-white border border-slate-200 text-slate-700 rounded-xl font-bold hover:border-indigo-200 hover:text-indigo-600 hover:shadow-md transition-all flex items-center gap-2.5 active:scale-95"
                                    >
                                        <MapPin className="w-5 h-5" />
                                        View Live Map
                                    </Link>
                                </div>
                            </div>
                        </div>

                        {/* Quick Stats / Weather */}
                        <div className="bg-slate-900 rounded-[2rem] p-8 text-white relative overflow-hidden flex flex-col justify-between">
                            <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 mix-blend-soft-light" />
                            <div className="absolute -bottom-12 -right-12 w-48 h-48 bg-indigo-500 rounded-full blur-3xl opacity-30" />

                            <div className="relative z-10">
                                <div className="flex items-center justify-between mb-8">
                                    <div className="p-3 bg-white/10 backdrop-blur-md rounded-xl">
                                        <Thermometer className="w-6 h-6 text-white" />
                                    </div>
                                    <span className="text-slate-400 text-xs font-bold uppercase tracking-wider">Local Vitals</span>
                                </div>
                                <div>
                                    <div className="text-4xl font-bold mb-1">{weather.temp}°C</div>
                                    <div className="text-indigo-200 font-medium text-sm">{weather.city}</div>
                                </div>
                            </div>

                            <div className="relative z-10 mt-6 pt-6 border-t border-white/10">
                                <div className="flex justify-between items-end">
                                    <div>
                                        <p className="text-xs text-slate-400 uppercase tracking-wider font-bold mb-1">Air Quality</p>
                                        <p className={`text-lg font-bold ${weather.aqi < 40 ? 'text-emerald-400' : weather.aqi < 60 ? 'text-amber-400' : 'text-rose-400'}`}>
                                            {weather.aqiLabel} ({weather.aqi})
                                        </p>
                                    </div>
                                    <Activity className="w-12 h-6 text-slate-500" />
                                </div>
                            </div>
                        </div>
                    </div>
                </section>

                {/* STATS GRID */}
                <section className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-10">
                    {[
                        { label: 'Verified Cases', value: stats.casesThisWeek, icon: Users, color: 'blue' },
                        { label: 'Active Zones', value: stats.activeOutbreaks, icon: Radio, color: 'indigo' },
                        { label: 'Risk Alerts', value: stats.activeBroadcasts, icon: AlertTriangle, color: 'amber' },
                        { label: 'Trusted Hospitals', value: stats.verifiedSources || 12, icon: ShieldCheck, color: 'emerald' },
                    ].map((stat, i) => (
                        <div key={i} className="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm hover:border-slate-300 transition-all group">
                            <div className="flex justify-between items-start mb-3">
                                <div className={`p-2 rounded-lg bg-${stat.color}-50 text-${stat.color}-600 group-hover:bg-${stat.color}-100 transition-colors`}>
                                    <stat.icon className="w-5 h-5" />
                                </div>
                                {i === 1 && <span className="flex h-2 w-2 rounded-full bg-indigo-500 animate-ping" />}
                            </div>
                            <h3 className="text-2xl font-bold text-slate-800 mb-0.5">{loading ? '...' : stat.value}</h3>
                            <p className="text-xs text-slate-500 font-medium">{stat.label}</p>
                        </div>
                    ))}
                </section>

                {/* CONTENT GRID */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

                    {/* LEFT COLUMN: Feed & Outbreaks */}
                    <div className="lg:col-span-2 space-y-8">
                        <div>
                            <div className="flex items-center justify-between mb-6">
                                <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
                                    <Zap className="w-5 h-5 text-amber-500 fill-current" />
                                    Live Updates
                                </h2>
                                <button className="text-sm text-indigo-600 font-bold hover:underline">View All</button>
                            </div>

                            <div className="bg-white rounded-[1.5rem] border border-slate-100 shadow-sm overflow-hidden">
                                {loading ? (
                                    <div className="p-8 text-center text-slate-400">Loading feeds...</div>
                                ) : recentOutbreaks.length === 0 ? (
                                    <div className="p-12 text-center">
                                        <div className="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mx-auto mb-4">
                                            <ShieldCheck className="w-8 h-8 text-slate-300" />
                                        </div>
                                        <p className="text-slate-900 font-bold">No active threats reported</p>
                                        <p className="text-slate-500 text-sm">Your area is currently safe.</p>
                                    </div>
                                ) : (
                                    <div className="divide-y divide-slate-50">
                                        {recentOutbreaks.map((outbreak) => (
                                            <div key={outbreak.id} className="p-5 hover:bg-slate-50 transition-colors flex items-center gap-4 group">
                                                <div className={`w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 ${getSeverityColor(outbreak.severity)}`}>
                                                    <Activity className="w-6 h-6" />
                                                </div>
                                                <div className="flex-1 min-w-0">
                                                    <div className="flex justify-between items-start">
                                                        <h4 className="font-bold text-slate-800 truncate group-hover:text-indigo-700 transition-colors pr-4">{outbreak.disease_type}</h4>
                                                        <span className="text-xs text-slate-400 whitespace-nowrap">{formatDate(outbreak.date_reported || outbreak.reported_at)}</span>
                                                    </div>
                                                    <div className="flex items-center gap-2 mt-1">
                                                        <MapPin className="w-3.5 h-3.5 text-slate-400" />
                                                        <span className="text-sm text-slate-500 truncate">{outbreak.city || outbreak.location}</span>
                                                    </div>
                                                </div>
                                                <div className="text-right">
                                                    <div className="font-bold text-slate-900">{outbreak.patient_count}</div>
                                                    <div className="text-[10px] text-slate-400 uppercase font-bold">Cases</div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Broadcasts Section */}
                        <div>
                            <h2 className="text-xl font-bold text-slate-900 mb-6 flex items-center gap-2">
                                <Radio className="w-5 h-5 text-indigo-500" />
                                Health Broadcasts
                            </h2>
                            <BroadcastFeed region={user.region === 'Universal' ? undefined : user.region} />
                        </div>
                    </div>

                    {/* RIGHT COLUMN: Sidebar Widgets */}
                    <div className="space-y-6">

                        {/* Map Widget - Live Surveillance Grid */}
                        <div className="bg-white p-1 rounded-[2rem] border border-slate-100 shadow-sm">
                            <div className="bg-slate-100 rounded-[1.7rem] relative overflow-hidden group min-h-[16rem]">
                                {/* Simulated Map visual backdrop */}
                                <div className="absolute inset-0 bg-[url('https://api.mapbox.com/styles/v1/mapbox/light-v10/static/72.8777,19.0760,10,0/600x400?access_token=YOUR_TOKEN')] bg-cover bg-center grayscale opacity-60 group-hover:grayscale-0 group-hover:opacity-100 transition-all duration-700" />
                                <div className="absolute inset-0 bg-gradient-to-t from-slate-900/90 via-slate-900/40 to-transparent flex flex-col justify-end p-6">

                                    <div className="mb-4">
                                        <div className="flex items-center justify-between text-white/90 mb-2">
                                            <span className="text-xs font-bold uppercase tracking-wider">Visual Clusters</span>
                                            <span className="text-xl font-bold">{gridStats.visual_clusters}</span>
                                        </div>
                                        <div className="w-full bg-white/20 h-1 rounded-full overflow-hidden">
                                            <div className="bg-indigo-500 h-full w-[80%] animate-pulse" />
                                        </div>
                                    </div>

                                    <div className="grid grid-cols-2 gap-4 mb-4">
                                        <div>
                                            <p className="text-xs text-slate-400 font-bold uppercase">Severe</p>
                                            <p className="text-lg font-bold text-rose-400">{gridStats.risk_severe}</p>
                                        </div>
                                        <div>
                                            <p className="text-xs text-slate-400 font-bold uppercase">Moderate</p>
                                            <p className="text-lg font-bold text-amber-400">{gridStats.risk_moderate}</p>
                                        </div>
                                    </div>

                                    <div className="w-full">
                                        <div className="flex justify-between items-end">
                                            <div>
                                                <p className="text-white font-bold text-lg">Live Grid</p>
                                                <p className="text-slate-300 text-[10px] leading-tight">Zones classified by patient density vectors.</p>
                                            </div>
                                            <Link to="/user/map" className="bg-white text-indigo-600 p-3 rounded-full hover:scale-110 transition-transform shadow-lg">
                                                <ChevronRight className="w-5 h-5" />
                                            </Link>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Hotspots */}
                        <div className="bg-white rounded-[2rem] border border-slate-100 shadow-sm p-6">
                            <h3 className="font-bold text-slate-900 mb-4">Risk Hotspots</h3>
                            <div className="space-y-3">
                                {hotspots.slice(0, 4).map((h, i) => (
                                    <div key={i} className="flex items-center justify-between py-2 border-b border-slate-50 last:border-0">
                                        <div className="flex items-center gap-3">
                                            <span className="text-sm font-bold text-slate-700">{h.city}</span>
                                        </div>
                                        <span className={`text-xs font-bold px-2 py-1 rounded-full ${h.risk === 'Critical' ? 'bg-rose-50 text-rose-600' : 'bg-orange-50 text-orange-600'}`}>
                                            {h.risk}
                                        </span>
                                    </div>
                                ))}
                                {hotspots.length === 0 && <p className="text-sm text-slate-400 italic">No high-risk zones currently.</p>}
                            </div>
                        </div>

                        {/* AI Promo */}
                        <div className="bg-indigo-600 rounded-[2rem] p-6 text-white text-center relative overflow-hidden">
                            <div className="absolute -top-10 -left-10 w-40 h-40 bg-indigo-500 rounded-full blur-3xl opacity-50" />
                            <div className="relative z-10">
                                <div className="w-12 h-12 bg-white/20 backdrop-blur-md rounded-xl flex items-center justify-center mx-auto mb-4">
                                    <Stethoscope className="w-6 h-6 text-white" />
                                </div>
                                <h3 className="font-bold text-lg mb-2">Feeling Unwell?</h3>
                                <p className="text-indigo-100 text-xs mb-6 leading-relaxed">
                                    Our AI Doctor is trained on millions of case files to provide instant guidance.
                                </p>
                                <Link to="/user/chatbot" className="block w-full py-3 bg-white text-indigo-600 rounded-xl font-bold text-xs uppercase tracking-widest shadow-lg hover:bg-indigo-50 transition-colors">
                                    Start Chat
                                </Link>
                            </div>
                        </div>
                    </div>
                </div>
            </main>

            {/* NOTIFICATIONS & CHATBOT */}
            <NotificationCenter
                isOpen={isNotificationsOpen}
                onClose={() => setIsNotificationsOpen(false)}
            />

            <Chatbot
                isOpen={isChatOpen}
                onClose={() => setIsChatOpen(false)}
                userName={user.full_name?.split(' ')[0]}
                initialLocation={{
                    city: user.region === 'Universal' ? '' : user.region,
                    country: 'India'
                }}
            />
        </div>
    );
};

export default UserDashboard;
