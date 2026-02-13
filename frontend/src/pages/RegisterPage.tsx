import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Lock, Mail, User, Phone, ArrowRight, Loader2, Check, Heart, Eye, EyeOff, AlertCircle } from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import { validatePassword } from '../services/auth';
import toast from 'react-hot-toast';

const RegisterPage = () => {
    const navigate = useNavigate();
    const { register, isLoading } = useAuthStore();

    const [formData, setFormData] = useState({
        email: '',
        password: '',
        full_name: '',
        phone: '',
        role: 'user'
    });

    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState('');
    const [passwordStrength, setPasswordStrength] = useState({
        score: 0,
        message: '',
        valid: false
    });

    useEffect(() => {
        if (formData.password) {
            setPasswordStrength(validatePassword(formData.password));
        } else {
            setPasswordStrength({ score: 0, message: '', valid: false });
        }
    }, [formData.password]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        if (!passwordStrength.valid) {
            toast.error('Please choose a stronger password');
            return;
        }

        // Auto-format phone
        let cleanPhone = formData.phone.replace(/\D/g, '');
        let formattedPhone = formData.phone.trim();

        if (cleanPhone.length > 0) {
            if (cleanPhone.length === 10 && !formattedPhone.startsWith('+')) {
                formattedPhone = '+91' + cleanPhone;
            } else if (!formattedPhone.startsWith('+')) {
                formattedPhone = '+' + cleanPhone;
            }
        }

        const submissionData = { ...formData, phone: formattedPhone };

        try {
            await register(submissionData);
            toast.success('Account created! Redirecting to login...');
            setTimeout(() => navigate('/user/login'), 1200);
        } catch (err: any) {
            const msg = err.message || 'Registration failed';
            // Handle duplicate account gracefully
            if (msg.toLowerCase().includes('already') || msg.toLowerCase().includes('exist') || msg.toLowerCase().includes('conflict')) {
                setError('An account with this email already exists.');
            } else {
                setError(msg);
            }
            toast.error(msg);
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setFormData(prev => ({
            ...prev,
            [e.target.name]: e.target.value
        }));
    };

    const getStrengthColor = (score: number) => {
        if (score < 40) return 'bg-red-500';
        if (score < 60) return 'bg-amber-500';
        if (score < 80) return 'bg-blue-400';
        return 'bg-emerald-500';
    };

    const getStrengthLabel = (score: number) => {
        if (score < 40) return 'Weak';
        if (score < 60) return 'Fair';
        if (score < 80) return 'Good';
        return 'Strong';
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 flex items-center justify-center p-4 py-8 relative overflow-hidden">
            {/* Animated background */}
            <div className="absolute inset-0 pointer-events-none">
                <div className="absolute top-[-20%] right-[-10%] w-[500px] h-[500px] bg-emerald-500/[0.07] rounded-full blur-[100px] animate-pulse" style={{ animationDuration: '8s' }} />
                <div className="absolute bottom-[-20%] left-[-10%] w-[400px] h-[400px] bg-teal-500/[0.07] rounded-full blur-[100px] animate-pulse" style={{ animationDuration: '6s' }} />
            </div>

            <div className="max-w-[480px] w-full relative z-10">
                {/* Header */}
                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-emerald-500/20 to-teal-500/20 mb-4 shadow-2xl shadow-emerald-500/10 border border-emerald-500/10">
                        <Heart className="w-8 h-8 text-emerald-400" />
                    </div>
                    <h1 className="text-3xl font-bold text-white mb-1 tracking-tight">Create Account</h1>
                    <p className="text-slate-400 text-sm">Join SymptoMap for personalized health insights</p>
                </div>

                {/* Card */}
                <div className="bg-slate-800/40 backdrop-blur-2xl border border-slate-700/50 rounded-3xl p-8 shadow-2xl relative">
                    <div className="absolute top-0 left-8 right-8 h-px bg-gradient-to-r from-transparent via-emerald-500/40 to-transparent" />

                    <form onSubmit={handleSubmit} className="space-y-4">
                        {/* Name + Email row */}
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-slate-300 mb-1.5">Full Name</label>
                                <div className="relative group">
                                    <User className="absolute left-3.5 top-1/2 -translate-y-1/2 w-[18px] h-[18px] text-slate-500 group-focus-within:text-emerald-400 transition-colors" />
                                    <input
                                        name="full_name"
                                        type="text"
                                        value={formData.full_name}
                                        onChange={handleChange}
                                        className="w-full bg-slate-900/60 border border-slate-600/50 rounded-xl py-2.5 pl-11 pr-4 text-white placeholder-slate-500 focus:ring-2 focus:ring-emerald-500/40 focus:border-emerald-500/50 transition-all outline-none text-sm"
                                        placeholder="Your name"
                                        required
                                    />
                                </div>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-slate-300 mb-1.5">Email</label>
                                <div className="relative group">
                                    <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-[18px] h-[18px] text-slate-500 group-focus-within:text-emerald-400 transition-colors" />
                                    <input
                                        name="email"
                                        type="email"
                                        value={formData.email}
                                        onChange={handleChange}
                                        className="w-full bg-slate-900/60 border border-slate-600/50 rounded-xl py-2.5 pl-11 pr-4 text-white placeholder-slate-500 focus:ring-2 focus:ring-emerald-500/40 focus:border-emerald-500/50 transition-all outline-none text-sm"
                                        placeholder="you@email.com"
                                        required
                                    />
                                </div>
                            </div>
                        </div>

                        {/* Phone */}
                        <div>
                            <label className="block text-sm font-medium text-slate-300 mb-1.5">Phone Number</label>
                            <div className="relative group">
                                <Phone className="absolute left-3.5 top-1/2 -translate-y-1/2 w-[18px] h-[18px] text-slate-500 group-focus-within:text-emerald-400 transition-colors" />
                                <input
                                    name="phone"
                                    type="tel"
                                    value={formData.phone}
                                    onChange={handleChange}
                                    className="w-full bg-slate-900/60 border border-slate-600/50 rounded-xl py-2.5 pl-11 pr-4 text-white placeholder-slate-500 focus:ring-2 focus:ring-emerald-500/40 focus:border-emerald-500/50 transition-all outline-none text-sm"
                                    placeholder="+91 99999 99999"
                                    required
                                />
                            </div>
                        </div>

                        {/* Password */}
                        <div>
                            <label className="block text-sm font-medium text-slate-300 mb-1.5">Password</label>
                            <div className="relative group">
                                <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-[18px] h-[18px] text-slate-500 group-focus-within:text-emerald-400 transition-colors" />
                                <input
                                    name="password"
                                    type={showPassword ? 'text' : 'password'}
                                    value={formData.password}
                                    onChange={handleChange}
                                    className="w-full bg-slate-900/60 border border-slate-600/50 rounded-xl py-2.5 pl-11 pr-12 text-white placeholder-slate-500 focus:ring-2 focus:ring-emerald-500/40 focus:border-emerald-500/50 transition-all outline-none text-sm"
                                    placeholder="Min 8 chars, uppercase, number, symbol"
                                    required
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 transition-colors"
                                >
                                    {showPassword ? <EyeOff className="w-[18px] h-[18px]" /> : <Eye className="w-[18px] h-[18px]" />}
                                </button>
                            </div>

                            {/* Password strength meter */}
                            {formData.password && (
                                <div className="mt-2.5 space-y-1.5">
                                    <div className="flex gap-1 h-1.5">
                                        {[...Array(4)].map((_, i) => (
                                            <div
                                                key={i}
                                                className={`flex-1 rounded-full transition-all duration-500 ${i < Math.ceil(passwordStrength.score / 25)
                                                    ? getStrengthColor(passwordStrength.score)
                                                    : 'bg-slate-700/50'
                                                    }`}
                                            />
                                        ))}
                                    </div>
                                    <div className="flex items-center justify-between">
                                        <span className={`text-xs ${passwordStrength.valid ? 'text-emerald-400' : 'text-slate-400'}`}>
                                            {passwordStrength.valid
                                                ? `✓ ${getStrengthLabel(passwordStrength.score)} password`
                                                : passwordStrength.message}
                                        </span>
                                        {passwordStrength.valid && <Check className="w-3.5 h-3.5 text-emerald-400" />}
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Error message */}
                        {error && (
                            <div className="flex items-start gap-2.5 p-3.5 bg-red-500/10 border border-red-500/20 rounded-xl text-sm">
                                <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
                                <div>
                                    <span className="text-red-400">{error}</span>
                                    {error.includes('already exists') && (
                                        <Link to="/user/login" className="block mt-1.5 text-emerald-400 hover:text-emerald-300 font-medium transition-colors text-xs">
                                            → Go to Login instead
                                        </Link>
                                    )}
                                </div>
                            </div>
                        )}

                        {/* Submit */}
                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-semibold py-3.5 px-4 rounded-xl transition-all duration-200 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed group shadow-lg shadow-emerald-600/20 hover:shadow-emerald-500/30 mt-1"
                        >
                            {isLoading ? (
                                <Loader2 className="w-5 h-5 animate-spin" />
                            ) : (
                                <>Create Account <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" /></>
                            )}
                        </button>
                    </form>

                    {/* Divider */}
                    <div className="flex items-center gap-3 my-6">
                        <div className="flex-1 h-px bg-slate-700/50" />
                        <span className="text-xs text-slate-500 uppercase tracking-wider">already registered?</span>
                        <div className="flex-1 h-px bg-slate-700/50" />
                    </div>

                    {/* Login link */}
                    <Link
                        to="/user/login"
                        className="block w-full text-center py-3 border border-slate-600/50 hover:border-emerald-500/30 rounded-xl text-slate-300 hover:text-emerald-400 transition-all text-sm font-medium hover:bg-emerald-500/5"
                    >
                        Sign in to your account
                    </Link>
                </div>

                {/* Footer */}
                <div className="mt-8 flex justify-center gap-6 text-xs text-slate-500">
                    <Link to="/register/doctor" className="hover:text-slate-300 transition-colors flex items-center gap-1">
                        Doctor Registration →
                    </Link>
                    <Link to="/" className="hover:text-slate-300 transition-colors">
                        Back to Home
                    </Link>
                </div>
            </div>
        </div>
    );
};

export default RegisterPage;
