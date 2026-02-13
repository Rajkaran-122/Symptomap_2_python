import { create } from 'zustand';
import { AuthService, User, LoginCredentials, RegisterData } from '../services/auth';

interface AuthState {
    user: User | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    error: string | null;
    mfaRequired: boolean;
    mfaEmail: string | null;

    // Actions
    login: (credentials: LoginCredentials) => Promise<void>;
    register: (data: RegisterData) => Promise<void>;
    verifyLogin: (email: string, otp: string) => Promise<void>;
    verifySignup: (email: string, otp: string) => Promise<void>;
    resendOtp: (email: string, purpose: 'signup' | 'login' | 'password_reset') => Promise<void>;

    logout: () => Promise<void>;
    checkAuth: () => Promise<void>;
    clearError: () => void;
    setMfaRequired: (required: boolean, email?: string) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
    user: AuthService.getCurrentUser(),
    isAuthenticated: AuthService.isAuthenticated(),
    isLoading: false,
    error: null,
    mfaRequired: false,
    mfaEmail: null,

    login: async (credentials) => {
        set({ isLoading: true, error: null, mfaRequired: false, mfaEmail: null });
        try {
            const response = await AuthService.login(credentials);

            // Direct login for all roles — no OTP
            set({
                user: response.user,
                isAuthenticated: true,
                isLoading: false,
                mfaRequired: false,
                mfaEmail: null
            });
        } catch (error: any) {
            set({
                error: error.message || 'Login failed',
                isLoading: false,
                isAuthenticated: false
            });
            throw error;
        }
    },

    register: async (data) => {
        set({ isLoading: true, error: null });
        try {
            await AuthService.register(data);
            set({ isLoading: false });
        } catch (error: any) {
            set({
                error: error.message || 'Registration failed',
                isLoading: false
            });
            throw error;
        }
    },

    verifyLogin: async (email, otp) => {
        set({ isLoading: true, error: null });
        try {
            const response = await AuthService.verifyLoginOtp(email, otp);
            set({
                user: response.user,
                isAuthenticated: true,
                isLoading: false,
                mfaRequired: false,
                mfaEmail: null
            });
        } catch (error: any) {
            set({
                error: error.message || 'Verification failed',
                isLoading: false
            });
            throw error;
        }
    },

    verifySignup: async (email, otp) => {
        set({ isLoading: true, error: null });
        try {
            await AuthService.verifyOtp(email, otp, 'signup');
            set({ isLoading: false });
        } catch (error: any) {
            set({
                error: error.message || 'Verification failed',
                isLoading: false
            });
            throw error;
        }
    },

    resendOtp: async (email, purpose) => {
        set({ isLoading: true, error: null });
        try {
            await AuthService.resendOtp(email, purpose);
            set({ isLoading: false });
        } catch (error: any) {
            set({
                error: error.message || 'Failed to resend OTP',
                isLoading: false
            });
            throw error;
        }
    },

    logout: async () => {
        set({ isLoading: true });
        try {
            await AuthService.logout();
        } finally {
            set({
                user: null,
                isAuthenticated: false,
                isLoading: false,
                error: null,
                mfaRequired: false,
                mfaEmail: null
            });
        }
    },

    checkAuth: async () => {
        try {
            if (AuthService.isAuthenticated()) {
                // Use stored user data from localStorage (no /auth/me endpoint needed)
                const user = AuthService.getCurrentUser();
                if (user) {
                    set({ user, isAuthenticated: true });
                } else {
                    // Token exists but no user data — clear everything
                    await AuthService.logout();
                    set({ user: null, isAuthenticated: false });
                }
            } else {
                set({ user: null, isAuthenticated: false });
            }
        } catch (error) {
            set({ user: null, isAuthenticated: false });
        }
    },

    clearError: () => set({ error: null }),

    setMfaRequired: (required, email) => set({ mfaRequired: required, mfaEmail: email || null })
}));
