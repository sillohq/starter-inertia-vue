<script setup lang="ts">
import { Head } from '@inertiajs/vue3'
import { Link } from '@inertiajs/vue3'
import type { SharedProps } from '@/types'

defineProps<SharedProps>()
</script>

<template>
  <Head title="Dashboard" />

  <div class="mx-auto max-w-2xl">
    <h1 class="text-3xl font-semibold tracking-tight text-zinc-900">
      Dashboard
    </h1>

    <p class="mt-2 text-lg text-zinc-600">
      This is your dashboard. Only signed-in users can see it.
    </p>

    <div class="mt-8 rounded-lg border border-zinc-200 bg-white p-6 shadow-sm">
      <p class="text-sm text-zinc-600">You're on the Vue twin's dashboard.</p>

      <Link
        href="/"
        class="mt-4 inline-block rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500"
      >
        Back home
      </Link>
    </div>
  </div>
</template>
