import React, { useState } from 'react';
import { X, Bell, Mail, Smartphone, MapPin, Save } from 'lucide-react';

interface UserPreferencesModalProps {
    isOpen: boolean;
    onClose: () => void;
}

export const UserPreferencesModal: React.FC<UserPreferencesModalProps> = ({ isOpen, onClose }) => {
    const [prefs, setPrefs] = useState({
        email: true,
        sms: false,
        inApp: true,
        region: 'Maharashtra',
        pushNotifications: true
    });

    if (!isOpen) return null;

    const handleSave = () => {
        // Mock save logic
        console.log('Saving preferences:', prefs);
        onClose();
    };

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm animate-fadeIn">
            <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden animate-slideUp">
                {/* Header */}
                <div className="bg-slate-900 p-6 text-white flex justify-between items-center">
                    <div>
                        <h2 className="text-xl font-bold flex items-center gap-2">
                            <Bell className="w-5 h-5 text-emerald-400" /> Notification Settings
                        </h2>
                        <p className="text-slate-400 text-sm">Customize how you receive alerts</p>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-full transition-colors">
                        <X className="w-6 h-6" />
                    </button>
                </div>

                {/* Content */}
                <div className="p-6 space-y-6">
                    {/* Primary Region */}
                    <div className="space-y-3">
                        <label className="text-sm font-bold text-slate-700 uppercase tracking-wider flex items-center gap-2">
                            <MapPin className="w-4 h-4" /> Primary Alert Region
                        </label>
                        <select
                            value={prefs.region}
                            onChange={(e) => setPrefs({ ...prefs, region: e.target.value })}
                            className="w-full p-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500 outline-none transition-all"
                        >
                            <option value="Maharashtra">Maharashtra</option>
                            <option value="Delhi">Delhi</option>
                            <option value="Karnataka">Karnataka</option>
                            <option value="Global">All Regions (Global)</option>
                        </select>
                    </div>

                    {/* Channels */}
                    <div className="space-y-4">
                        <label className="text-sm font-bold text-slate-700 uppercase tracking-wider">
                            Delivery Channels
                        </label>

                        <div className="space-y-3">
                            {/* Email */}
                            <div className="flex items-center justify-between p-4 bg-slate-50 rounded-xl border border-slate-100">
                                <div className="flex items-center gap-3">
                                    <div className="p-2 bg-blue-100 text-blue-600 rounded-lg">
                                        <Mail className="w-5 h-5" />
                                    </div>
                                    <div>
                                        <div className="font-bold text-slate-800">Email Alerts</div>
                                        <div className="text-xs text-slate-500">Detailed outbreak reports</div>
                                    </div>
                                </div>
                                <button
                                    onClick={() => setPrefs({ ...prefs, email: !prefs.email })}
                                    className={`w-12 h-6 rounded-full transition-all relative ${prefs.email ? 'bg-emerald-500' : 'bg-slate-300'}`}
                                >
                                    <div className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-all ${prefs.email ? 'left-7' : 'left-1'}`} />
                                </button>
                            </div>

                            {/* SMS */}
                            <div className="flex items-center justify-between p-4 bg-slate-50 rounded-xl border border-slate-100">
                                <div className="flex items-center gap-3">
                                    <div className="p-2 bg-purple-100 text-purple-600 rounded-lg">
                                        <Smartphone className="w-5 h-5" />
                                    </div>
                                    <div>
                                        <div className="font-bold text-slate-800">SMS Alerts</div>
                                        <div className="text-xs text-slate-500">Immediate critical warnings</div>
                                    </div>
                                </div>
                                <button
                                    onClick={() => setPrefs({ ...prefs, sms: !prefs.sms })}
                                    className={`w-12 h-6 rounded-full transition-all relative ${prefs.sms ? 'bg-emerald-500' : 'bg-slate-300'}`}
                                >
                                    <div className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-all ${prefs.sms ? 'left-7' : 'left-1'}`} />
                                </button>
                            </div>

                            {/* In-App */}
                            <div className="flex items-center justify-between p-4 bg-slate-50 rounded-xl border border-slate-100">
                                <div className="flex items-center gap-3">
                                    <div className="p-2 bg-emerald-100 text-emerald-600 rounded-lg">
                                        <Bell className="w-5 h-5" />
                                    </div>
                                    <div>
                                        <div className="font-bold text-slate-800">App Notifications</div>
                                        <div className="text-xs text-slate-500">Visual indicators on dashboard</div>
                                    </div>
                                </div>
                                <button
                                    onClick={() => setPrefs({ ...prefs, inApp: !prefs.inApp })}
                                    className={`w-12 h-6 rounded-full transition-all relative ${prefs.inApp ? 'bg-emerald-500' : 'bg-slate-300'}`}
                                >
                                    <div className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-all ${prefs.inApp ? 'left-7' : 'left-1'}`} />
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Footer */}
                <div className="p-6 bg-slate-50 flex gap-3">
                    <button
                        onClick={onClose}
                        className="flex-1 py-3 px-4 border border-slate-200 rounded-xl font-bold text-slate-600 hover:bg-slate-100 transition-colors"
                    >
                        Cancel
                    </button>
                    <button
                        onClick={handleSave}
                        className="flex-1 py-3 px-4 bg-emerald-600 text-white rounded-xl font-bold flex items-center justify-center gap-2 hover:bg-emerald-700 shadow-lg shadow-emerald-200 transition-all"
                    >
                        <Save className="w-5 h-5" /> Save Changes
                    </button>
                </div>
            </div>
        </div>
    );
};
