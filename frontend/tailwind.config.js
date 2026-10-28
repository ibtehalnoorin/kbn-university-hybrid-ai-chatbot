/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        amethyst: {
          deep: '#24103F',
          dark: '#160B2B',
        },
        electric: {
          DEFAULT: '#8B5CF6',
          bright: '#A855F7',
        },
        lavender: {
          soft: '#D8B4FE',
        },
        mainBg: '#0F0A19',
        surface: '#1B1229',
        primaryText: '#F5F3FF',
        secondaryText: '#B8A9CC',
        borderCol: '#38264D',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
