/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'crypto-green': '#00ff88',
        'crypto-red': '#ff4444',
        'crypto-blue': '#0088ff',
        'crypto-purple': '#8844ff',
        'dark-bg': '#0a0a0f',
        'dark-card': '#12121a',
        'dark-border': '#1f1f2e',
      },
      animation: {
        'pulse-green': 'pulse-green 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'slide-up': 'slide-up 0.3s ease-out',
      },
      keyframes: {
        'pulse-green': {
          '0%, 100%': { opacity: 1 },
          '50%': { opacity: 0.5 },
        },
        'glow': {
          'from': { boxShadow: '0 0 5px #00ff88, 0 0 10px #00ff88' },
          'to': { boxShadow: '0 0 20px #00ff88, 0 0 30px #00ff88' },
        },
        'slide-up': {
          'from': { transform: 'translateY(10px)', opacity: 0 },
          'to': { transform: 'translateY(0)', opacity: 1 },
        },
      },
    },
  },
  plugins: [],
}
