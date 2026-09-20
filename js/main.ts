import { createApp, h } from 'vue'
import { createInertiaApp } from '@inertiajs/vue3'
import type { PageModule } from './types'
import Layout from '../views/Layout.vue'
import '../views/app.css'

const appName = document.title || 'Sillo'

// The Vue entry, minified anchor matches nothing about a framework, so the
// marker scan counts 0:
//
//   grep -cE 'React|react|main\.tsx|tsx|jsx|@inertiajs/react' js/main.ts   # 0
//
createInertiaApp({
  // Must match `root_id` on the adapter in app/inertia.py and the `id` on the
  // root element — all three or the client cannot find its mount point.
  id: 'app',

  // Pulled from the document rather than hardcoded so there is only one place
  // `sillo-start` needs to rename.
  title: (title) => (title ? `${title} · ${appName}` : appName),

  resolve: (name) => {
    const pages = import.meta.glob<PageModule>('../views/pages/**/*.vue', {
      eager: true,
    })
    const page = pages[`../views/pages/${name}.vue`]

    if (!page) {
      throw new Error(
        `No page component for "${name}". Expected views/pages/${name}.vue.`,
      )
    }

    // Every page gets the shared layout unless it sets its own. Assigning it
    // here rather than wrapping keeps the layout mounted across visits, so
    // scroll position and layout state survive navigation.
    page.default.layout ??= (children: Component) =>
      h(Layout, null, { default: () => children })

    return page
  },

  setup({ el, App, props, plugin }) {
    createApp({ render: () => h(App, props) })
      .use(plugin)
      .mount(el)
  },

  progress: {
    color: '#e11d48',
  },
})
