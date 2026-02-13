import { create } from 'zustand';
import { AuthService, User, LoginCredentials, RegisterData } from '../services/auth';

interface AuthState {
    user: User | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    error: string | null;

    // Actions
    login: (credentials: LoginCredentials) => Promise<void>;
    register: (data: RegisterData) => Promise<void>;
    logout: () => Promise<void>;
    checkAuth: () => Promise<void>;
    clearError: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
    user: AuthService.getCurrentUser(),
    isAuthenticated: AuthService.isAuthenticated(),
    isLoading: false,
    error: null,

    login: async (credentials) => {
        set({ isLoading: true, error: null });
        try {
            const response = await AuthService.login(credentials);

            // Direct login for all roles — no OTP
            set({
                user: response.user,
                isAuthenticated: true,
                isLoading: false
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

    logout: async () => {
        set({ isLoading: true });
        try {
            await AuthService.logout();
        } finally {
            set({
                user: null,
                isAuthenticated: false,
                isLoading: false,
                error: null
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

    clearError: () => set({ error: null })
}));
