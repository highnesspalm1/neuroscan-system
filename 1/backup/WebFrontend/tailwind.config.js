/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // NeuroScan Brand Colors (matching desktop app)
        primary: {
          50: '#e6fffe',
          100: '#ccfffc',
          200: '#99fff9',
          300: '#66fff6',
          400: '#33fff3',
          500: '#00E5FF',  // Main brand color
          600: '#00b8cc',
          700: '#008a99',
          800: '#005c66',
          900: '#002e33',
        },
        accent: {
          50: '#f0fff4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#39FF14',  // Neon green accent
          600: '#16a34a',
          700: '#15803d',
          800: '#166534',
          900: '#14532d',
        },
        dark: {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#111820',  // Main dark background
          950: '#0c1015',
        }
      },
      fontFamily: {
        'inter': ['Inter', 'sans-serif'],
      },
      backdropBlur: {
        'xs': '2px',
      },
      animation: {
        'pulse-soft': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        glow: {
          'from': { boxShadow: '0 0 20px rgba(0, 229, 255, 0.3)' },
          'to': { boxShadow: '0 0 30px rgba(0, 229, 255, 0.6)' },
        }
      },
      backgroundImage: {
        'glassmorphism': 'linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%)',
        'glassmorphism-dark': 'linear-gradient(135deg, rgba(17, 24, 32, 0.8) 0%, rgba(17, 24, 32, 0.4) 100%)',
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
      },
    },
  },
  plugins: [
    function({ addUtilities }) {
      const newUtilities = {
        '.glass': {
          background: 'rgba(17, 24, 32, 0.7)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          borderRadius: '16px',
        },
        '.glass-light': {
          background: 'rgba(255, 255, 255, 0.1)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          borderRadius: '16px',
        },
        '.glass-card': {
          background: 'rgba(17, 24, 32, 0.8)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(0, 229, 255, 0.2)',
          borderRadius: '20px',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
        },
        '.neon-border': {
          border: '1px solid rgba(0, 229, 255, 0.5)',
          boxShadow: '0 0 20px rgba(0, 229, 255, 0.3)',
        },
        '.neon-text': {
          textShadow: '0 0 10px rgba(0, 229, 255, 0.8)',
        }
      }
      addUtilities(newUtilities)
    }
  ],
}
