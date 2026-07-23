import { ROUTES } from '../consts'
import { Answers } from './types'

const DAY_MS = 24 * 60 * 60 * 1000
// A hearing this many calendar days away (or sooner) is too soon for us to
// help in time.
const URGENT_HEARING_DAYS = 14

// Whole calendar days from today until the given native-date-input value
// (YYYY-MM-DD), both taken as local dates so the result never depends on the
// time of day. NaN when the value is missing or not a real calendar date.
const daysUntil = (value: string): number => {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value)
  if (!match) return NaN
  const [, y, m, d] = match.map(Number)
  const target = new Date(y, m - 1, d)
  // Reject rolled-over values (e.g. 2026-02-31 -> 3 March).
  if (
    target.getFullYear() !== y ||
    target.getMonth() !== m - 1 ||
    target.getDate() !== d
  ) {
    return NaN
  }
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  return Math.round((target.getTime() - today.getTime()) / DAY_MS)
}

/**
 * Eligibility exits, ported from the old form's question `effect`s: after a
 * question is answered (on leaving its page), a matching predicate may
 * redirect the user out of the form to an exit page. Answers are persisted
 * before navigating, so returning to the form resumes mid-flow.
 */
export const EXITS: Record<string, (data: Answers) => string | undefined> = {
  ISSUES: (d) =>
    d.ISSUES === 'INELIGIBLE_COMPENSATION'
      ? ROUTES.INELIGIBLE_COMPENSATION
      : undefined,
  IS_VICTORIAN_TENANT: (d) =>
    d.IS_VICTORIAN_TENANT ? undefined : ROUTES.INELIGIBLE_OUTSIDE_VICTORIA,
  INELIGIBLE_CHOICE: (d) =>
    d.INELIGIBLE_CHOICE ? undefined : ROUTES.INELIGIBLE_INCOME,
  REPAIRS_VCAT: (d) =>
    Array.isArray(d.REPAIRS_VCAT) &&
    (d.REPAIRS_VCAT as string[]).includes('GOTTEN_VCAT')
      ? ROUTES.INELIGIBLE_REPAIRS_ORDER_OBTAINED
      : undefined,
  REPAIRS_APPLIED_VCAT: (d) =>
    d.REPAIRS_APPLIED_VCAT ? undefined : ROUTES.EXIT_VCAT_REPRESENTATION,
  BONDS_MOVE_OUT_DATE: (d) =>
    d.BONDS_MOVE_OUT_DATE ? undefined : ROUTES.INELIGIBLE_BOND_OUT_OF_SCOPE,
  BOND_RTBA: (d) =>
    d.BOND_RTBA ? undefined : ROUTES.INELIGIBLE_BOND_OUT_OF_SCOPE,
  BONDS_HAS_LANDLORD_MADE_RTBA_APPLICATION: (d) =>
    !d.BONDS_HAS_LANDLORD_MADE_RTBA_APPLICATION ||
    d.BONDS_HAS_LANDLORD_MADE_RTBA_APPLICATION === "I don't know"
      ? ROUTES.INELIGIBLE_BOND_OUT_OF_SCOPE
      : undefined,
  EVICTION_RETALIATORY_IS_ALREADY_REMOVED: (d) =>
    d.EVICTION_RETALIATORY_IS_ALREADY_REMOVED
      ? ROUTES.INELIGIBLE_ALREADY_EVICTED
      : undefined,
  EVICTION_RETALIATORY_HAS_NOTICE: (d) =>
    d.EVICTION_RETALIATORY_HAS_NOTICE
      ? undefined
      : ROUTES.INELIGIBLE_NO_NOTICE_TO_VACATE,
  EVICTION_RETALIATORY_VCAT_HEARING_DATE: (d) => {
    const days = daysUntil(String(d.EVICTION_RETALIATORY_VCAT_HEARING_DATE))
    // A missing or unparseable date keeps the user in the form rather than
    // ejecting them: the question is a required native date input, so a valid
    // value is the norm, and wrongly bouncing a legitimate user out of a legal
    // service is worse than letting a degenerate edge reach a paralegal.
    if (Number.isNaN(days)) return undefined
    return days <= URGENT_HEARING_DAYS
      ? ROUTES.INELIGIBLE_URGENT_HEARING
      : undefined
  },
}

export const getExitRoute = (
  questionName: string,
  data: Answers
): string | undefined => EXITS[questionName]?.(data)
