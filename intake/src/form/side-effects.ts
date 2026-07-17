import { logException } from '../utils'
import { SubmissionSaver } from './save'
import { Answers } from './types'

export interface SideEffectContext {
  answers: Answers
  saver: SubmissionSaver
}

/**
 * Effects fired when the user passes a question (keyed by question name). The
 * only effect is the one-time submission create once we have the user's email
 * (so partial submissions are captured and MailChimp can send reminders);
 * funnel analytics are emitted per page from FormPage.
 */
export const SIDE_EFFECTS: Record<string, (ctx: SideEffectContext) => void> = {
  EMAIL: ({ answers, saver }) => {
    if (answers.EMAIL) {
      saver.create(answers).catch(logException)
    }
  },
}

export const runSideEffect = (questionName: string, ctx: SideEffectContext) => {
  SIDE_EFFECTS[questionName]?.(ctx)
}
