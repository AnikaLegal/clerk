import { events } from '../analytics'
import { logException } from '../utils'
import { SubmissionSaver } from './save'
import { Answers } from './types'

export interface SideEffectContext {
  answers: Answers
  saver: SubmissionSaver
}

/**
 * Effects fired when the user passes a question (keyed by question name),
 * at the same anchors as the old form: funnel analytics events, plus the
 * one-time submission create once we have the user's email.
 */
export const SIDE_EFFECTS: Record<string, (ctx: SideEffectContext) => void> = {
  EMAIL: ({ answers, saver }) => {
    events.onEligibilityComplete()
    if (answers.EMAIL) {
      saver
        .create(answers)
        .then(() => events.onFirstSave())
        .catch(logException)
    }
  },
  AVAILABILITY: () => events.onBasicDetailsComplete(),
  PROPERTY_MANAGER_INTRO: () => events.onIssueDetailsComplete(),
  IMPACT_INTRO: () => events.onLandlordDetailsComplete(),
  REFERRER_TYPE: () => events.onPersonalDetailsComplete(),
}

export const runSideEffect = (questionName: string, ctx: SideEffectContext) => {
  SIDE_EFFECTS[questionName]?.(ctx)
}
