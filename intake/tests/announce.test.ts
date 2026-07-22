import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { announcePage, setDocumentTitle } from '../src/views/announce'

// The tests run in node: stub the one document property the module touches.
// The React glue (effect timing, ref attachment) is exercised in the browser.
const stubDocument = () => {
  const doc = { title: 'Untouched | Anika Legal' }
  vi.stubGlobal('document', doc)
  return doc
}

const makeHeading = () => {
  const heading = { focus: vi.fn() }
  return heading as unknown as HTMLElement & { focus: ReturnType<typeof vi.fn> }
}

describe('announce', () => {
  let doc: { title: string }

  beforeEach(() => {
    doc = stubDocument()
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('sets the document title with the site suffix', () => {
    setDocumentTitle('Contact us')
    expect(doc.title).toBe('Contact us | Anika Legal')
  })

  it('announces a page: title plus focus on the heading', () => {
    const heading = makeHeading()
    announcePage('Page not found', heading)
    expect(doc.title).toBe('Page not found | Anika Legal')
    expect(heading.focus).toHaveBeenCalledTimes(1)
  })

  it('does nothing for an empty title (view rendered nothing)', () => {
    const heading = makeHeading()
    announcePage('', heading)
    expect(doc.title).toBe('Untouched | Anika Legal')
    expect(heading.focus).not.toHaveBeenCalled()
  })

  it('still sets the title when the heading is not rendered', () => {
    expect(() => announcePage('Contact us', null)).not.toThrow()
    expect(doc.title).toBe('Contact us | Anika Legal')
  })
})
