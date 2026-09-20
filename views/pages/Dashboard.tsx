import { Head, usePage } from '@inertiajs/react'
import type { SharedProps } from '@/js/types'

interface Props {
  stats: {
    signed_in_as: string
  }
}

export default function Dashboard({ stats }: Props) {
  const { auth } = usePage<SharedProps>().props

  return (
    <>
      <Head title="Dashboard" />

      <section className="rounded-xl border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-900">
        <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>

        <p className="mt-2 text-zinc-600 dark:text-zinc-400">
          Signed in as <strong className="font-medium text-zinc-900 dark:text-zinc-100">{stats.signed_in_as}</strong>.
        </p>

        {/*
          `auth.user` is a shared prop, resolved per request in
          app/inertia.py. It is on every page without any handler passing it,
          which is what shared props are for — and it is a hand-listed subset
          of the model, not a dump of it, so the password hash cannot reach
          the browser by someone adding a column later.
        */}
        <dl className="mt-6 grid grid-cols-[auto_1fr] gap-x-6 gap-y-2 text-sm">
          <dt className="text-zinc-500 dark:text-zinc-400">Username</dt>
          <dd>{auth.user?.username}</dd>
          <dt className="text-zinc-500 dark:text-zinc-400">Email</dt>
          <dd>{auth.user?.email}</dd>
          <dt className="text-zinc-500 dark:text-zinc-400">Name</dt>
          <dd>
            {auth.user?.full_name ?? <em className="text-zinc-500 dark:text-zinc-400">not set</em>}
          </dd>
          <dt className="text-zinc-500 dark:text-zinc-400">Staff</dt>
          <dd>{auth.user?.is_staff ? 'yes' : 'no'}</dd>
        </dl>
      </section>
    </>
  )
}
