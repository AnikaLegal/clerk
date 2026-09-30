import { FormStatus } from './section-nav'

// What the collapsed navigation bar says when the section list is folded
// away: the section the user is in, and where it sits in the form. Both are
// blank outside the sectioned flow, where the bar is not shown.
export const summariseNav = (
  status: FormStatus
): { title: string; subtitle: string } => {
  const current = status.sections.find((s) => s.state === 'current')
  if (!current) return { title: '', subtitle: '' }
  return {
    title: current.label,
    subtitle: `Section ${current.index + 1} of ${status.sectionCount}`,
  }
}
