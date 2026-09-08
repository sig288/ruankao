/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        paper: {
          50: '#fffbf4',
          100: '#f3ebdd',
          200: '#e8dcc8',
          300: '#d9c7ab',
        },
        ink: {
          50: '#eef6f2',
          100: '#dceee6',
          500: '#2d8a6a',
          600: '#1b6b52',
          700: '#1b4a3c',
          800: '#16382e',
          900: '#12241e',
        },
        pine: {
          50: '#eef6f2',
          100: '#dceee6',
          500: '#2d8a6a',
          600: '#1b6b52',
          700: '#165744',
        },
        cinnabar: {
          50: '#fdf0e8',
          100: '#f8dcc8',
          500: '#d4713a',
          600: '#c45c26',
          700: '#a44a1c',
        },
        primary: {
          50: '#eef6f2',
          100: '#dceee6',
          500: '#2d8a6a',
          600: '#1b6b52',
          700: '#165744',
        }
      },
      maxWidth: {
        phone: '28rem',
      }
    },
  },
  plugins: [],
}
