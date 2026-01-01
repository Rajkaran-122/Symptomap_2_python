import { useState } from 'react';
import Chatbot from '@/components/Chatbot';

const ChatbotPage = () => {
    const [activeTab, setActiveTab] = useState<'radar' | 'doctor'>('radar');

    return (
        <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-teal-50 flex flex-col items-center py-6">
            <div className="w-full max-w-4xl bg-white rounded-xl shadow-2xl overflow-hidden min-h-[80vh] flex flex-col">
                {/* Visual Header */}
                <div className="bg-slate-900 text-white p-6 text-center">
                    <h1 className="text-3xl font-bold mb-2">SymptoMap Intelligence</h1>
                    <p className="text-slate-400">Advanced Viral Detection & AI Diagnostics</p>
                </div>

                {/* Navigation Tabs */}
                <div className="flex border-b border-gray-200">
                    <button
                        onClick={() => setActiveTab('radar')}
                        className={`flex-1 py-4 text-center font-bold text-lg transition-colors flex items-center justify-center gap-2
                            ${activeTab === 'radar'
                                ? 'bg-white text-emerald-600 border-b-4 border-emerald-500'
                                : 'bg-gray-50 text-gray-500 hover:bg-gray-100'}`}
                    >
                        <span>📡</span> Viral Radar
                    </button>
                    <button
                        onClick={() => setActiveTab('doctor')}
                        className={`flex-1 py-4 text-center font-bold text-lg transition-colors flex items-center justify-center gap-2
                            ${activeTab === 'doctor'
                                ? 'bg-white text-blue-600 border-b-4 border-blue-500'
                                : 'bg-gray-50 text-gray-500 hover:bg-gray-100'}`}
                    >
                        <span>🩺</span> Dr. AI (Pro)
                    </button>
                </div>

                {/* Content Area */}
                <div className="flex-1 p-6 bg-white overflow-hidden flex flex-col">
                    {activeTab === 'radar' ? (
                        <div className="flex-1 flex flex-col items-center justify-center space-y-8 animate-fadeIn">
                            <div className="text-center space-y-4 max-w-lg">
                                <div className="w-24 h-24 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-4 animate-pulse">
                                    <span className="text-4xl">📡</span>
                                </div>
                                <h2 className="text-2xl font-bold text-slate-800">Viral Shield Activated</h2>
                                <p className="text-slate-600">
                                    Scanning local hospital data for active viral threats in your area...
                                </p>
                            </div>

                            <div className="w-full max-w-md bg-amber-50 border border-amber-200 rounded-xl p-6 shadow-sm">
                                <div className="flex items-start gap-4">
                                    <div className="text-2xl">⚠️</div>
                                    <div>
                                        <h3 className="font-bold text-amber-800">Viral Alert: Mumbai</h3>
                                        <p className="text-sm text-amber-700 mt-1">
                                            Local doctors report elevated cases of <strong>Viral Fever</strong>.
                                        </p>
                                        <div className="mt-4 space-y-2">
                                            <div className="text-xs font-bold uppercase tracking-wider text-amber-900">Recommended Precautions</div>
                                            <ul className="text-sm text-amber-800 space-y-1 list-disc pl-4">
                                                <li>Wear a mask in crowded areas</li>
                                                <li>Stay hydrated (3L+ water/day)</li>
                                                <li>Monitor body temperature</li>
                                                <li>Avoid street food</li>
                                            </ul>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="text-center">
                                <button
                                    onClick={() => setActiveTab('doctor')}
                                    className="text-blue-600 hover:underline font-medium"
                                >
                                    Feeling symptoms? Consult Dr. AI &rarr;
                                </button>
                            </div>
                        </div>
                    ) : (
                        <div className="flex-1 bg-white rounded-xl shadow-xl overflow-hidden h-[600px]">
                            {/* Pass mode prop to Chatbot if we want to change behavior */}
                            <Chatbot />
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default ChatbotPage;
