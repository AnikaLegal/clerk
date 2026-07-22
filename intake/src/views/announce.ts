import { useEffect, useRef } from 'react'

// Mirrors the title pattern of the Django page shell (intake/base.html).
export const setDocumentTitle = (title: string) => {
  document.title = `${title} | Anika Legal`
}

/**
 * Announce an SPA route swap to assistive tech. A real page load announces
 * the new page and resets the reading position for free; a React route swap
 * does neither, so exit/submitted/error views would otherwise appear silently
 * with keyboard focus dumped on <body>. Set the document title and move focus
 * to the page heading instead: attach the returned ref to the view's
 * <h1 tabIndex={-1}>. Focusing the heading places the keyboard and screen
 * reader reading position on the new content and reads the heading aloud.
 * Re-announces whenever the title changes (e.g. the no-email page swapping to
 * its success view).
 */
// The announcement itself, separated from the React glue so it can be tested
// without a DOM environment.
export const announcePage = (title: string, heading: HTMLElement | null) => {
  // An empty title means the view rendered nothing - skip the announcement.
  if (!title) return
  setDocumentTitle(title)
  heading?.focus()
}

export const useAnnouncePage = (title: string) => {
  const headingRef = useRef<HTMLHeadingElement>(null)
  useEffect(() => {
    announcePage(title, headingRef.current)
  }, [title])
  return headingRef
}
