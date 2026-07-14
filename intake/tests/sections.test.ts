import { describe, expect, it } from 'vitest'

import { PAGES } from '../src/questions'
import { SECTIONS, sectionIndexForPage } from '../src/questions/sections'

describe('progress sections', () => {
  it('assigns every page to exactly one section, and no extras', () => {
    const inSections = SECTIONS.flatMap((s) => s.pages)
    const pageNames = PAGES.map((p) => p.name)

    // No page appears in two sections.
    expect(new Set(inSections).size).toBe(inSections.length)
    // Sections and PAGES cover exactly the same set of pages.
    expect([...inSections].sort()).toEqual([...pageNames].sort())
  })

  it('maps page names to their section index, in page order', () => {
    // Sections are contiguous chunks of the flat page order, so the section
    // index is non-decreasing as the user walks the pages.
    const indexes = PAGES.map((p) => sectionIndexForPage(p.name))
    expect(indexes).toEqual([...indexes].sort((a, b) => a - b))
    expect(Math.min(...indexes)).toBe(0)
    expect(Math.max(...indexes)).toBe(SECTIONS.length - 1)
  })

  it('returns -1 for pages outside the sectioned flow', () => {
    expect(sectionIndexForPage('WELCOME')).toBe(-1)
    expect(sectionIndexForPage(undefined)).toBe(-1)
  })
})
