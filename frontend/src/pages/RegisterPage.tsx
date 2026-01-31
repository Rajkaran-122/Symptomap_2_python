import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Lock, Mail, User, Phone, ArrowRight, Loader2, Check, X } from 'lucide-react';
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
        role: 'patient' // Default role
    });

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

        if (!passwordStrength.valid) {
            toast.error('Please choose a stronger password');
            return;
        }

        try {
            await register(formData);
            toast.success('Registration successful! Please verify your email.');
            navigate('/login');
        } catch (err: any) {
            toast.error(err.message || 'Registration failed');
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        setFormData(prev => ({
            ...prev,
            [e.target.name]: e.target.value
        }));
    };

    const getStrengthColor = (score: number) => {
        if (score < 40) return 'bg-red-500';
        if (score < 60) return 'bg-yellow-500';
        if (score < 80) return 'bg-blue-500';
        return 'bg-green-500';
    };

    return (
        <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4 py-8">
            {/* Background effects */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-blue-500/10 blur-[120px] rounded-full" />
                <div className="absolute bottom-0 left-0 w-[500px] h-[500px] bg-purple-500/10 blur-[120px] rounded-full" />
            </div>

            <div className="max-w-md w-full relative z-10">
                <div className="text-center mb-8">
                    <h1 className="text-3xl font-bold text-white mb-2">Create Account</h1>
                    <p className="text-slate-400">Join SymptoMap network</p>
                </div>

                <div className="bg-slate-800/50 backdrop-blur-xl border border-slate-700 rounded-2xl p-8 shadow-2xl">
                    <form onSubmit={handleSubmit} className="space-y-5">
                        {/* Full Name */}
                        <div>
                            <label className="block text-sm font-medium text-slate-300 mb-1.5">
                                Full Name
                            </label>
                            <div className="relative">
                                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                                <input
                                    name="full_name"
                                    type="text"
                                    value={formData.full_name}
                                    onChange={handleChange}
                                    className="w-full bg-slate-900/50 border border-slate-600 rounded-lg py-2.5 pl-10 pr-4 text-white placeholder-slate-500 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                                    placeholder="John Doe"
                                    required
                                />
                            </div>
                        </div>

                        {/* Email */}
                        <div>
                            <label className="block text-sm font-medium text-slate-300 mb-1.5">
                                Email Address
                            </label>
                            <div className="relative">
                                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                                <input
                                    name="email"
                                    type="email"
                                    value={formData.email}
                                    onChange={handleChange}
                                    className="w-full bg-slate-900/50 border border-slate-600 rounded-lg py-2.5 pl-10 pr-4 text-white placeholder-slate-500 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                                    placeholder="you@example.com"
                                    required
                                />
                            </div>
                        </div>

                        {/* Phone */}
                        <div>
                            <label className="block text-sm font-medium text-slate-300 mb-1.5">
                                Phone Number (Optional)
                            </label>
                            <div className="relative">
                                <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                                <input
                                    name="phone"
                                    type="tel"
                                    value={formData.phone}
                                    onChange={handleChange}
                                    className="w-full bg-slate-900/50 border border-slate-600 rounded-lg py-2.5 pl-10 pr-4 text-white placeholder-slate-500 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                                    placeholder="+91 99999 99999"
                                />
                            </div>
                        </div>

                        {/* Role Selection */}
                        <div>
                            <label className="block text-sm font-medium text-slate-300 mb-1.5">
                                I am a...
                            </label>
                            <select
                                name="role"
                                value={formData.role}
                                onChange={handleChange}
                                className="w-full bg-slate-900/50 border border-slate-600 rounded-lg py-2.5 px-4 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                            >
                                <option value="patient">General User (Patient)</option>
                                <option value="doctor">Doctor / Healthcare Professional</option>
                            </select>
                        </div>

                        {/* Password */}
                        <div>
                            <label className="block text-sm font-medium text-slate-300 mb-1.5">
                                Password
                            </label>
                            <div className="relative mb-2">
                                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                                <input
                                    name="password"
                                    type="password"
                                    value={formData.password}
                                    onChange={handleChange}
                                    className="w-full bg-slate-900/50 border border-slate-600 rounded-lg py-2.5 pl-10 pr-4 text-white placeholder-slate-500 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                                    placeholder="••••••••••••"
                                    required
                                />
                            </div>

                            {/* Strength Meter */}
                            {formData.password && (
                                <div className="space-y-2">
                                    <div className="flex gap-1 h-1">
                                        {[...Array(4)].map((_, i) => (
                                            <div
                                                key={i}
                                                className={`flex-1 rounded-full transition-colors duration-300 ${i < Math.floor(passwordStrength.score / 25)
                                                        ? getStrengthColor(passwordStrength.score)
                                                        : 'bg-slate-700'
                                                    }`}
                                            />
                                        ))}
                                    </div>
                                    <div className="flex items-center justify-between text-xs">
                                        <span className={`${passwordStrength.valid ? 'text-green-400' : 'text-slate-400'}`}>
                                            {passwordStrength.valid ? 'Strong password' : passwordStrength.message}
                                        </span>
                                        {passwordStrength.valid ? (
                                            <Check className="w-4 h-4 text-green-400" />
                                        ) : (
                                            <X className="w-4 h-4 text-slate-500" />
                                        )}
                                    </div>
                                </div>
                            )}
                        </div>

                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full bg-blue-600 hover:bg-blue-500 text-white font-semibold py-3 px-4 rounded-lg transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed group mt-2"
                        >
                            {isLoading ? (
                                <Loader2 className="w-5 h-5 animate-spin" />
                            ) : (
                                <>Create Account <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" /></>
                            )}
                        </button>
                    </form>

                    <div className="mt-6 text-center text-sm text-slate-400">
                        Already have an account?{' '}
                        <Link to="/login" className="text-blue-400 hover:text-blue-300 font-medium transition-colors">
                            Sign in
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default RegisterPage;
