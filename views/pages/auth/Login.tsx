import { Head, Link, useForm } from '@inertiajs/react'
import type { FormEvent } from 'react'
import { button, card, field } from '@/js/ui'

export default function Login() {
  /*
   * `useForm` holds the field values, the submit state, and the errors the
   * server flashed back. `errors` here is Inertia's own — it reads the shared
   * `errors` prop that app/inertia.py populates from the session, so a failed
   * POST redirects back and the messages are simply present on the next
   * render. Nothing on this page inspects a response.
   */
  const { data, setData, post, processing, errors, reset } = useForm({
    email: '',
    password: '',
  })

  function submit(event: FormEvent) {
    event.preventDefault()
    post('/login', {
      // Never leave a password in component state after a failed attempt.
      onFinish: () => reset('password'),
    })
  }

  return (
    <>
      <Head title="Sign in" />

      <form className={card} onSubmit={submit} noValidate>
        <h1 className="text-2xl font-semibold tracking-tight">Sign in</h1>

        <label className={field.wrap}>
          <span className={field.label}>Email</span>
          <input
            type="email"
            className={field.input}
            value={data.email}
            onChange={(event) => setData('email', event.target.value)}
            autoComplete="username"
            autoFocus
          />
          {errors.email && <em className={field.error}>{errors.email}</em>}
        </label>

        <label className={field.wrap}>
          <span className={field.label}>Password</span>
          <input
            type="password"
            className={field.input}
            value={data.password}
            onChange={(event) => setData('password', event.target.value)}
            autoComplete="current-password"
          />
          {errors.password && <em className={field.error}>{errors.password}</em>}
        </label>

        <button type="submit" className={button.solid} disabled={processing}>
          {processing ? 'Signing in…' : 'Sign in'}
        </button>

        <p className="text-sm text-zinc-600 dark:text-zinc-400">
          No account yet?{' '}
          <Link href="/register" className="underline underline-offset-4 hover:text-brand">
            Create one
          </Link>
          .
        </p>
      </form>
    </>
  )
}
