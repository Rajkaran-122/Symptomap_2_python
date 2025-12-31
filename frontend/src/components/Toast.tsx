import React from 'react';

interface ToastProps {
    message: string;
    type?: 'success' | 'error' | 'warning' | 'info';
    onClose?: () => void;
}

export const Toast: React.FC<ToastProps> = ({ message, type = 'info', onClose }) => {
    const backgroundColor = {
        success: 'bg-green-500',
        error: 'bg-red-500',
        warning: 'bg-yellow-500',
        info: 'bg-blue-500'
    }[type];

    const icon = {
        success: '✓',
        error: '✕',
        warning: '⚠',
        info: 'ℹ'
    }[type];

    React.useEffect(() => {
        const timer = setTimeout(() => {
            onClose?.();
        }, 5000);

        return () => clearTimeout(timer);
    }, [onClose]);

    return (
        <div className={`fixed top-4 right-4 ${backgroundColor} text-white px-6 py-3 rounded-lg shadow-lg flex items-center gap-3 animate-slide-in-right z-50`}>
            <span className="text-xl">{icon}</span>
            <span className="font-medium">{message}</span>
            {onClose && (
                <button onClick={onClose} className="ml-2 text-white hover:text-gray-200">
                    ✕
                </button>
            )}
        </div>
    );
};

interface ToastContainerProps {
    toasts: Array<{ id: string; message: string; type: 'success' | 'error' | 'warning' | 'info' }>;
    removeToast: (id: string) => void;
}

export const ToastContainer: React.FC<ToastContainerProps> = ({ toasts, removeToast }) => {
    return (
        <div className="fixed top-4 right-4 z-50 space-y-2">
            {toasts.map((toast, index) => (
                <div key={toast.id} style={{ marginTop: `${index * 70}px` }}>
                    <Toast
                        message={toast.message}
                        type={toast.type}
                        onClose={() => removeToast(toast.id)}
                    />
                </div>
            ))}
        </div>
    );
};
