/**
 * SymptoMap Authentication Service
 * Handles JWT tokens, refresh, and secure authentication
 */

import axios, { AxiosInstance, InternalAxiosRequestConfig, AxiosError } from 'axios';

const API_URL = (import.meta as any).env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Token storage keys
const ACCESS_TOKEN_KEY = 'symptomap_access_token';
const USER_KEY = 'symptomap_user';

// Types
export interface User {
    id: string;
    email: string;
    full_name: string;
    role: 'doctor' | 'admin' | 'patient' | 'public';
    mfa_enabled?: boolean;
}

export interface LoginCredentials {
    email: string;
    password: string;
    mfa_code?: string;
}

export interface RegisterData {
    email: string;
    password: string;
    full_name: string;
    phone?: string;
    role?: string;
}

export interface AuthResponse {
    access_token: string;
    refresh_token?: string;
    token_type: string;
    expires_in: number;
    user: User;
}

export interface MFASetupResponse {
    secret: string;
    qr_uri: string;
    backup_codes: string[];
}

// Create axios instance with interceptors
const createAuthenticatedClient = (): AxiosInstance => {
    const client = axios.create({
        baseURL: API_URL,
        timeout: 30000,
        withCredentials: true, // Send cookies for refresh token
        headers: {
            'Content-Type': 'application/json',
        },
    });

    // Request interceptor - add auth token
    client.interceptors.request.use(
        (config: InternalAxiosRequestConfig) => {
            const token = localStorage.getItem(ACCESS_TOKEN_KEY);
            if (token && config.headers) {
                config.headers.Authorization = `Bearer ${token}`;
            }
            return config;
        },
        (error) => Promise.reject(error)
    );

    // Response interceptor - handle 401 and refresh token
    client.interceptors.response.use(
        (response) => response,
        async (error: AxiosError) => {
            const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

            // If 401 and not already retrying
            if (error.response?.status === 401 && !originalRequest._retry) {
                originalRequest._retry = true;

                try {
                    // Try to refresh the token
                    const refreshed = await AuthService.refreshToken();
                    if (refreshed) {
                        // Retry original request with new token
                        const token = localStorage.getItem(ACCESS_TOKEN_KEY);
                        if (originalRequest.headers) {
                            originalRequest.headers.Authorization = `Bearer ${token}`;
                        }
                        return client(originalRequest);
                    }
                } catch (refreshError) {
                    // Refresh failed, logout user
                    AuthService.logout();
                    window.location.href = '/login';
                }
            }

            return Promise.reject(error);
        }
    );

    return client;
};

export const authClient = createAuthenticatedClient();

