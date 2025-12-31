/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe', // Ice Blue
          200: '#bfdbfe',
          300: '#93c5fd', // Sky Blue
          400: '#60a5fa',
          500: '#3b82f6', // Bright Blue
          600: '#2563eb',
          700: '#1e3a8a', // Royal Blue
          800: '#1e40af',
          900: '#0a2463', // Deep Navy
          950: '#0f172a',
        },
        gray: {
          50: '#f8fafc',
          100: '#f1f5f9', // Off white - Cards
          200: '#e2e8f0', // Dividers
          300: '#cbd5e1',
          400: '#94a3b8', // Borders
          500: '#64748b',
          600: '#475569', // Body text
          700: '#334155',
          800: '#1e293b', // Subheadings
          900: '#0f172a', // Almost black - Text
          950: '#020617',
        },
        critical: {
          DEFAULT: '#dc2626',
          bg: '#fee2e2',
        },
        warning: {
          DEFAULT: '#f59e0b',
          bg: '#fef3c7',
        },
        success: {
          DEFAULT: '#10b981',
          bg: '#d1fae5',
        },
        info: {
          DEFAULT: '#06b6d4',
          bg: '#cffafe',
        },
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      boxShadow: {
        'sm': '0 1px 2px rgba(0, 0, 0, 0.04)',
        'md': '0 4px 6px rgba(0, 0, 0, 0.05)',
        'lg': '0 10px 15px rgba(0, 0, 0, 0.08)',
        'xl': '0 20px 25px rgba(0, 0, 0, 0.10)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-in': 'fadeIn 0.5s ease-out',
        'slide-up': 'slideUp 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(100%)' },
          '100%': { transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
}

