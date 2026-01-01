import { useState } from 'react';
import { Mail, Bell, CheckCircle, AlertTriangle, Send, X } from 'lucide-react';

interface EmailNotificationProps {
    onClose?: () => void;
}

const EmailNotification = ({ onClose }: EmailNotificationProps) => {
    const [email, setEmail] = useState('');
    const [notifyTypes, setNotifyTypes] = useState({
        outbreaks: true,
        approvals: true,
        alerts: true,
        reports: false,
    });
    const [sending, setSending] = useState(false);
    const [sent, setSent] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!email) return;

        setSending(true);

        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1500));

        // Store in localStorage to simulate persistence
        const subscriptions = JSON.parse(localStorage.getItem('email_subscriptions') || '[]');
        subscriptions.push({
            email,
            types: notifyTypes,
            subscribedAt: new Date().toISOString()
        });
        localStorage.setItem('email_subscriptions', JSON.stringify(subscriptions));

        setSending(false);
        setSent(true);

        // Reset after showing success
        setTimeout(() => {
            setSent(false);
            setEmail('');
        }, 3000);
    };

    const toggleType = (type: keyof typeof notifyTypes) => {
        setNotifyTypes(prev => ({ ...prev, [type]: !prev[type] }));
    };

    if (sent) {
        return (
            <div className="bg-white/90 backdrop-blur-xl rounded-2xl shadow-xl border border-white/20 p-6 text-center">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-emerald-500 to-green-600 flex items-center justify-center">
                    <CheckCircle className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-bold text-gray-800 mb-2">Subscribed!</h3>
                <p className="text-gray-600 text-sm">You'll receive notifications at {email}</p>
            </div>
        );
    }

    return (
        <div className="bg-white/90 backdrop-blur-xl rounded-2xl shadow-xl border border-white/20 p-6 relative overflow-hidden">
            {/* Background decoration */}
            <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-blue-500/10 to-indigo-500/5 rounded-full blur-3xl -z-10"></div>

            {/* Close button */}
            {onClose && (
                <button
                    onClick={onClose}
                    className="absolute top-4 right-4 p-1.5 rounded-lg hover:bg-gray-100 transition-colors"
                >
                    <X className="w-4 h-4 text-gray-400" />
                </button>
            )}

            {/* Header */}
            <div className="flex items-center gap-3 mb-6">
                <div className="p-2.5 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 shadow-lg shadow-blue-300/50">
                    <Bell className="w-5 h-5 text-white" />
                </div>
                <div>
                    <h3 className="font-bold text-gray-800 text-lg">Email Notifications</h3>
                    <p className="text-xs text-gray-400">Stay updated on outbreak alerts</p>
                </div>
            </div>

            <form onSubmit={handleSubmit}>
                {/* Email Input */}
                <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">Email Address</label>
                    <div className="relative">
                        <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="doctor@hospital.com"
                            className="w-full pl-11 pr-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all text-sm"
                            required
                        />
                    </div>
                </div>

                {/* Notification Types */}
                <div className="mb-5">
                    <label className="block text-sm font-medium text-gray-700 mb-3">Notify me about:</label>
                    <div className="grid grid-cols-2 gap-2">
                        {[
                            { key: 'outbreaks', label: 'New Outbreaks', icon: AlertTriangle, color: 'red' },
                            { key: 'approvals', label: 'Approvals', icon: CheckCircle, color: 'green' },
                            { key: 'alerts', label: 'Risk Alerts', icon: Bell, color: 'amber' },
                            { key: 'reports', label: 'Weekly Reports', icon: Mail, color: 'blue' },
                        ].map(({ key, label, icon: Icon, color }) => (
                            <button
                                key={key}
                                type="button"
                                onClick={() => toggleType(key as keyof typeof notifyTypes)}
                                className={`p-3 rounded-xl border-2 transition-all flex items-center gap-2 ${notifyTypes[key as keyof typeof notifyTypes]
                                        ? `border-${color}-500 bg-${color}-50 text-${color}-700`
                                        : 'border-gray-200 text-gray-500 hover:border-gray-300'
                                    }`}
                            >
                                <Icon className="w-4 h-4" />
                                <span className="text-xs font-medium">{label}</span>
                            </button>
                        ))}
                    </div>
                </div>

                {/* Submit Button */}
                <button
                    type="submit"
                    disabled={sending || !email}
                    className="w-full py-3 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold flex items-center justify-center gap-2 transition-all disabled:opacity-50 shadow-lg shadow-blue-200"
                >
                    {sending ? (
                        <>
                            <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                            Subscribing...
                        </>
                    ) : (
                        <>
                            <Send className="w-4 h-4" />
                            Subscribe to Alerts
                        </>
                    )}
                </button>
            </form>

            {/* Note */}
            <p className="text-[10px] text-gray-400 text-center mt-4">
                Unsubscribe anytime. We respect your inbox.
            </p>
        </div>
    );
};

export default EmailNotification;
