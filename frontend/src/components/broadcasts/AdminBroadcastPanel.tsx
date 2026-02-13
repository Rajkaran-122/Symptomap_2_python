
import React, { useState, useEffect } from 'react';
import { Radio, Clock, MapPin, Plus, X, Send } from 'lucide-react';
import { authClient } from '../../services/auth';

interface Broadcast {
    id: string;
    title: string;
    content: string;
    severity: 'info' | 'warning' | 'critical' | 'emergency';
    region: string | null;
    channels: string[];
    created_at: string;
    expires_at: string | null;
    is_automated: boolean;
    active: boolean;
}

const AdminBroadcastPanel: React.FC = () => {
    const [broadcasts, setBroadcasts] = useState<Broadcast[]>([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);

    // New Broadcast Form State
    const [formData, setFormData] = useState({
        title: '',
        content: '',
        severity: 'info',
        region: 'India',
        channels: {
            app: true,
            email: false,
            sms: false
        },
        expires_hours: 24
    });

    useEffect(() => {
        fetchBroadcasts();
    }, []);

    const fetchBroadcasts = async () => {
        try {
            const response = await authClient.get('/broadcasts');
            setBroadcasts(Array.isArray(response.data) ? response.data : []);
        } catch (err) {
            console.error('Failed to fetch broadcasts', err);
        } finally {
            setLoading(false);
        }
    };

    const handleCreate = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            // Calculate expiry
            const expiresAt = new Date();
            expiresAt.setHours(expiresAt.getHours() + formData.expires_hours);

            // Convert object channels to list for API
            const activeChannels = Object.entries(formData.channels)
                .filter(([_, active]) => active)
                .map(([channel]) => channel === 'app' ? 'in_app' : channel);

            const payload = {
                title: formData.title,
                content: formData.content,
                severity: formData.severity,
                region: formData.region,
                channels: activeChannels,
                expires_at: expiresAt.toISOString(),
                is_active: true
            };

            await authClient.post('/broadcasts', payload);

            setShowModal(false);
            setFormData({
                title: '',
                content: '',
                severity: 'info',
                region: 'India',
                channels: {
                    app: true,
                    email: false,
                    sms: false
                },
                expires_hours: 24
            });
            fetchBroadcasts();
            alert('Broadcast sent successfully!');
        } catch (err) {
            console.error('Failed to create broadcast', err);
            alert('Failed to send broadcast');
        }
    };

    const getSeverityColor = (severity: string) => {
        const colors: any = {
            info: 'bg-blue-100 text-blue-800 border-blue-200',
            warning: 'bg-amber-100 text-amber-800 border-amber-200',
            critical: 'bg-red-100 text-red-800 border-red-200',
            emergency: 'bg-red-200 text-red-900 border-red-300 animate-pulse'
        };
        return colors[severity] || colors.info;
    };

    return (
        <div className="p-6 max-w-7xl mx-auto">
            <div className="flex justify-between items-center mb-6">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">Broadcast Management</h1>
                    <p className="text-gray-500">Send alerts and notifications to users</p>
                </div>
                <button
                    onClick={() => setShowModal(true)}
                    className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                >
                    <Plus className="w-5 h-5" /> New Broadcast
                </button>
            </div>

            {/* Broadcast List */}
            <div className="space-y-4">
                {loading ? (
                    <p className="text-gray-500 text-center py-8">Loading broadcasts...</p>
                ) : broadcasts.length === 0 ? (
                    <div className="text-center py-12 bg-white rounded-xl border border-dashed border-gray-300">
                        <Radio className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                        <h3 className="text-lg font-medium text-gray-900">No Broadcasts Yet</h3>
                        <p className="text-gray-500">Create your first broadcast to alert users.</p>
                    </div>
                ) : (
                    broadcasts.map(b => (
                        <div key={b.id} className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
                            <div className="flex justify-between items-start mb-2">
                                <div className="flex items-center gap-2">
                                    <span className={`px-2 py-0.5 rounded text-xs font-semibold uppercase ${getSeverityColor(b.severity)}`}>
                                        {b.severity}
                                    </span>
                                    {b.is_automated && (
                                        <span className="bg-purple-100 text-purple-800 px-2 py-0.5 rounded text-xs">AI Generated</span>
                                    )}
                                </div>
                                <span className="text-gray-400 text-sm flex items-center gap-1">
                                    <Clock className="w-3 h-3" />
                                    {new Date(b.created_at).toLocaleString()}
                                </span>
                            </div>

                            <h3 className="text-lg font-bold text-gray-900 mb-2">{b.title}</h3>
                            <p className="text-gray-600 mb-4">{b.content}</p>

                            <div className="flex items-center gap-4 text-sm text-gray-500 pt-4 border-t border-gray-100">
                                <span className="flex items-center gap-1">
                                    <MapPin className="w-4 h-4" />
                                    {b.region || 'Global'}
                                </span>
                                <span className="flex items-center gap-1">
                                    <Send className="w-4 h-4" />
                                    {b.channels.join(', ')}
                                </span>
                            </div>
                        </div>
                    ))
                )}
            </div>

            {/* Create Modal */}
            {showModal && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-xl shadow-xl w-full max-w-lg overflow-hidden">
                        <div className="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-gray-50">
                            <h2 className="text-lg font-bold text-gray-900">New Broadcast</h2>
                            <button onClick={() => setShowModal(false)} className="text-gray-400 hover:text-gray-600">
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        <form onSubmit={handleCreate} className="p-6 space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
                                <input
                                    type="text"
                                    required
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                                    placeholder="e.g., Heavy Rain Alert"
                                    value={formData.title}
                                    onChange={e => setFormData({ ...formData, title: e.target.value })}
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Content</label>
                                <textarea
                                    required
                                    rows={4}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                                    placeholder="Detailed message..."
                                    value={formData.content}
                                    onChange={e => setFormData({ ...formData, content: e.target.value })}
                                />
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Severity</label>
                                    <select
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                                        value={formData.severity}
                                        onChange={e => setFormData({ ...formData, severity: e.target.value as any })}
                                    >
                                        <option value="info">Info</option>
                                        <option value="warning">Warning</option>
                                        <option value="critical">Critical</option>
                                        <option value="emergency">Emergency</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Region</label>
                                    <select
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                                        value={formData.region}
                                        onChange={e => setFormData({ ...formData, region: e.target.value })}
                                    >
                                        <option value="India">India (Global)</option>
                                        <option value="Rajasthan">Rajasthan</option>
                                        <option value="Maharashtra">Maharashtra</option>
                                        <option value="Karnataka">Karnataka</option>
                                        <option value="Tamil Nadu">Tamil Nadu</option>
                                        <option value="Delhi">Delhi</option>
                                        <option value="Gujarat">Gujarat</option>
                                        <option value="Uttar Pradesh">Uttar Pradesh</option>
                                        <option value="West Bengal">West Bengal</option>
                                        <option value="Telangana">Telangana</option>
                                        <option value="Kerala">Kerala</option>
                                        <option value="Madhya Pradesh">Madhya Pradesh</option>
                                    </select>
                                </div>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Delivery Channels</label>
                                <div className="flex gap-4 p-3 bg-gray-50 rounded-lg border border-gray-200">
                                    <label className="flex items-center gap-2 cursor-pointer group">
                                        <input
                                            type="checkbox"
                                            className="w-4 h-4 text-indigo-600 rounded border-gray-300 focus:ring-indigo-500"
                                            checked={formData.channels.app}
                                            onChange={e => setFormData({
                                                ...formData,
                                                channels: { ...formData.channels, app: e.target.checked }
                                            })}
                                        />
                                        <span className="text-sm text-gray-700 group-hover:text-indigo-600 transition-colors">In-App</span>
                                    </label>
                                    <label className="flex items-center gap-2 cursor-pointer group">
                                        <input
                                            type="checkbox"
                                            className="w-4 h-4 text-indigo-600 rounded border-gray-300 focus:ring-indigo-500"
                                            checked={formData.channels.email}
                                            onChange={e => setFormData({
                                                ...formData,
                                                channels: { ...formData.channels, email: e.target.checked }
                                            })}
                                        />
                                        <span className="text-sm text-gray-700 group-hover:text-indigo-600 transition-colors">Email</span>
                                    </label>
                                    <label className="flex items-center gap-2 cursor-pointer group">
                                        <input
                                            type="checkbox"
                                            className="w-4 h-4 text-indigo-600 rounded border-gray-300 focus:ring-indigo-500"
                                            checked={formData.channels.sms}
                                            onChange={e => setFormData({
                                                ...formData,
                                                channels: { ...formData.channels, sms: e.target.checked }
                                            })}
                                        />
                                        <span className="text-sm text-gray-700 group-hover:text-indigo-600 transition-colors">SMS</span>
                                    </label>
                                </div>
                                <p className="mt-1 text-xs text-gray-500">Critical alerts should use multiple channels for better reach.</p>
                            </div>

                            <div className="flex justify-end gap-3 pt-4">
                                <button
                                    type="button"
                                    onClick={() => setShowModal(false)}
                                    className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center gap-2"
                                >
                                    <Send className="w-4 h-4" /> Send Broadcast
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default AdminBroadcastPanel;
