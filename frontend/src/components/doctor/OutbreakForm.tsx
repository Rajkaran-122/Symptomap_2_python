import { useState } from 'react';
import { MapPin, Users, AlertCircle, CheckCircle } from 'lucide-react';
import MapPicker from './MapPicker';
import { API_BASE_URL } from '../../config/api';

interface OutbreakFormProps {
    onSuccess: () => void;
}

const OutbreakForm = ({ onSuccess }: OutbreakFormProps) => {
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState(false);
    const [error, setError] = useState('');

    const [formData, setFormData] = useState({
        disease_type: '',
        patient_count: '',
        severity: 'moderate',
        latitude: 19.0760,
        longitude: 72.8777,
        location_name: '',
        city: '',
        state: '',
        description: '',
    });

    const diseases = [
        'COVID-19', 'Dengue', 'Malaria', 'Tuberculosis', 'Influenza',
        'Typhoid', 'Cholera', 'Hepatitis', 'Measles', 'Other'
    ];

    const handleLocationSelect = (lat: number, lng: number, name: string) => {
        setFormData(prev => ({
            ...prev,
            latitude: lat,
            longitude: lng,
            location_name: name
        }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setSuccess(false);
        setLoading(true);

        try {
            const token = localStorage.getItem('doctor_token');

            const response = await fetch(`${API_BASE_URL}/doctor/outbreak`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    ...formData,
                    patient_count: parseInt(formData.patient_count)
                }),
            });

            if (!response.ok) {
                throw new Error('Failed to submit outbreak');
            }

            setSuccess(true);
            setFormData({
                disease_type: '',
                patient_count: '',
                severity: 'moderate',
                latitude: 19.0760,
                longitude: 72.8777,
                location_name: '',
                city: '',
                state: '',
                description: '',
            });
            onSuccess();

            setTimeout(() => setSuccess(false), 3000);
        } catch (err) {
            setError('Failed to submit outbreak. Please try again.');
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
                    <span>Outbreak reported successfully!</span>
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
                {/* Disease Type */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Disease Type *
                    </label>
                    <select
                        value={formData.disease_type}
                        onChange={(e) => setFormData(prev => ({ ...prev, disease_type: e.target.value }))}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        required
                    >
                        <option value="">Select disease</option>
                        {diseases.map(disease => (
                            <option key={disease} value={disease}>{disease}</option>
                        ))}
                    </select>
                </div>

                {/* Patient Count */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        <div className="flex items-center gap-2">
                            <Users className="w-4 h-4" />
                            Number of Patients *
                        </div>
                    </label>
                    <input
                        type="number"
                        min="1"
                        value={formData.patient_count}
                        onChange={(e) => setFormData(prev => ({ ...prev, patient_count: e.target.value }))}
                        placeholder="Enter patient count"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        required
                    />
                </div>

                {/* Severity */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Severity Level *
                    </label>
                    <select
                        value={formData.severity}
                        onChange={(e) => setFormData(prev => ({ ...prev, severity: e.target.value }))}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        required
                    >
                        <option value="mild">Mild</option>
                        <option value="moderate">Moderate</option>
                        <option value="severe">Severe</option>
                    </select>
                </div>

                {/* City */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        City *
                    </label>
                    <input
                        type="text"
                        value={formData.city}
                        onChange={(e) => setFormData(prev => ({ ...prev, city: e.target.value }))}
                        placeholder="e.g., Mumbai"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        required
                    />
                </div>

                {/* State */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        State *
                    </label>
                    <input
                        type="text"
                        value={formData.state}
                        onChange={(e) => setFormData(prev => ({ ...prev, state: e.target.value }))}
                        placeholder="e.g., Maharashtra"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        required
                    />
                </div>

                {/* Location Name */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        <div className="flex items-center gap-2">
                            <MapPin className="w-4 h-4" />
                            Location/Hospital Name *
                        </div>
                    </label>
                    <input
                        type="text"
                        value={formData.location_name}
                        onChange={(e) => setFormData(prev => ({ ...prev, location_name: e.target.value }))}
                        placeholder="e.g., City General Hospital"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        required
                    />
                </div>
            </div>

            {/* Map Picker */}
            <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                    Mark Location on Map *
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

            {/* Description */}
            <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                    Additional Notes
                </label>
                <textarea
                    value={formData.description}
                    onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                    rows={3}
                    placeholder="Any additional information about the outbreak..."
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
            </div>

            {/* Submit Button */}
            <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-4 rounded-lg transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
                {loading ? 'Submitting...' : 'Submit Outbreak Report'}
            </button>
        </form>
    );
};

export default OutbreakForm;
