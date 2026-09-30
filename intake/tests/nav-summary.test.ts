import { describe, expect, it } from 'vitest'

import { summariseNav } from '../src/form/nav-summary'
import { FormStatus, SectionStatus } from '../src/form/section-nav'

const section = (
  index: number,
  state: SectionStatus['state'],
  complete = state === 'done'
): SectionStatus => ({
  index,
  label: `Section ${index}`,
  state,
  complete,
  navigable: state !== 'current',
})

const status = (sections: SectionStatus[]): FormStatus => ({
  sections,
  percent: 40,
  doneCount: sections.filter((s) => s.complete).length,
  sectionCount: sections.length,
})

describe('summariseNav', () => {
  it('names the current section and its position in the form', () => {
    const summary = summariseNav(
      status([section(0, 'done'), section(1, 'current'), section(2, 'later')])
    )
    expect(summary.title).toBe('Section 1')
    expect(summary.subtitle).toBe('Section 2 of 3')
  })

  it('still names the current section once it is complete', () => {
    const summary = summariseNav(
      status([section(0, 'done'), section(1, 'current', true)])
    )
    expect(summary.title).toBe('Section 1')
    expect(summary.subtitle).toBe('Section 2 of 2')
  })

  it('is blank outside the sectioned flow', () => {
    const summary = summariseNav(status([section(0, 'later')]))
    expect(summary.title).toBe('')
    expect(summary.subtitle).toBe('')
  })
})
