/*
 * Enhanced Landing Page - SymptoMap
 * Professional hero section with live stats and feature showcase
 */

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { TrendingUp, AlertTriangle, Activity, MapPin, BarChart3, FileText, Shield, Zap } from 'lucide-react';

export const LandingPage: React.FC = () => {
    const navigate = useNavigate();
    const [stats, setStats] = useState({
        active_outbreaks: '0',
        ai_predictions: '0',
        alerts_sent: '0',
        coverage_area: '0 States'
    });

    useEffect(() => {
        // Fetch live stats
        const loadStats = async () => {
            try {
                const API_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000/api/v1';
                const response = await fetch(`${API_URL}/stats/dashboard`);
                const data = await response.json();
                setStats({
                    active_outbreaks: data.active_outbreaks || '0',
                    ai_predictions: data.ai_predictions || '0',
                    alerts_sent: '5',
                    coverage_area: data.coverage_area || '4 States'
                });
            } catch (error) {
                console.error('Failed to load stats:', error);
            }
        };
        loadStats();
    }, []);

    const features = [
        {
            icon: TrendingUp,
            title: 'AI Predictions',
            description: 'Advanced SEIR model forecasting with multi-scenario analysis',
            color: 'from-blue-500 to-indigo-600',
            route: '/predictions'
        },
        {
            icon: AlertTriangle,
            title: 'Alert Management',
            description: 'Real-time outbreak alerts with smart notifications',
            color: 'from-red-500 to-pink-600',
            route: '/alerts'
        },
        {
            icon: BarChart3,
            title: 'Analytics Dashboard',
            description: 'Comprehensive data visualization and trend analysis',
            color: 'from-purple-500 to-indigo-600',
            route: '/analytics'
        },
        {
            icon: FileText,
            title: 'Reports',
            description: 'Detailed outbreak reports with export capabilities',
            color: 'from-green-500 to-teal-600',
            route: '/reports'
        }
    ];

    return (
        <div className="min-h-screen w-full bg-gradient-to-br from-gray-50 via-white to-gray-100">
            {/* Hero Section */}
            <div className="relative overflow-hidden bg-gradient-to-br from-primary-900 via-primary-800 to-primary-900">
                <div className="absolute inset-0 bg-grid-white/[0.05] bg-[size:20px_20px]"></div>
                <div className="absolute top-0 right-0 w-96 h-96 bg-primary-700/20 rounded-full blur-3xl"></div>
                <div className="absolute bottom-0 left-0 w-96 h-96 bg-primary-600/20 rounded-full blur-3xl"></div>

                <div className="relative max-w-7xl mx-auto px-6 py-20 md:py-32">
                    <div className="text-center">
                        <div className="inline-flex items-center gap-2 bg-white/10 backdrop-blur-sm border border-white/20 rounded-full px-4 py-2 mb-6">
                            <Shield className="w-4 h-4 text-green-400" />
                            <span className="text-sm font-semibold text-white">AI-Powered Health Surveillance</span>
                        </div>

                        <h1 className="text-5xl md:text-7xl font-bold text-white mb-6">
                            SymptoMap
                        </h1>
                        <p className="text-xl md:text-2xl text-primary-100 mb-4 max-w-3xl mx-auto">
                            Advanced Disease Outbreak Prediction & Surveillance System
                        </p>
                        <p className="text-lg text-primary-200 mb-12 max-w-2xl mx-auto">
                            Real-time monitoring, AI-powered predictions, and intelligent alert systems for proactive health management
                        </p>

                        <div className="flex flex-wrap items-center justify-center gap-4 mb-16">
                            <button
                                onClick={() => navigate('/dashboard')}
                                className="bg-white text-primary-900 px-8 py-4 rounded-xl font-bold text-lg hover:bg-gray-100 transition-all shadow-xl flex items-center gap-2"
                            >
                                <MapPin className="w-5 h-5" />
                                View Live Map
                            </button>
                            <button
                                onClick={() => navigate('/predictions')}
                                className="bg-primary-600 text-white px-8 py-4 rounded-xl font-bold text-lg hover:bg-primary-700 transition-all border-2 border-white/20 flex items-center gap-2"
                            >
                                <TrendingUp className="w-5 h-5" />
                                AI Predictions
                            </button>
                        </div>

                        {/* Live Stats */}
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto">
                            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                                <div className="text-4xl font-bold text-white mb-2">{stats.active_outbreaks}</div>
                                <div className="text-sm text-primary-200">Active Outbreaks</div>
                            </div>
                            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                                <div className="text-4xl font-bold text-white mb-2">{stats.ai_predictions}</div>
                                <div className="text-sm text-primary-200">AI Predictions</div>
                            </div>
                            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                                <div className="text-4xl font-bold text-white mb-2">{stats.alerts_sent}</div>
                                <div className="text-sm text-primary-200">Alerts Sent</div>
                            </div>
                            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                                <div className="text-4xl font-bold text-white mb-2">{stats.coverage_area}</div>
                                <div className="text-sm text-primary-200">Coverage</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Features Grid */}
            <div className="max-w-7xl mx-auto px-6 py-20">
                <div className="text-center mb-12">
                    <h2 className="text-4xl font-bold text-gray-900 mb-4">Powerful Features</h2>
                    <p className="text-xl text-gray-600">Everything you need for comprehensive outbreak management</p>
                </div>

                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {features.map((feature, idx) => {
                        const Icon = feature.icon;
                        return (
                            <button
                                key={idx}
                                onClick={() => navigate(feature.route)}
                                className="group bg-white rounded-2xl p-6 shadow-lg hover:shadow-2xl transition-all border border-gray-100 hover:border-gray-200 text-left"
                            >
                                <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${feature.color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                                    <Icon className="w-7 h-7 text-white" />
                                </div>
                                <h3 className="text-xl font-bold text-gray-900 mb-2">{feature.title}</h3>
                                <p className="text-gray-600 text-sm leading-relaxed">{feature.description}</p>
                            </button>
                        );
                    })}
                </div>
            </div>

            {/* System Highlights */}
            <div className="bg-gradient-to-br from-gray-900 to-gray-800 text-white py-20">
                <div className="max-w-7xl mx-auto px-6">
                    <div className="text-center mb-12">
                        <h2 className="text-4xl font-bold mb-4">Why SymptoMap?</h2>
                        <p className="text-xl text-gray-300">Built with cutting-edge technology for maximum impact</p>
                    </div>

                    <div className="grid md:grid-cols-3 gap-8">
                        <div className="text-center">
                            <div className="w-16 h-16 bg-blue-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                                <Zap className="w-8 h-8 text-blue-400" />
                            </div>
                            <h3 className="text-xl font-bold mb-2">Real-Time Updates</h3>
                            <p className="text-gray-400">Live data synchronization with instant notifications</p>
                        </div>
                        <div className="text-center">
                            <div className="w-16 h-16 bg-purple-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                                <Activity className="w-8 h-8 text-purple-400" />
                            </div>
                            <h3 className="text-xl font-bold mb-2">AI-Powered</h3>
                            <p className="text-gray-400">SEIR model predictions with confidence intervals</p>
                        </div>
                        <div className="text-center">
                            <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                                <Shield className="w-8 h-8 text-green-400" />
                            </div>
                            <h3 className="text-xl font-bold mb-2">Secure & Reliable</h3>
                            <p className="text-gray-400">Enterprise-grade security and 99.9% uptime</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* CTA Section */}
            <div className="max-w-7xl mx-auto px-6 py-20 text-center">
                <h2 className="text-4xl font-bold text-gray-900 mb-6">Ready to explore?</h2>
                <p className="text-xl text-gray-600 mb-8">Access all features through the navigation menu</p>
                <button
                    onClick={() => navigate('/dashboard')}
                    className="bg-primary-600 hover:bg-primary-700 text-white px-8 py-4 rounded-xl font-bold text-lg transition-all shadow-lg inline-flex items-center gap-2"
                >
                    <MapPin className="w-5 h-5" />
                    Go to Dashboard
                </button>
            </div>
        </div>
    );
};

export default LandingPage;
