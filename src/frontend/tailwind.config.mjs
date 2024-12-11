const { addIconSelectors } = require('@iconify/tailwind')

/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {},
    colors: {
      primary: '#455a63',
      'primary-text': 'white',
      secondary: '#eee',
      success: '#4D766E',
      'body-dark': '#212121',
      'text-dark': 'white',
      'primary-dark': '#454545',
      black: '#000'
    },
  },
  plugins: [addIconSelectors(['mdi'])],
  safelist: [
    'text-black'
  ]
}