// Auth Service
export const AuthService = {
    /**
     * Register a new user
     */
    register: async (data: RegisterData): Promise<{ success: boolean; message: string }> => {
        try {
            const response = await axios.post(`${API_URL}/auth/register`, data);
            return { success: true, message: response.data.message };
        } catch (error: any) {
            const message = error.response?.data?.detail || 'Registration failed';
            throw new Error(message);
        }
    },

    /**
     * Login with email and password
     */
    login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
        try {
            // OAuth2 form data format
            const formData = new URLSearchParams();
            formData.append('username', credentials.email);
            formData.append('password', credentials.password);
            if (credentials.mfa_code) {
                formData.append('scope', credentials.mfa_code);
            }

            const response = await axios.post(`${API_URL}/auth/login`, formData, {
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                withCredentials: true,
            });

            const authData: AuthResponse = response.data;

            // Store tokens and user
            localStorage.setItem(ACCESS_TOKEN_KEY, authData.access_token);
            localStorage.setItem(USER_KEY, JSON.stringify(authData.user));

            return authData;
        } catch (error: any) {
            // Check if MFA is required
            if (error.response?.headers?.['x-mfa-required'] === 'true') {
                throw new Error('MFA_REQUIRED');
            }

            const message = error.response?.data?.detail || 'Login failed';
            throw new Error(message);
        }
    },

    /**
     * Refresh the access token
     */
    refreshToken: async (): Promise<boolean> => {
        try {
            const response = await axios.post(
                `${API_URL}/auth/refresh`,
                {},
                { withCredentials: true }
            );

            const authData: AuthResponse = response.data;
            localStorage.setItem(ACCESS_TOKEN_KEY, authData.access_token);
            localStorage.setItem(USER_KEY, JSON.stringify(authData.user));

            return true;
        } catch (error) {
            return false;
        }
    },

    /**
     * Logout user
     */
    logout: async (): Promise<void> => {
        try {
            await authClient.post('/auth/logout');
        } catch (error) {
            // Ignore logout errors
        } finally {
            localStorage.removeItem(ACCESS_TOKEN_KEY);
            localStorage.removeItem(USER_KEY);
        }
    },

    /**
     * Get current user from storage
     */
    getCurrentUser: (): User | null => {
        const userJson = localStorage.getItem(USER_KEY);
        if (userJson) {
            try {
                return JSON.parse(userJson);
            } catch {
                return null;
            }
        }
        return null;
    },

    /**
     * Get current user from API
     */
    getMe: async (): Promise<User> => {
        const response = await authClient.get('/auth/me');
        return response.data;
    },

    /**
     * Check if user is authenticated
     */
    isAuthenticated: (): boolean => {
        return !!localStorage.getItem(ACCESS_TOKEN_KEY);
    },

    /**
     * Get access token
     */
    getToken: (): string | null => {
        return localStorage.getItem(ACCESS_TOKEN_KEY);
    },

    /**
     * Change password
     */
    changePassword: async (currentPassword: string, newPassword: string): Promise<void> => {
        await authClient.post('/auth/change-password', {
            current_password: currentPassword,
            new_password: newPassword,
        });
    },

    /**
     * Request password reset
     */
    requestPasswordReset: async (email: string): Promise<void> => {
        await axios.post(`${API_URL}/auth/forgot-password`, { email });
    },

    /**
     * Reset password with token
     */
    resetPassword: async (token: string, newPassword: string): Promise<void> => {
        await axios.post(`${API_URL}/auth/reset-password`, {
            token,
            new_password: newPassword,
        });
    },

    // ==========================================
    // MFA Methods
    // ==========================================

    /**
     * Setup MFA - returns QR code and backup codes
     */
    setupMFA: async (): Promise<MFASetupResponse> => {
        const response = await authClient.post('/auth/mfa/setup');
        return response.data;
    },

    /**
     * Verify MFA setup with TOTP code
     */
    verifyMFASetup: async (code: string): Promise<void> => {
        await authClient.post('/auth/mfa/verify', { code });
    },

    /**
     * Disable MFA
     */
    disableMFA: async (code: string): Promise<void> => {
        await authClient.post('/auth/mfa/disable', { code });
    },
};

// Password validation utility (matching backend rules)
export const validatePassword = (password: string): { valid: boolean; message: string; score: number } => {
    let score = 0;
    const issues: string[] = [];

    // Length check
    if (password.length < 12) {
        issues.push('At least 12 characters');
    } else if (password.length >= 16) {
        score += 30;
    } else {
        score += 20;
    }

    // Uppercase
    if (/[A-Z]/.test(password)) {
        score += 15;
    } else {
        issues.push('Add uppercase letter');
    }

    // Lowercase
    if (/[a-z]/.test(password)) {
        score += 15;
    } else {
        issues.push('Add lowercase letter');
    }

    // Numbers
    if (/\d/.test(password)) {
        score += 15;
    } else {
        issues.push('Add number');
    }

    // Special characters
    if (/[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\;'`~]/.test(password)) {
        score += 20;
    } else {
        issues.push('Add special character');
    }

    // No repeated characters
    if (!/(.)\1{3,}/.test(password)) {
        score += 5;
    }

    const valid = issues.length === 0 && score >= 60;
    const message = issues.length > 0 ? issues.join(', ') : 'Strong password';

    return { valid, message, score };
};

export default AuthService;
