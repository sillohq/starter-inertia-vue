<script setup lang="ts">
import { Link } from '@inertiajs/vue3'
import type { SharedProps } from '@/types'

const props = defineProps<SharedProps>()

const navLinks = [
  { href: '/', label: 'Home' },
  { href: '/dashboard', label: 'Dashboard', requiresAuth: true },
]
</script>

<template>
  <div class="min-h-screen bg-zinc-50">
    <header class="border-b border-zinc-200 bg-white">
      <div class="mx-auto flex h-16 max-w-5xl items-center justify-between px-4">
        <Link href="/" class="text-lg font-semibold text-zinc-900">
          {{ props.appName }}
        </Link>

        <nav class="flex items-center gap-4">
          <template v-for="link in navLinks" :key="link.href">
            <Link
              v-if="!link.requiresAuth || props.auth.user"
              :href="link.href"
              class="text-sm font-medium text-zinc-600 hover:text-zinc-900"
            >
              {{ link.label }}
            </Link>
          </template>

          <template v-if="props.auth.user">
            <Link
              href="/logout"
              method="post"
              as="button"
              class="text-sm font-medium text-zinc-600 hover:text-zinc-900"
            >
              Log out
            </Link>
          </template>

          <template v-else>
            <Link
              href="/login"
              class="text-sm font-medium text-zinc-600 hover:text-zinc-900"
            >
              Log in
            </Link>
            <Link
              href="/register"
              class="rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-indigo-500"
            >
              Register
            </Link>
          </template>
        </nav>
      </div>
    </header>

    <main class="mx-auto max-w-5xl px-4 py-8">
      <template v-if="props.flash.success">
        <div
          class="mb-4 rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800"
        >
          {{ props.flash.success }}
        </div>
      </template>

      <slot />
    </main>
  </div>
</template>
