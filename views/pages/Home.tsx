import { Head, Link, usePage } from '@inertiajs/react'
import { button } from '@/js/ui'
import type { SharedProps } from '@/js/types'

interface Props {
  message: string
}

export default function Home({ message }: Props) {
  const { auth } = usePage<SharedProps>().props

  return (
    <>
      {/* Sets document.title through the `title` callback in app.tsx. */}
      <Head title="Home" />

      <section>
        <h1 className="text-4xl font-semibold tracking-tight text-balance">
          One request, one page.
        </h1>

        <p className="mt-4 text-lg text-zinc-600 dark:text-zinc-400">{message}</p>

        <p className="mt-6 max-w-prose text-sm text-zinc-600 dark:text-zinc-400">
          This page was rendered by{' '}
          <code className="rounded border border-zinc-200 bg-zinc-100 px-1.5 py-0.5 font-mono text-[0.9em] dark:border-zinc-800 dark:bg-zinc-900">
            routes/web.py
          </code>
          . Its props came down with the document on the first visit and over XHR on every visit
          after — no API call, no loading state, no second source of truth.
        </p>

        <div className="mt-8 flex flex-wrap gap-3">
          {auth.user ? (
            <Link href="/dashboard" className={button.solid}>
              Go to your dashboard
            </Link>
          ) : (
            <>
              <Link href="/register" className={button.solid}>
                Create an account
              </Link>
              <Link href="/login" className={button.ghost}>
                Sign in
              </Link>
            </>
          )}
        </div>
      </section>
    </>
  )
}
