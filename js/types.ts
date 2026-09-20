import type { Page } from '@inertiajs/core'
import type { ResolvedComponent } from '@inertiajs/vue3'

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
  app_name: string
  auth: { user: AuthUser | null }
  errors: Record<string, string>
  flash: { success: string | null; error: string | null }
  [key: string]: unknown
}

/**
 * A page module, as `import.meta.glob` hands it back.
 *
 * `default` is the Vue component. `layout` is what the entry reads to wrap a
 * page in the shared Layout — it is typed `ResolvedComponent` because that is
 * exactly what `@inertiajs/vue3` hands `createInertiaApp`'s `resolve` callback.
 *
 * `layout` is what the entry mutates when it assigns a default, so it starts
 * out optional. Pages that set their own layout (check the shared shell first)
 * declare it here.
 */
export interface PageModule {
  default: ResolvedComponent
  layout?: (children: ResolvedComponent) => ResolvedComponent
}

export type AppPage<P = Record<string, unknown>> = Page<SharedProps & P>
