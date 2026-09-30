import { useEffect, useMemo, useState } from 'react'
import { Action, ListModel, Model } from 'survey-core'
import { ReactElementFactory } from 'survey-react-ui'

import { summariseNav } from '../form/nav-summary'
import { readFormStatus, SectionState } from '../form/section-nav'
import { SECTIONS } from '../questions'

export interface SectionListOptions {
  survey: Model
  // Questions the user has passed, as maintained by the form (see setUpForm).
  // Together with the survey it decides each section's state.
  visited: Set<string>
  // Jumps to a section's first visible page; a no-op for a section that is not
  // currently reachable (see useFormNavigation's jumpToSection).
  onJump: (sectionIndex: number) => void
  // Whether the answers have been sent, which is what completes the final
  // Review & send section (see readFormStatus).
  sent?: boolean
  // Show the sections without offering them: on the send and confirmation
  // steps there is nowhere left to navigate to.
  readOnly?: boolean
}

// What the navigation shows besides the rows: the whole-form progress and the
// current section, for the rail's head and the collapsed bar.
export interface SectionSummary {
  percent: number
  doneCount: number
  sectionCount: number
  title: string
  subtitle: string
}

/**
 * The questionnaire's sections (see questions/sections.ts) as a SurveyJS list
 * model - the same machinery its built-in table of contents uses, which gives
 * us its list markup, roles and keyboard handling while the entries, their
 * states and where they navigate stay ours. Shared by the docked rail and the
 * narrow-screen sheet, so both read the same states.
 *
 * Each row is numbered in a circle, which carries the section's state: a tick
 * once the section is complete, a heavier ring for the one the user is in, and a
 * grey ring for a section that cannot be opened yet. A section ahead becomes
 * reachable once every page between here and its first page has been passed, so
 * a jump can never skip a question or an eligibility exit that Continue would
 * have stopped on (see form/section-nav.ts).
 */
export const useSectionList = ({
  survey,
  visited,
  onJump,
  sent = false,
  readOnly = false,
}: SectionListOptions) => {
  const list = useMemo(() => buildSectionList(survey, onJump), [survey, onJump])
  const [summary, setSummary] = useState<SectionSummary>({
    percent: 0,
    doneCount: 0,
    sectionCount: SECTIONS.length,
    title: '',
    subtitle: '',
  })
  // Keep the rows and the summary in step with the survey. Answering a question
  // doesn't re-render FormPage (SurveyJS renders its own questions), yet it can
  // change the section states without a page change - picking an answer that
  // triggers an eligibility exit must drop the ticks from the completed
  // sections past it there and then. So sync on the survey's own value changes
  // as well as on page changes; the rows re-render on their own (the state is
  // a SurveyJS property on each action), the summary through React state.
  useEffect(() => {
    const sync = () => {
      const status = readFormStatus(survey, visited, sent)
      status.sections.forEach((section) => {
        const action = list.actions[section.index] as SectionAction
        // The marker: a complete section keeps its tick even while current -
        // jumping back into a finished section must not revert it to a number.
        action.sectionState = section.complete ? 'done' : section.state
        action.enabled =
          !readOnly && (section.state === 'current' || section.navigable)
        if (section.state === 'current') list.selectedItem = action
      })
      const next = {
        percent: status.percent,
        doneCount: status.doneCount,
        sectionCount: status.sectionCount,
        ...summariseNav(status),
      }
      setSummary((prev) =>
        prev.percent === next.percent &&
        prev.doneCount === next.doneCount &&
        prev.title === next.title &&
        prev.subtitle === next.subtitle
          ? prev
          : next
      )
    }
    sync()
    survey.onValueChanged.add(sync)
    survey.onCurrentPageChanged.add(sync)
    return () => {
      survey.onValueChanged.remove(sync)
      survey.onCurrentPageChanged.remove(sync)
    }
  }, [survey, visited, list, sent, readOnly])

  return { list, summary }
}

// A list entry carrying its section's state. Held as a SurveyJS property so the
// list item re-renders when it changes.
class SectionAction extends Action {
  get sectionState(): SectionState {
    return this.getPropertyValue('sectionState') ?? 'later'
  }

  set sectionState(state: SectionState) {
    this.setPropertyValue('sectionState', state)
  }
}

// The row's content: the numbered marker (a tick once the section is done) and
// the section name. The marker is decorative - the row's own state is conveyed
// by the list item's selected / disabled state.
const SectionRow = ({ item }: { item: SectionAction }) => (
  <>
    <span
      className={`intake-nav__marker intake-nav__marker--${item.sectionState}`}
      aria-hidden="true"
    >
      {item.sectionState === 'done' ? null : Number(item.id) + 1}
    </span>
    <span className="intake-nav__label">{item.title}</span>
  </>
)

const SECTION_ROW_COMPONENT = 'intake-nav-item'
ReactElementFactory.Instance.registerElement(SECTION_ROW_COMPONENT, (props) => (
  <SectionRow {...(props as { item: SectionAction })} />
))

// One entry per section, in flow order. Mirrors the options SurveyJS builds its
// own table of contents with (see createTOCListModel): a menu of radio-like
// items, no search box, and selection driven by us rather than by clicks.
const buildSectionList = (
  survey: Model,
  onJump: (sectionIndex: number) => void
): ListModel<Action> => {
  const list = new ListModel<Action>({
    items: SECTIONS.map(
      (section, index) =>
        new SectionAction({
          id: String(index),
          title: section.label,
          component: SECTION_ROW_COMPONENT,
          action: () => onJump(index),
        })
    ),
    searchEnabled: false,
    locOwner: survey,
    listRole: 'menu',
    listItemRole: 'menuitemradio',
  })
  list.allowSelection = false
  return list
}
