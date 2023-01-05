/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './groupridesapp/templates/**/*.html',
    './users/templates/**/*.html',
    './groupridesapp/**/*.py',
    './users/**/*.py',
    './static/flowbite/**/*.js'
  ],
  theme: {
    extend: {},
  },
    plugins: [
        require('flowbite/plugin')
    ]
}
