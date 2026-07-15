import { defineConfig } from 'vitepress'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "xeo",
  description: "Awesome Earth Observation Instruments in Python",
  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      { text: 'Home', link: '/' },
      { text: 'API Reference', link: '/api' },
      { text: 'Tutorials', link: '/tutorials/' },
      { text: 'Contributing', link: '/contributing' },
      { text: 'Changelog', link: '/CHANGELOG' },
      { text: 'How to Cite', link: '/publications' },
      { text: 'Instrument Catalogue', link: 'https://awesome-spectral-indices.github.io/awesome-earth-observation-instruments/' },
    ],

    socialLinks: [
      { icon: 'github', link: 'https://github.com/awesome-spectral-indices/xeo' }
    ],

    search: {
      provider: 'local'
    },

    footer: {
      message: 'Released under the MIT License.',
      copyright: 'Copyright © 2026-present David Montero Loaiza'
    }
  },
  markdown: {
    languageAlias: {
      pycon: 'python',
    },
  },
})
