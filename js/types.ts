import type { Component, DefineComponent, VNode } from 'vue'

export interface SharedProps {
  appName: string
  auth: {
    user: {
      id: number
      name: string
      email: string
      username: string
      full_name: string | null
    } | null
  }
  errors: Record<string, string>
  flash: {
    success: string | null
    error: string | null
  }
}

export interface PageModule {
  default: DefineComponent & {
    layout?: (child: Component) => VNode
  }
  layout?: (child: Component) => VNode
}
