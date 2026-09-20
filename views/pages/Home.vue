<script setup lang="ts">
import { computed } from 'vue'
import { Head, Link, usePage } from '@inertiajs/vue3'
import type { SharedProps } from '@/types'

const props = defineProps<SharedProps>()
const { auth, appName, flash } = props

const greeting = computed(() => {
  const user = auth.user
  return user
    ? `Welcome back, ${user.full_name ?? user.username}.`
    : 'Welcome to the starter.'
})
</script>

<template>
  <Head title="Home" />

  <div class="mx-auto max-w-2xl">
    <h1 class="text-3xl font-semibold tracking-tight text-zinc-900">
      {{ appName }}
    </h1>

    <p class="mt-2 text-lg text-zinc-600">{{ greeting }}</p>

    <div class="mt-8 rounded-lg border border-zinc-200 bg-white p-6 shadow-sm">
      <p class="text-sm text-zinc-600">
        Sillo on the back, Vue on the front. Your Vue twin of the starter is
        running.
      </p>

      <Link
        href="/dashboard"
        class="mt-4 inline-block rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500"
      >
        Go to the dashboard
      </Link>
    </div>
  </div>
</template>
