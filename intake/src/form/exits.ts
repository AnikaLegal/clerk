import { ROUTES } from '../consts'
import { Answers } from './types'

const FORTNIGHT_MS = 14 * 24 * 60 * 60 * 1000

/**
 * Eligibility exits, ported from the old form's question `effect`s: after a
 * question is answered (on leaving its page), a matching predicate may
 * redirect the user out of the form to an exit page. Answers are persisted
 * before navigating, so returning to the form resumes mid-flow.
 */
export const EXITS: Record<string, (data: Answers) => string | undefined> = {
  ISSUES: (d) =>
    d.ISSUES === 'INELIGIBLE_COMPENSATION'
      ? ROUTES.LEGAL_SCOPE_COMPENSATION
      : undefined,
  IS_VICTORIAN_TENANT: (d) =>
    d.IS_VICTORIAN_TENANT ? undefined : ROUTES.GEOGRAPHY,
  INELIGIBLE_CHOICE: (d) =>
    d.INELIGIBLE_CHOICE ? undefined : ROUTES.INELIGIBLE_MEANS,
  // Leaving EMAIL blank routes to the no-email contact fallback.
  EMAIL: (d) => (d.EMAIL ? undefined : ROUTES.NO_EMAIL),
  REPAIRS_VCAT: (d) =>
    Array.isArray(d.REPAIRS_VCAT) &&
    (d.REPAIRS_VCAT as string[]).includes('GOTTEN_VCAT')
      ? ROUTES.INELIGIBLE_REPAIRS_GOTTEN_VCAT
      : undefined,
  REPAIRS_APPLIED_VCAT: (d) =>
    d.REPAIRS_APPLIED_VCAT ? undefined : ROUTES.INELIGIBLE_REPAIRS_APPLIED_VCAT,
  BONDS_MOVE_OUT_DATE: (d) =>
    d.BONDS_MOVE_OUT_DATE ? undefined : ROUTES.BONDS_RECOVERY,
  BOND_RTBA: (d) => (d.BOND_RTBA ? undefined : ROUTES.BONDS_RECOVERY),
  BONDS_LANDLORD_INTENTS_TO_MAKE_CLAIM: (d) =>
    d.BONDS_LANDLORD_INTENTS_TO_MAKE_CLAIM ? undefined : ROUTES.BONDS_RECOVERY,
  BONDS_HAS_LANDLORD_MADE_RTBA_APPLICATION: (d) =>
    !d.BONDS_HAS_LANDLORD_MADE_RTBA_APPLICATION ||
    d.BONDS_HAS_LANDLORD_MADE_RTBA_APPLICATION === "I don't know"
      ? ROUTES.BONDS_RECOVERY
      : undefined,
  EVICTION_RETALIATORY_IS_ALREADY_REMOVED: (d) =>
    d.EVICTION_RETALIATORY_IS_ALREADY_REMOVED
      ? ROUTES.INELIGIBLE_ALREADY_REMOVED
      : undefined,
  EVICTION_RETALIATORY_HAS_NOTICE: (d) =>
    d.EVICTION_RETALIATORY_HAS_NOTICE
      ? undefined
      : ROUTES.INELIGIBLE_NO_EVICTIONS_NOTICE,
  EVICTION_RETALIATORY_VCAT_HEARING_DATE: (d) => {
    const hearing = Date.parse(String(d.EVICTION_RETALIATORY_VCAT_HEARING_DATE))
    return hearing <= Date.now() + FORTNIGHT_MS
      ? ROUTES.INELIGIBLE_VCAT_HEARING
      : undefined
  },
}

export const getExitRoute = (
  questionName: string,
  data: Answers
): string | undefined => EXITS[questionName]?.(data)
