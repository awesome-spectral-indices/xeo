import { defineConfig } from 'vitepress'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "xeo",
  description: "Awesome Earth Observation Instruments in Python",
  base: '/xeo/',
  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Getting Started', link: '/getting-started' },
      { text: 'API Reference', link: '/api' },
      { text: 'Tutorials', link: '/tutorials/' },
      { text: 'Contributing', link: '/contributing' },
      { text: 'Changelog', link: '/CHANGELOG' },
      { text: 'How to Cite', link: '/publications' },
      { text: 'Instrument Catalogue', link: 'https://awesome-spectral-indices.github.io/awesome-earth-observation-instruments/' },
    ],

    sidebar: {
      '/tutorials/': [
        {
          text: 'Tutorials',
          items: [
            { text: 'Overview', link: '/tutorials/' },
            { text: '01 — Getting started', link: '/tutorials/01_getting_started' },
            { text: '02 — Exploring instruments', link: '/tutorials/02_exploring_instruments' },
            { text: '03 — Spectral bands', link: '/tutorials/03_spectral_bands' },
            { text: '04 — Spectral response functions', link: '/tutorials/04_spectral_response_functions' },
            { text: '05 — Raw data and DataFrames', link: '/tutorials/05_raw_data_and_dataframe_workflows' },
            { text: '06 — Data access', link: '/tutorials/06_data_access' },
            { text: '07 — Advanced search', link: '/tutorials/07_advanced_search' },
            { text: '08 — Plotting spectral data', link: '/tutorials/08_plotting' },
          ],
        },
      ],
    },

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
