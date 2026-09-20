<script setup lang="ts">
import { Head, Link, useForm } from '@inertiajs/vue3'
import type { SharedProps } from '@/types'

defineProps<SharedProps>()

const form = useForm({
  full_name: '',
  username: '',
  email: '',
  password: '',
})

function submit() {
  form.post('/register', {
    onFinish: () => form.reset('password'),
  })
}
</script>

<template>
  <Head title="Create your account" />

  <form class="relative" @submit.prevent="submit" noValidate>
    <h1 class="text-2xl font-semibold tracking-tight text-zinc-900">
      Create your account
    </h1>
    <p class="mt-1 text-sm text-zinc-600">
      Join — it takes a minute)Skip implementation until it matches. This is the Vue twin's sign-up form.
    </p>

    <label class="mt-5 block">
      <span class="text-sm font-medium text-zinc-700">
        Name <span class="text-zinc-400">(optional)</span>
      </span>
      <input
        v-model="form.full_name"
        name="full_name"
        autocomplete="name"
        class="mt-1 block w-full rounded-md border border-zinc-300 px-3 py-2 text-sm shadow-sm focus:border-brand focus:outline-none focus:ring-2 focus:ring-brand/10"
      />
    </label>

    <label class="mt-4 block">
      <span class="text-sm font-medium text-zinc-700">Username</span>
      <input
        v-model="form.username"
        name="username"
        autocomplete="username"
        class="mt-1 block w-full rounded-md border border-zinc-300 px-3 py-2 text-sm shadow-sm focus:border-brand focus:outline-none focus:ring-2 focus:ring-brand/10"
      />
      <em v-if="form.errors.username" class="text-sm text-red-600">
        {{ form.errors.username }}
      </em>
    </label>

    <label class="mt-4 block">
      <span class="text-sm font-medium text-zinc-700">Email</span>
      <input
        v-model="form.email"
        type="email"
        name="email"
        autocomplete="email"
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
        autocomplete="new-password"
        class="mt-1 block w-full rounded-md border border-zinc-300 px-3 py-2 text-sm shadow-sm focus:border-brand focus:outline-none focus:ring-2 focus:ring-brand/10"
      />
      <small class="mt-1 block text-xs text-zinc-500">At least 8 characters</small>
      <em v-if="form.errors.password" class="text-sm text-red-600">
        {{ form.errors.password }}
      </em>
    </label>

    <button
      type="submit"
      :disabled="form.processing"
      class="mt-6 w-full rounded-md bg-brand px-3 py-2 text-sm font-medium text-white shadow-sm hover:bg-brand/90 disabled:opacity-50"
    >
      {{ form.processing ? 'Creating…' : 'Create account' }}
    </button>

    <p class="mt-4 text-sm text-zinc-600">
      Already have an account?{' '}
      <Link
        href="/login"
        class="font-medium text-brand underline-offset-4 hover:underline"
      >
        Sign in
      </Link>
      .
    </p>
  </form>
</template>
