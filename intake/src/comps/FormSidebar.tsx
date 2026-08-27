import { useEffect, useMemo, useState } from 'react'
import { Action, ListModel, Model, getTocRootCss } from 'survey-core'
import { List, ReactElementFactory } from 'survey-react-ui'

import { readFormStatus, SectionState } from '../form/section-nav'
import { SECTIONS } from '../questions'

interface FormSidebarProps {
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

/**
 * The form's side navigation: the questionnaire's sections (see
 * questions/sections.ts), listed on SurveyJS's own list model - the same
 * machinery its built-in table of contents uses, which gives us its list
 * markup, roles and keyboard handling while the entries, their states and where
 * they navigate stay ours.
 *
 * Each row is numbered in a circle, which carries the section's state: a tick
 * once the section is complete, a heavier ring for the one the user is in, and a
 * grey ring for a section that cannot be opened yet. A section ahead becomes
 * reachable once every page between here and its first page has been passed, so
 * a jump can never skip a question or an eligibility exit that Continue would
 * have stopped on (see form/section-nav.ts).
 */
export const FormSidebar = ({
  survey,
  visited,
  onJump,
  sent = false,
  readOnly = false,
}: FormSidebarProps) => {
  const list = useMemo(() => buildSectionList(survey, onJump), [survey, onJump])
  // The head's progress summary: whole-form percent and sections complete.
  const [meter, setMeter] = useState({
    percent: 0,
    doneCount: 0,
    sectionCount: SECTIONS.length,
  })
  // Keep the rows and the meter in step with the survey. Answering a question
  // doesn't re-render FormPage (SurveyJS renders its own questions), yet it can
  // change the section states without a page change - picking an answer that
  // triggers an eligibility exit must drop the ticks from the completed
  // sections past it there and then. So sync on the survey's own value changes
  // as well as on page changes; the rows re-render on their own (the state is
  // a SurveyJS property on each action), the meter through React state.
  useEffect(() => {
    const sync = () => {
      const { sections, percent, doneCount, sectionCount } = readFormStatus(
        survey,
        visited,
        sent
      )
      sections.forEach((status) => {
        const action = list.actions[status.index] as SectionAction
        // The marker: a complete section keeps its tick even while current -
        // jumping back into a finished section must not revert it to a number.
        action.sectionState = status.complete ? 'done' : status.state
        action.enabled =
          !readOnly && (status.state === 'current' || status.navigable)
        if (status.state === 'current') list.selectedItem = action
      })
      setMeter((prev) =>
        prev.percent === percent && prev.doneCount === doneCount
          ? prev
          : { percent, doneCount, sectionCount }
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

  return (
    <nav
      className={`intake-sidebar${readOnly ? ' intake-sidebar--readonly' : ''}`}
      aria-label="Form sections"
    >
      {/* The rail is banded like the question column: a head holding the
          progress summary, the section list, and a foot whose hairline
          continues the one above the Back / Continue buttons. The foot is
          empty for now - the save-and-finish-later action lands in it later. */}
      <div className="intake-sidebar__head">
        <span className="intake-sidebar__title">Your progress</span>
        <div
          className="intake-nav__meter"
          role="progressbar"
          aria-label="Form progress"
          aria-valuemin={0}
          aria-valuemax={100}
          aria-valuenow={meter.percent}
        >
          <div
            className="intake-nav__meter-fill"
            style={{ width: `${meter.percent}%` }}
          />
        </div>
        <span className="intake-sidebar__subtitle">
          {meter.doneCount} of {meter.sectionCount} done
        </span>
      </div>
      <div className="intake-sidebar__list">
        <div className={getTocRootCss(survey)}>
          <List model={list} />
        </div>
      </div>
      <div className="intake-sidebar__foot" />
    </nav>
  )
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
