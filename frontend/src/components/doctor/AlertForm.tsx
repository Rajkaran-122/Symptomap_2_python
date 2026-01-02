import { useState } from 'react';
import { AlertTriangle, MapPin, Clock, CheckCircle, AlertCircle } from 'lucide-react';
import MapPicker from './MapPicker';
import { API_BASE_URL } from '../../config/api';

interface AlertFormProps {
    onSuccess: () => void;
}

const AlertForm = ({ onSuccess }: AlertFormProps) => {
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState(false);
    const [error, setError] = useState('');

    const [formData, setFormData] = useState({
        alert_type: 'warning',
        title: '',
        message: '',
        latitude: 19.0760,
        longitude: 72.8777,
        affected_area: '',
        expiry_hours: 24,
    });

    const handleLocationSelect = (lat: number, lng: number, name: string) => {
        setFormData(prev => ({
            ...prev,
            latitude: lat,
            longitude: lng,
            affected_area: name
        }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setSuccess(false);
        setLoading(true);

        try {
            const token = localStorage.getItem('doctor_token');

            const response = await fetch(`${API_BASE_URL}/doctor/alert`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    ...formData,
                    expiry_hours: parseInt(String(formData.expiry_hours))
                }),
            });

            if (!response.ok) {
                throw new Error('Failed to create alert');
            }

            setSuccess(true);
            setFormData({
                alert_type: 'warning',
                title: '',
                message: '',
                latitude: 19.0760,
                longitude: 72.8777,
                affected_area: '',
                expiry_hours: 24,
            });
            onSuccess();

            setTimeout(() => setSuccess(false), 3000);
        } catch (err) {
            setError('Failed to create alert. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="space-y-6">
            {/* Success Message */}
            {success && (
                <div className="flex items-center gap-2 p-4 bg-green-50 border border-green-200 rounded-lg text-green-700">
                    <CheckCircle className="w-5 h-5" />
                    <span>Alert created successfully!</span>
                </div>
            )}

            {/* Error Message */}
            {error && (
                <div className="flex items-center gap-2 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
                    <AlertCircle className="w-5 h-5" />
                    <span>{error}</span>
                </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Alert Type */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        <div className="flex items-center gap-2">
                            <AlertTriangle className="w-4 h-4" />
                            Alert Type *
                        </div>
                    </label>
                    <select
                        value={formData.alert_type}
                        onChange={(e) => setFormData(prev => ({ ...prev, alert_type: e.target.value }))}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        required
                    >
                        <option value="info">Info</option>
                        <option value="warning">Warning</option>
                        <option value="critical">Critical</option>
                    </select>
                </div>

                {/* Expiry Hours */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        <div className="flex items-center gap-2">
                            <Clock className="w-4 h-4" />
                            Alert Duration (hours) *
                        </div>
                    </label>
                    <input
                        type="number"
                        min="1"
                        max="168"
                        value={formData.expiry_hours}
                        onChange={(e) => setFormData(prev => ({ ...prev, expiry_hours: parseInt(e.target.value) }))}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        required
                    />
                    <p className="text-xs text-gray-500 mt-1">Max: 168 hours (7 days)</p>
                </div>
            </div>

            {/* Title */}
            <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                    Alert Title *
                </label>
                <input
                    type="text"
                    value={formData.title}
                    onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                    placeholder="e.g., High Dengue Risk in Western Suburbs"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                />
            </div>

            {/* Message */}
            <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                    Alert Message *
                </label>
                <textarea
                    value={formData.message}
                    onChange={(e) => setFormData(prev => ({ ...prev, message: e.target.value }))}
                    rows={4}
                    placeholder="Detailed alert message for healthcare professionals and the public..."
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                />
            </div>

            {/* Affected Area */}
            <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                    <div className="flex items-center gap-2">
                        <MapPin className="w-4 h-4" />
                        Affected Area *
                    </div>
                </label>
                <input
                    type="text"
                    value={formData.affected_area}
                    onChange={(e) => setFormData(prev => ({ ...prev, affected_area: e.target.value }))}
                    placeholder="e.g., Andheri West, Mumbai"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                />
            </div>

            {/* Map Picker */}
            <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                    Mark Alert Location on Map *
                </label>
                <MapPicker
                    latitude={formData.latitude}
                    longitude={formData.longitude}
                    onLocationSelect={handleLocationSelect}
                />
                <p className="text-xs text-gray-500 mt-1">
                    Current: {formData.latitude.toFixed(4)}, {formData.longitude.toFixed(4)}
                </p>
            </div>

            {/* Submit Button */}
            <button
                type="submit"
                disabled={loading}
                className="w-full bg-orange-600 hover:bg-orange-700 text-white font-semibold py-3 px-4 rounded-lg transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
                {loading ? 'Creating Alert...' : 'Create Alert'}
            </button>
        </form>
    );
};

export default AlertForm;
