import { createInertiaApp } from '@inertiajs/react'
import type { ReactNode } from 'react'
import { createRoot } from 'react-dom/client'
import Layout from '@/views/Layout'
import type { PageModule } from './types'
import './app.css'

const appName = document.title || 'Sillo'

createInertiaApp({
  // Must match `root_id` on the adapter in app/inertia.py and the div in
  // root.html. All three, or the client cannot find its mount point or its
  // page object.
  id: 'app',

  // Taken from the document rather than written here. The shell renders
  // `<title>{{ app_name }}</title>` before any JavaScript runs, so this
  // follows APP_NAME on its own — a hardcoded name would be a second place to
  // change, and one that `sillo-start` does not know how to rename.
  title: (title) => (title ? `${title} · ${appName}` : appName),

  // Maps the component name a handler returns — `render("auth/Login")` — onto
  // a module under ../views/pages. The glob is eager so every page is in the
  // main bundle; switch to `{ eager: false }` and `await pages[path]()` once
  // there are enough pages for code splitting to be worth the extra round
  // trip.
  //
  // The path is relative and literal on purpose: Vite resolves globs at build
  // time by reading this string, so it cannot go through the `@/` alias and
  // cannot be built from a variable.
  resolve: (name) => {
    const pages = import.meta.glob<PageModule>('../views/pages/**/*.tsx', {
      eager: true,
    })
    const page = pages[`../views/pages/${name}.tsx`]

    if (!page) {
      // Without this the failure is `Cannot read properties of undefined
      // (reading 'default')` from inside Inertia, which says nothing about
      // which component was missing.
      throw new Error(
        `No page component for "${name}". Expected views/pages/${name}.tsx.`,
      )
    }

    // Every page gets the shared layout unless it sets its own. Assigning it
    // here rather than wrapping in each page is what makes the layout persist
    // across visits: React keeps the instance mounted, so scroll position and
    // any layout state survive navigation.
    page.default.layout ??= (children: ReactNode) => <Layout>{children}</Layout>

    return page
  },

  setup({ el, App, props }) {
    createRoot(el).render(<App {...props} />)
  },

  progress: {
    color: '#e11d48',
  },
})
