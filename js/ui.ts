/*
 * The class strings that appear on more than one page.
 *
 * Plain strings rather than components, deliberately. A `<Button>` decides
 * what a button is allowed to be, and every page then works around it; a
 * string composes — `${button.solid} w-full` — and deletes cleanly when you
 * bring your own component library.
 */

const focusRing =
  'focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand'

export const button = {
  base: `inline-flex items-center justify-center rounded-lg px-3.5 py-2 text-sm font-medium transition ${focusRing} disabled:pointer-events-none disabled:opacity-60`,
  get solid() {
    return `${this.base} bg-brand text-white hover:bg-brand-strong`
  },
  get ghost() {
    return `${this.base} border border-zinc-200 hover:bg-zinc-100 dark:border-zinc-800 dark:hover:bg-zinc-800`
  },
}

export const field = {
  /** The <label> wrapping a caption and its control. */
  wrap: 'flex flex-col gap-1.5',
  /** The caption above the control. */
  label: 'text-sm font-medium',
  /** The control itself. */
  input: `rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm ${focusRing} dark:border-zinc-800 dark:bg-zinc-900`,
  /** A validation message from the server, under the control. */
  error: 'text-sm text-red-700 not-italic dark:text-red-400',
  /** Supporting text under the control. */
  hint: 'text-xs text-zinc-500 dark:text-zinc-400',
}

/** The centred panel the auth forms sit in. */
export const card =
  'mx-auto flex w-full max-w-sm flex-col gap-4 rounded-xl border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-900'
