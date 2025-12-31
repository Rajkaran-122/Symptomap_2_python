import { useState, useCallback } from 'react';

interface Toast {
    id: string;
    message: string;
    type: 'success' | 'error' | 'warning' | 'info';
}

/**
 * Custom hook for managing toast notifications
 * 
 * Provides methods to add and remove toasts
 */
export const useToast = () => {
    const [toasts, setToasts] = useState<Toast[]>([]);

    const addToast = useCallback((message: string, type: Toast['type'] = 'info') => {
        const id = `toast-${Date.now()}-${Math.random()}`;
        const newToast: Toast = { id, message, type };

        setToasts(prev => [...prev, newToast]);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            removeToast(id);
        }, 5000);

        return id;
    }, []);

    const removeToast = useCallback((id: string) => {
        setToasts(prev => prev.filter(toast => toast.id !== id));
    }, []);

    return { toasts, addToast, removeToast };
};
