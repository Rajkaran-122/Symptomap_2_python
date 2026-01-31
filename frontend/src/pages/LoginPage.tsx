import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Lock, Mail, AlertCircle, ArrowRight, ShieldCheck, Loader2 } from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import toast from 'react-hot-toast';

const LoginPage = () => {
    const navigate = useNavigate();
    const { login, isLoading } = useAuthStore();

    const [credentials, setCredentials] = useState({
        email: '',
        password: '',
        mfa_code: ''
    });
    const [showMFA, setShowMFA] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        try {
            await login(credentials);
            toast.success('Welcome back!');
            navigate('/dashboard');
        } catch (err: any) {
            if (err.message === 'MFA_REQUIRED') {
                setShowMFA(true);
                toast('Please enter your MFA code', { icon: '🔐' });
            } else {
                setError(err.message || 'Login failed');
                toast.error(err.message || 'Login failed');
            }
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setCredentials(prev => ({
            ...prev,
            [e.target.name]: e.target.value
        }));
    };

    return (
        <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
            {/* Background effects */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <div className="absolute -top-1/2 -left-1/2 w-full h-full bg-blue-500/10 blur-[120px] rounded-full" />
                <div className="absolute top-1/2 left-1/2 w-full h-full bg-purple-500/10 blur-[120px] rounded-full" />
            </div>

            <div className="max-w-md w-full relative z-10">
                <div className="text-center mb-8">
                    <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-400 mb-2">
                        SymptoMap
                    </h1>
                    <p className="text-slate-400">Secure Disease Surveillance Platform</p>
                </div>

                <div className="bg-slate-800/50 backdrop-blur-xl border border-slate-700 rounded-2xl p-8 shadow-2xl">
                    <h2 className="text-2xl font-semibold text-white mb-6">
                        {showMFA ? 'Two-Factor Authentication' : 'Welcome Back'}
                    </h2>

                    <form onSubmit={handleSubmit} className="space-y-6">
                        {!showMFA ? (
                            <>
                                <div>
                                    <label className="block text-sm font-medium text-slate-300 mb-2">
                                        Email Address
                                    </label>
                                    <div className="relative">
                                        <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                                        <input
                                            name="email"
                                            type="email"
                                            value={credentials.email}
                                            onChange={handleChange}
                                            className="w-full bg-slate-900/50 border border-slate-600 rounded-lg py-3 pl-10 pr-4 text-white placeholder-slate-500 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                                            placeholder="doctor@hospital.com"
                                            required
                                        />
                                    </div>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-slate-300 mb-2">
                                        Password
                                    </label>
                                    <div className="relative">
                                        <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                                        <input
                                            name="password"
                                            type="password"
                                            value={credentials.password}
                                            onChange={handleChange}
                                            className="w-full bg-slate-900/50 border border-slate-600 rounded-lg py-3 pl-10 pr-4 text-white placeholder-slate-500 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                                            placeholder="••••••••••••"
                                            required
                                        />
                                    </div>
                                </div>
                            </>
                        ) : (
                            <div className="animate-in fade-in slide-in-from-right-4 duration-300">
                                <label className="block text-sm font-medium text-slate-300 mb-2">
                                    Authenticator Code
                                </label>
                                <div className="relative">
                                    <ShieldCheck className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                                    <input
                                        name="mfa_code"
                                        type="text"
                                        value={credentials.mfa_code}
                                        onChange={handleChange}
                                        className="w-full bg-slate-900/50 border border-slate-600 rounded-lg py-3 pl-10 pr-4 text-white placeholder-slate-500 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all tracking-widest text-center text-xl"
                                        placeholder="000 000"
                                        maxLength={6}
                                        autoFocus
                                        required
                                    />
                                </div>
                                <p className="text-xs text-slate-400 mt-2 text-center">
                                    Enter the 6-digit code from your authenticator app
                                </p>
                            </div>
                        )}

                        {error && (
                            <div className="flex items-center gap-2 p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm">
                                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                                <span>{error}</span>
                            </div>
                        )}

                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full bg-blue-600 hover:bg-blue-500 text-white font-semibold py-3 px-4 rounded-lg transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed group"
                        >
                            {isLoading ? (
                                <Loader2 className="w-5 h-5 animate-spin" />
                            ) : showMFA ? (
                                <>Verify & Login <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" /></>
                            ) : (
                                <>Sign In <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" /></>
                            )}
                        </button>
                    </form>

                    <div className="mt-6 text-center text-sm text-slate-400">
                        Don't have an account?{' '}
                        <Link to="/register" className="text-blue-400 hover:text-blue-300 font-medium transition-colors">
                            Register now
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default LoginPage;
