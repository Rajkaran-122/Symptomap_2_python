import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Lock, Mail, User, Phone, ArrowRight, Loader2, Check, Stethoscope, Heart, BadgeCheck, Eye, EyeOff, AlertCircle } from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import { validatePassword } from '../services/auth';
import toast from 'react-hot-toast';

const DoctorRegisterPage = () => {
    const navigate = useNavigate();
    const { register, isLoading } = useAuthStore();

    const [formData, setFormData] = useState({
        email: '',
        password: '',
        full_name: '',
        phone: '',
        role: 'doctor'
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

        let cleanPhone = formData.phone.replace(/\D/g, '');
        let formattedPhone = formData.phone.trim();
        if (cleanPhone.length > 0) {
            if (cleanPhone.length === 10 && !formattedPhone.startsWith('+')) {
                formattedPhone = '+91' + cleanPhone;
            } else if (!formattedPhone.startsWith('+')) {
                formattedPhone = '+' + cleanPhone;
            }
        }

        try {
            await register({ ...formData, phone: formattedPhone });
            toast.success('Account created! Redirecting to login...');
            setTimeout(() => navigate('/login'), 1200);
        } catch (err: any) {
            const msg = err.message || 'Registration failed';
            if (msg.toLowerCase().includes('already') || msg.toLowerCase().includes('exist') || msg.toLowerCase().includes('conflict')) {
                setError('An account with this email already exists.');
            } else {
                setError(msg);
            }
            toast.error(msg);
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
    };

    const getStrengthColor = (score: number) => {
        if (score < 40) return 'bg-red-500';
        if (score < 60) return 'bg-amber-500';
        if (score < 80) return 'bg-blue-400';
        return 'bg-emerald-500';
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 flex items-center justify-center p-4 py-8 relative overflow-hidden">
            {/* Animated background — Blue theme */}
            <div className="absolute inset-0 pointer-events-none">
                <div className="absolute top-[-20%] right-[-10%] w-[500px] h-[500px] bg-blue-500/[0.07] rounded-full blur-[100px] animate-pulse" style={{ animationDuration: '8s' }} />
                <div className="absolute bottom-[-20%] left-[-10%] w-[400px] h-[400px] bg-indigo-500/[0.07] rounded-full blur-[100px] animate-pulse" style={{ animationDuration: '6s' }} />
            </div>

            <div className="max-w-[480px] w-full relative z-10">
                {/* Header */}
                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500/20 to-indigo-500/20 mb-4 shadow-2xl shadow-blue-500/10 border border-blue-500/10">
                        <Stethoscope className="w-8 h-8 text-blue-400" />
                    </div>
                    <h1 className="text-3xl font-bold text-white mb-1 tracking-tight">Doctor Registration</h1>
                    <p className="text-slate-400 text-sm">Join SymptoMap as a healthcare professional</p>
                </div>

                {/* Card */}
                <div className="bg-slate-800/40 backdrop-blur-2xl border border-slate-700/50 rounded-3xl p-8 shadow-2xl relative">
                    <div className="absolute top-0 left-8 right-8 h-px bg-gradient-to-r from-transparent via-blue-500/40 to-transparent" />

                    <form onSubmit={handleSubmit} className="space-y-4">
                        {/* Name + Email row */}
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-slate-300 mb-1.5">Full Name</label>
                                <div className="relative group">
                                    <User className="absolute left-3.5 top-1/2 -translate-y-1/2 w-[18px] h-[18px] text-slate-500 group-focus-within:text-blue-400 transition-colors" />
                                    <input
                                        name="full_name"
                                        type="text"
                                        value={formData.full_name}
                                        onChange={handleChange}
                                        className="w-full bg-slate-900/60 border border-slate-600/50 rounded-xl py-2.5 pl-11 pr-4 text-white placeholder-slate-500 focus:ring-2 focus:ring-blue-500/40 focus:border-blue-500/50 transition-all outline-none text-sm"
                                        placeholder="Dr. Jane Smith"
                                        required
                                    />
                                </div>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-slate-300 mb-1.5">Email</label>
                                <div className="relative group">
                                    <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-[18px] h-[18px] text-slate-500 group-focus-within:text-blue-400 transition-colors" />
                                    <input
                                        name="email"
                                        type="email"
                                        value={formData.email}
                                        onChange={handleChange}
                                        className="w-full bg-slate-900/60 border border-slate-600/50 rounded-xl py-2.5 pl-11 pr-4 text-white placeholder-slate-500 focus:ring-2 focus:ring-blue-500/40 focus:border-blue-500/50 transition-all outline-none text-sm"
                                        placeholder="doctor@hospital.com"
                                        required
                                    />
                                </div>
                            </div>
                        </div>

                        {/* Phone */}
                        <div>
                            <label className="block text-sm font-medium text-slate-300 mb-1.5">Phone Number</label>
                            <div className="relative group">
                                <Phone className="absolute left-3.5 top-1/2 -translate-y-1/2 w-[18px] h-[18px] text-slate-500 group-focus-within:text-blue-400 transition-colors" />
                                <input
                                    name="phone"
                                    type="tel"
                                    value={formData.phone}
                                    onChange={handleChange}
                                    className="w-full bg-slate-900/60 border border-slate-600/50 rounded-xl py-2.5 pl-11 pr-4 text-white placeholder-slate-500 focus:ring-2 focus:ring-blue-500/40 focus:border-blue-500/50 transition-all outline-none text-sm"
                                    placeholder="+91 99999 99999"
                                    required
                                />
                            </div>
                        </div>

                        {/* Info banner */}
                        <div className="flex items-start gap-3 p-3 bg-blue-500/10 border border-blue-500/20 rounded-xl">
                            <BadgeCheck className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
                            <p className="text-xs text-blue-300 leading-relaxed">
                                Doctor accounts require admin approval before gaining full access to clinical tools.
                            </p>
                        </div>

                        {/* Password */}
                        <div>
                            <label className="block text-sm font-medium text-slate-300 mb-1.5">Password</label>
                            <div className="relative group">
                                <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-[18px] h-[18px] text-slate-500 group-focus-within:text-blue-400 transition-colors" />
                                <input
                                    name="password"
                                    type={showPassword ? 'text' : 'password'}
                                    value={formData.password}
                                    onChange={handleChange}
                                    className="w-full bg-slate-900/60 border border-slate-600/50 rounded-xl py-2.5 pl-11 pr-12 text-white placeholder-slate-500 focus:ring-2 focus:ring-blue-500/40 focus:border-blue-500/50 transition-all outline-none text-sm"
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
                                            {passwordStrength.valid ? '✓ Strong password' : passwordStrength.message}
                                        </span>
                                        {passwordStrength.valid && <Check className="w-3.5 h-3.5 text-emerald-400" />}
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Error */}
                        {error && (
                            <div className="flex items-start gap-2.5 p-3.5 bg-red-500/10 border border-red-500/20 rounded-xl text-sm">
                                <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
                                <div>
                                    <span className="text-red-400">{error}</span>
                                    {error.includes('already exists') && (
                                        <Link to="/login" className="block mt-1.5 text-blue-400 hover:text-blue-300 font-medium transition-colors text-xs">
                                            → Go to Doctor Login instead
                                        </Link>
                                    )}
                                </div>
                            </div>
                        )}

                        {/* Submit */}
                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold py-3.5 px-4 rounded-xl transition-all duration-200 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed group shadow-lg shadow-blue-600/20 hover:shadow-blue-500/30 mt-1"
                        >
                            {isLoading ? (
                                <Loader2 className="w-5 h-5 animate-spin" />
                            ) : (
                                <>Register as Doctor <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" /></>
                            )}
                        </button>
                    </form>

                    {/* Divider */}
                    <div className="flex items-center gap-3 my-6">
                        <div className="flex-1 h-px bg-slate-700/50" />
                        <span className="text-xs text-slate-500 uppercase tracking-wider">already registered?</span>
                        <div className="flex-1 h-px bg-slate-700/50" />
                    </div>

                    <Link
                        to="/login"
                        className="block w-full text-center py-3 border border-slate-600/50 hover:border-blue-500/30 rounded-xl text-slate-300 hover:text-blue-400 transition-all text-sm font-medium hover:bg-blue-500/5"
                    >
                        Sign in to your doctor account
                    </Link>
                </div>

                {/* Footer */}
                <div className="mt-8 flex justify-center gap-6 text-xs text-slate-500">
                    <Link to="/register" className="hover:text-slate-300 transition-colors flex items-center gap-1">
                        <Heart className="w-3.5 h-3.5" />Patient Registration
                    </Link>
                    <Link to="/" className="hover:text-slate-300 transition-colors">
                        Back to Home
                    </Link>
                </div>
            </div>
        </div>
    );
};

export default DoctorRegisterPage;
