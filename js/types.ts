import type { Page } from '@inertiajs/core'
import type { Component } from 'vue'

/** The signed-in user, as `app/inertia.py:current_user` serialises them. */
export interface AuthUser {
  id: number
  email: string
  username: string
  full_name: string | null
  is_staff: boolean
}

/**
 * Props every page receives, from `share_globals` in app/inertia.py.
 *
 * `errors` and `flash` are always present — never optional — because the
 * Python side resolves them on every render, defaulting to an empty mapping.
 * Typing them as possibly-undefined would push a `?.` into every component
 * that reads them, for a case that cannot occur.
 */
export interface SharedProps {
  appName: string
  auth: { user: AuthUser | null }
  errors: Record<string, string>
  flash: { success: string | null; error: string | null }
  [key: string]: unknown
}

/** A page module, as `import.meta.glob` hands it back. */
export interface PageModule {
  default: Component
  layout?: (children: Component) => Component
}

export type AppPage<P = Record<string, unknown>> = Page<SharedProps & P>
