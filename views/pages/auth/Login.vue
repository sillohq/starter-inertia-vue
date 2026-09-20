<script setup lang="ts">
import { Head } from '@inertiajs/vue3'
import { useForm } from '@inertiajs/vue3'
import type { SharedProps } from '@/types'

defineProps<SharedProps>()

const form = useForm({ email: '', password: '' })

function submit() {
  form.post('/login', {
    onFinish: () => form.reset('password'),
  })
}
</script>

<template>
  <Head title="Sign in" />

  <form class="relative" @submit.prevent="submit" noValidate>
    <h1 class="text-2xl font-semibold tracking-tight text-zinc-900">
      Sign in
    </h1>
    <p class="mt-1 text-sm text-zinc-600">
      Continue where you left off. This is the Vue twin's sign-in form.
    </p>

    <label class="mt-5 block">
      <span class="text-sm font-medium text-zinc-700">Email</span>
      <input
        v-model="form.email"
        type="email"
        name="email"
        autocomplete="username"
        :class="input"
        class="mt-1 block w-full rounded-md border border-zinc-300 px-3 py-2 text-sm shadow-sm focus:border-brand focus:outline-none focus:ring-2 focus:ring-brand/10"
      />
      <em v-if="form.errors.email" class="text-sm text-red-600">
        {{ form.errors.email }}
      </em>
    </label>

    <label class="mt-4 block">
      <span class="text-sm font-medium text-zinc-700">Password</span>
      <input
        v-model="form.password"
        type="password"
        name="password"
        autocomplete="current-password"
        class="mt-1 block w-full rounded-md border border-zinc-300 px-3 py-2 text-sm shadow-sm focus:border-brand focus:outline-none focus:ring-2 focus:ring-brand/10"
      />
      <em v-if="form.errors.password" class="text-sm text-red-600">
        {{ form.errors.password }}
      </em>
    </label>

    <button
      type="submit"
      :disabled="form.processing"
      class="mt-6 w-full rounded-md bg-brand px-3 py-2 text-sm font-medium text-white shadow-sm hover:bg-brand/90 disabled:opacity-50"
    >
      {{ form.processing ? 'Signing in…' : 'Sign in' }}
    </button>

    <p class="mt-4 text-sm text-zinc-600">
      New here?{' '}
      <Link href="/register" class="font-medium text-brand underline-offset-4 hover:underline">
        Create an account
      </Link>
      .
    </p>
  </form>
</template>
