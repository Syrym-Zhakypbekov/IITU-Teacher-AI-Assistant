/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'primary-blue': '#1e40af',
        'secondary-blue': '#3b82f6',
        'accent-blue': '#60a5fa',
        'dark-navy': '#0f172a',
      },
    },
  },
  plugins: [],
}
