import { Head, Link, useForm } from '@inertiajs/react'
import type { FormEvent } from 'react'
import { button, card, field } from '@/js/ui'

export default function Register() {
  const { data, setData, post, processing, errors, reset } = useForm({
    full_name: '',
    username: '',
    email: '',
    password: '',
  })

  function submit(event: FormEvent) {
    event.preventDefault()
    post('/register', {
      onFinish: () => reset('password'),
    })
  }

  return (
    <>
      <Head title="Create account" />

      <form className={card} onSubmit={submit} noValidate>
        <h1 className="text-2xl font-semibold tracking-tight">Create your account</h1>

        <label className={field.wrap}>
          <span className={field.label}>
            Name <small className={field.hint}>optional</small>
          </span>
          <input
            className={field.input}
            value={data.full_name}
            onChange={(event) => setData('full_name', event.target.value)}
            autoComplete="name"
            autoFocus
          />
          {errors.full_name && <em className={field.error}>{errors.full_name}</em>}
        </label>

        <label className={field.wrap}>
          <span className={field.label}>Username</span>
          <input
            className={field.input}
            value={data.username}
            onChange={(event) => setData('username', event.target.value)}
            autoComplete="username"
          />
          {errors.username && <em className={field.error}>{errors.username}</em>}
        </label>

        <label className={field.wrap}>
          <span className={field.label}>Email</span>
          <input
            type="email"
            className={field.input}
            value={data.email}
            onChange={(event) => setData('email', event.target.value)}
            autoComplete="email"
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
            autoComplete="new-password"
          />
          {errors.password && <em className={field.error}>{errors.password}</em>}
          <small className={field.hint}>At least 8 characters.</small>
        </label>

        <button type="submit" className={button.solid} disabled={processing}>
          {processing ? 'Creating…' : 'Create account'}
        </button>

        <p className="text-sm text-zinc-600 dark:text-zinc-400">
          Already have an account?{' '}
          <Link href="/login" className="underline underline-offset-4 hover:text-brand">
            Sign in
          </Link>
          .
        </p>
      </form>
    </>
  )
}
