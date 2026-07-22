// Phone validation, shared by the main form's phone questions and the
// no-email contact page: an optional leading + followed by 8 to 15 digits,
// nothing else. Rejects letters, separators (spaces, hyphens, parentheses)
// and too few or too many digits.
export const PHONE_VALIDATOR = {
  type: 'regex',
  regex: '^\\+?\\d{8,15}$',
  text: "That phone number doesn't look valid. Enter digits only, like 0412345678 or +61412345678.",
}

// The longest valid value: a leading + and 15 digits. Comfortably within the
// backend's 32 character phone number columns.
export const PHONE_MAX_LENGTH = 16
