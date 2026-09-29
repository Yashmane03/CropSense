/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        crop: {
          50: '#f2f8f3',
          100: '#e1efe3',
          200: '#c4dfc9',
          300: '#99c7a2',
          400: '#66bb6a',  // Secondary green
          500: '#388e3c',
          600: '#2e7d32',  // Primary green #2E7D32
          700: '#25632a',
          800: '#214f24',
          900: '#1b411f',
          950: '#0c2310',
        },
        earth: {
          bg: '#F5F9F3',    // Light background #F5F9F3
          card: '#FFFFFF',
          border: '#E2EAF0',
          accent: '#D97706', // Warm earthy amber
          accentHover: '#B45309',
        }
      },
    },
  },
  plugins: [],
}
