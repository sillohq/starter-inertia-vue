import { Link, router, usePage } from '@inertiajs/react'
import type { ReactNode } from 'react'
import type { SharedProps } from '@/js/types'
import { button } from '@/js/ui'

/**
 * The shell every page renders inside.
 *
 * Assigned once in app.tsx rather than wrapped around each page, which is what
 * makes it *persistent*: Inertia keeps this component mounted across visits,
 * so state in here — an open menu, a scroll position — survives navigation.
 * Wrapping each page instead remounts the layout on every visit and loses it.
 */

export default function Layout({ children }: { children: ReactNode }) {
  const { auth, app_name, flash } = usePage<SharedProps>().props

  return (
    /*
     * min-h-screen, not min-h-full: a percentage height needs an unbroken
     * chain of sized ancestors, and Inertia's mount <div> is not one — so
     * min-h-full collapsed to the content and left the footer floating
     * mid-page on anything short.
     */
    <div className="flex min-h-screen flex-col">
      <header className="flex items-center gap-4 border-b border-zinc-200 px-6 py-4 dark:border-zinc-800">
        <Link href="/" className="font-semibold tracking-tight">
          {app_name}
        </Link>

        <nav className="ml-auto flex items-center gap-4 text-sm">
          {auth.user ? (
            <>
              <Link href="/dashboard" className="hover:text-brand">
                Dashboard
              </Link>
              <span className="text-zinc-500 dark:text-zinc-400">{auth.user.username}</span>
              {/*
                A button, not a link. Signing out changes state, so it must be
                a POST — a GET can be triggered by any page that embeds the
                URL, and by prefetchers that follow links on your behalf.
              */}
              <button type="button" className={button.ghost} onClick={() => router.post('/logout')}>
                Sign out
              </button>
            </>
          ) : (
            <>
              <Link href="/login" className="hover:text-brand">
                Sign in
              </Link>
              <Link href="/register" className={button.solid}>
                Create account
              </Link>
            </>
          )}
        </nav>
      </header>

      {/* Rendered here, once, so no page has to remember to show it. */}
      {flash.success && (
        <p className="mx-6 mt-4 rounded-lg border border-emerald-600/30 bg-emerald-600/10 px-4 py-2.5 text-sm text-emerald-700 dark:text-emerald-400">
          {flash.success}
        </p>
      )}
      {flash.error && (
        <p className="mx-6 mt-4 rounded-lg border border-red-700/30 bg-red-700/10 px-4 py-2.5 text-sm text-red-700 dark:text-red-400">
          {flash.error}
        </p>
      )}

      <main className="mx-auto w-full max-w-3xl grow px-6 py-12">{children}</main>

      <footer className="border-t border-zinc-200 px-6 py-6 text-sm text-zinc-500 dark:border-zinc-800 dark:text-zinc-400">
        Built with{' '}
        <a href="https://sillo.build" className="underline underline-offset-4 hover:text-brand">
          Sillo
        </a>{' '}
        and{' '}
        <a href="https://inertiajs.com" className="underline underline-offset-4 hover:text-brand">
          Inertia
        </a>
        .
      </footer>
    </div>
  )
}
