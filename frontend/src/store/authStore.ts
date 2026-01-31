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
            throw error; // Re-throw to handle MFA requirement in UI
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
                const user = await AuthService.getMe();
                set({ user, isAuthenticated: true });
            } else {
                set({ user: null, isAuthenticated: false });
            }
        } catch (error) {
            // Token might be invalid or expired
            AuthService.logout();
            set({ user: null, isAuthenticated: false });
        }
    },

    clearError: () => set({ error: null })
}));
