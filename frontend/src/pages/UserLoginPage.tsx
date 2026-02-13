import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Lock, Mail, AlertCircle, ArrowRight, Loader2, Heart, Eye, EyeOff } from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import toast from 'react-hot-toast';

const UserLoginPage = () => {
    const navigate = useNavigate();
    const { login, isLoading } = useAuthStore();

    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        try {
            await login({ email, password });
            const currentUser = useAuthStore.getState().user;
            toast.success(`Welcome back, ${currentUser?.full_name || 'User'}!`);
            if (currentUser?.role === 'user') {
                navigate('/user/dashboard');
            } else {
                navigate('/dashboard');
            }
        } catch (err: any) {
            const msg = err.message || 'Login failed';
            setError(msg);
            toast.error(msg);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 flex items-center justify-center p-4 relative overflow-hidden">
            {/* Premium animated background */}
            <div className="absolute inset-0 pointer-events-none">
                <div className="absolute top-[-20%] right-[-10%] w-[500px] h-[500px] bg-emerald-500/[0.07] rounded-full blur-[100px] animate-pulse" style={{ animationDuration: '8s' }} />
                <div className="absolute bottom-[-20%] left-[-10%] w-[400px] h-[400px] bg-teal-500/[0.07] rounded-full blur-[100px] animate-pulse" style={{ animationDuration: '6s' }} />
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-cyan-500/[0.03] rounded-full blur-[120px]" />
            </div>

            <div className="max-w-[420px] w-full relative z-10">
                {/* Logo & Title */}
                <div className="text-center mb-10">
                    <div className="inline-flex items-center justify-center w-20 h-20 rounded-3xl bg-gradient-to-br from-emerald-500/20 to-teal-500/20 mb-5 shadow-2xl shadow-emerald-500/10 border border-emerald-500/10">
                        <Heart className="w-10 h-10 text-emerald-400" />
                    </div>
                    <h1 className="text-3xl font-bold text-white mb-1.5 tracking-tight">
                        Welcome Back
                    </h1>
                    <p className="text-slate-400 text-sm">
                        Sign in to your health portal
                    </p>
                </div>

                {/* Card */}
                <div className="bg-slate-800/40 backdrop-blur-2xl border border-slate-700/50 rounded-3xl p-8 shadow-2xl">
                    {/* Top accent */}
                    <div className="absolute top-0 left-8 right-8 h-px bg-gradient-to-r from-transparent via-emerald-500/40 to-transparent" />

                    <form onSubmit={handleSubmit} className="space-y-5">
                        {/* Email */}
                        <div>
                            <label className="block text-sm font-medium text-slate-300 mb-2">Email</label>
                            <div className="relative group">
                                <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-[18px] h-[18px] text-slate-500 group-focus-within:text-emerald-400 transition-colors" />
                                <input
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    className="w-full bg-slate-900/60 border border-slate-600/50 rounded-xl py-3 pl-11 pr-4 text-white placeholder-slate-500 focus:ring-2 focus:ring-emerald-500/40 focus:border-emerald-500/50 transition-all outline-none"
                                    placeholder="you@example.com"
                                    required
                                    autoComplete="email"
                                />
                            </div>
                        </div>

                        {/* Password */}
                        <div>
                            <label className="block text-sm font-medium text-slate-300 mb-2">Password</label>
                            <div className="relative group">
                                <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-[18px] h-[18px] text-slate-500 group-focus-within:text-emerald-400 transition-colors" />
                                <input
                                    type={showPassword ? 'text' : 'password'}
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="w-full bg-slate-900/60 border border-slate-600/50 rounded-xl py-3 pl-11 pr-12 text-white placeholder-slate-500 focus:ring-2 focus:ring-emerald-500/40 focus:border-emerald-500/50 transition-all outline-none"
                                    placeholder="Enter your password"
                                    required
                                    autoComplete="current-password"
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 transition-colors"
                                >
                                    {showPassword ? <EyeOff className="w-[18px] h-[18px]" /> : <Eye className="w-[18px] h-[18px]" />}
                                </button>
                            </div>
                        </div>

                        {/* Error */}
                        {error && (
                            <div className="flex items-center gap-2.5 p-3 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-sm animate-in fade-in slide-in-from-top-1 duration-200">
                                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                                <span>{error}</span>
                            </div>
                        )}

                        {/* Submit */}
                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-semibold py-3.5 px-4 rounded-xl transition-all duration-200 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed group shadow-lg shadow-emerald-600/20 hover:shadow-emerald-500/30 mt-2"
                        >
                            {isLoading ? (
                                <Loader2 className="w-5 h-5 animate-spin" />
                            ) : (
                                <>Sign In <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" /></>
                            )}
                        </button>
                    </form>

                    {/* Divider */}
                    <div className="flex items-center gap-3 my-6">
                        <div className="flex-1 h-px bg-slate-700/50" />
                        <span className="text-xs text-slate-500 uppercase tracking-wider">or</span>
                        <div className="flex-1 h-px bg-slate-700/50" />
                    </div>

                    {/* Register link */}
                    <Link
                        to="/register"
                        className="block w-full text-center py-3 border border-slate-600/50 hover:border-emerald-500/30 rounded-xl text-slate-300 hover:text-emerald-400 transition-all text-sm font-medium hover:bg-emerald-500/5"
                    >
                        Create a new account
                    </Link>
                </div>

                {/* Footer links */}
                <div className="mt-8 flex justify-center gap-6 text-xs text-slate-500">
                    <Link to="/login" className="hover:text-slate-300 transition-colors flex items-center gap-1">
                        Doctor Portal →
                    </Link>
                    <Link to="/" className="hover:text-slate-300 transition-colors">
                        Back to Home
                    </Link>
                </div>
            </div>
        </div>
    );
};

export default UserLoginPage;
