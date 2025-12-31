import { useState } from 'react';
import { MapPin, Search } from 'lucide-react';

interface MapPickerProps {
    latitude: number;
    longitude: number;
    onLocationSelect: (lat: number, lng: number, name: string) => void;
}

const MapPicker = ({ latitude, longitude, onLocationSelect }: MapPickerProps) => {
    const [manualLat, setManualLat] = useState(latitude.toString());
    const [manualLng, setManualLng] = useState(longitude.toString());
    const [locationSearch, setLocationSearch] = useState('');

    // Predefined locations for quick selection
    const predefinedLocations = [
        { name: 'Mumbai, Maharashtra', lat: 19.0760, lng: 72.8777 },
        { name: 'Delhi', lat: 28.6139, lng: 77.2090 },
        { name: 'Bangalore, Karnataka', lat: 12.9716, lng: 77.5946 },
        { name: 'Chennai, Tamil Nadu', lat: 13.0827, lng: 80.2707 },
        { name: 'Kolkata, West Bengal', lat: 22.5726, lng: 88.3639 },
        { name: 'Hyderabad, Telangana', lat: 17.3850, lng: 78.4867 },
        { name: 'Pune, Maharashtra', lat: 18.5204, lng: 73.8567 },
        { name: 'Ahmedabad, Gujarat', lat: 23.0225, lng: 72.5714 },
    ];

    const filteredLocations = predefinedLocations.filter(loc =>
        loc.name.toLowerCase().includes(locationSearch.toLowerCase())
    );

    const handleManualUpdate = () => {
        const lat = parseFloat(manualLat);
        const lng = parseFloat(manualLng);

        if (!isNaN(lat) && !isNaN(lng) && lat >= -90 && lat <= 90 && lng >= -180 && lng <= 180) {
            onLocationSelect(lat, lng, `Custom Location`);
        }
    };

    return (
        <div className="space-y-4">
            {/* Search Cities */}
            <div>
                <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                    <input
                        type="text"
                        value={locationSearch}
                        onChange={(e) => setLocationSearch(e.target.value)}
                        placeholder="Search major cities..."
                        className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                    />
                </div>

                {locationSearch && (
                    <div className="mt-2 max-h-40 overflow-y-auto border border-gray-200 rounded-lg">
                        {filteredLocations.map((loc, idx) => (
                            <button
                                key={idx}
                                type="button"
                                onClick={() => {
                                    onLocationSelect(loc.lat, loc.lng, loc.name);
                                    setManualLat(loc.lat.toString());
                                    setManualLng(loc.lng.toString());
                                    setLocationSearch('');
                                }}
                                className="w-full px-4 py-2 text-left hover:bg-gray-50 text-sm flex items-center gap-2"
                            >
                                <MapPin className="w-4 h-4 text-gray-400" />
                                {loc.name}
                            </button>
                        ))}
                        {filteredLocations.length === 0 && (
                            <div className="px-4 py-3 text-sm text-gray-500">No cities found</div>
                        )}
                    </div>
                )}
            </div>

            {/* Manual Coordinates */}
            <div>
                <p className="text-sm font-medium text-gray-700 mb-2">Or enter coordinates manually:</p>
                <div className="grid grid-cols-2 gap-3">
                    <div>
                        <label className="block text-xs text-gray-600 mb-1">Latitude</label>
                        <input
                            type="number"
                            step="0.0001"
                            value={manualLat}
                            onChange={(e) => setManualLat(e.target.value)}
                            onBlur={handleManualUpdate}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                    </div>
                    <div>
                        <label className="block text-xs text-gray-600 mb-1">Longitude</label>
                        <input
                            type="number"
                            step="0.0001"
                            value={manualLng}
                            onChange={(e) => setManualLng(e.target.value)}
                            onBlur={handleManualUpdate}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                    </div>
                </div>
            </div>

            {/* Visual Map Placeholder */}
            <div className="bg-gray-100 rounded-lg p-8 text-center border-2 border-dashed border-gray-300">
                <MapPin className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                <p className="text-sm text-gray-600">Map View</p>
                <p className="text-xs text-gray-500 mt-1">
                    Location: {latitude.toFixed(4)}, {longitude.toFixed(4)}
                </p>
                <p className="text-xs text-gray-400 mt-2">
                    (Interactive map can be added with MapLibre GL)
                </p>
            </div>
        </div>
    );
};

export default MapPicker;
