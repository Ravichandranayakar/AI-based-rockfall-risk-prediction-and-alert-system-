/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      animation: {
        'pulse-red': 'pulse-red 2s infinite',
        'fade-in': 'fadeIn 0.5s ease-in-out',
      },
      keyframes: {
        'pulse-red': {
          '0%': { boxShadow: '0 0 0 0 rgba(239, 68, 68, 0.7)' },
          '70%': { boxShadow: '0 0 0 10px rgba(239, 68, 68, 0)' },
          '100%': { boxShadow: '0 0 0 0 rgba(239, 68, 68, 0)' },
        },
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(-10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        }
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
  safelist: [
    'bg-red-100', 'bg-yellow-100', 'bg-green-100',
    'text-red-600', 'text-yellow-600', 'text-green-600',
    'text-red-800', 'text-yellow-800', 'text-green-800',
    'border-red-300', 'border-yellow-300', 'border-green-300',
  ]
}