<script setup lang="ts">
import { Head } from '@inertiajs/vue3'
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
      Only signed-in users get here. It proves the protected route, the
      adapter, and the auth guard all work on the Vue twin.
    </p>

    <div class="mt-8 rounded-lg border border-zinc-200 bg-white p-6 shadow-sm">
      <p class="text-sm text-zinc-600">
        You're in, {{ auth.user?.full_name ?? auth.user?.username }}. This is
        the part of the site behind the login wall.
      </p>
    </div>
  </div>
</template>
