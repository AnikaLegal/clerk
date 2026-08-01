import { Model, settings } from 'survey-core'
import { DefaultLightPanelless } from 'survey-core/themes'

import { LINKS } from '../consts'
import { PAGES, QUESTIONS_BY_NAME } from '../questions'
import { PHONE_MAX_LENGTH, PHONE_VALIDATOR } from './phone'
import { IntakeQuestion } from './types'
import './functions'

// Mirrors the old form's allowed upload extensions.
export const ACCEPTED_UPLOAD_TYPES = '.png,.jpg,.jpeg,.pdf,.docx'

// Name of the leading welcome page: the intro screen shown before the
// questions. It is an ordinary first page (not a SurveyJS start page), so it
// takes part in Previous / Next and browser Back / Forward like any other
// page; it simply carries no answer.
export const WELCOME_PAGE = 'WELCOME'

// Content for the WELCOME page: the welcome / intro screen shown before the
// questions begin, replacing the old standalone landing splash page.
const WELCOME_HTML = `
  <h2>Welcome to the Anika Legal intake form!</h2>
  <p>We're here to help you with your rental problem. We need to ask you a
  series of simple questions to check whether you're eligible and to understand
  your problem. This questionnaire takes approximately 10 minutes to
  complete.</p>
  <p>Before starting, please have the following ready:</p>
  <ul>
    <li>Your rental property details</li>
    <li>Your landlord's details</li>
    <li>Your agent's details, if applicable</li>
    <li>Your income</li>
  </ul>
  <p>You can have a look at our
  <a href="${LINKS.COLLECTIONS_STATEMENT}" target="_blank">Collections
  Statement</a> if you have any questions about why we need your information,
  and what we do with it.</p>
`

// Pass through the question's colCount (e.g. 2 for long choice lists that
// should render in two columns); omitted when unset so it keeps the default
// single column.
const choiceColumns = (q: IntakeQuestion): { colCount?: number } =>
  q.colCount === undefined ? {} : { colCount: q.colCount }

// Optional questions carry an "(optional)" suffix on their title so users
// know they can skip them. Conditionally-required questions (requiredIf,
// e.g. the address fields in manual mode) are left unmarked - they are
// sometimes required, and SurveyJS shows its required asterisk dynamically.
const titleFor = (q: IntakeQuestion): string | undefined =>
  q.title && !q.required && !q.requiredIf ? `${q.title} (optional)` : q.title

const toElement = (q: IntakeQuestion): Record<string, unknown> => {
  const base = {
    name: q.name,
    title: titleFor(q),
    description: q.description,
    isRequired: q.required,
    // Element-level visibility: pages can now hold several questions, so each
    // question shows/hides on its own condition within a visible page.
    visibleIf: q.visibleIf,
    // Conditional-required, e.g. the address street/suburb/postcode are only
    // required when the user is entering the address manually.
    requiredIf: q.requiredIf,
    // Conditional-enabled: when false the question renders read-only (e.g. the
    // address fields are read-only while the search box fills them).
    enableIf: q.enableIf,
    // Conditional-reset: clears the value when the expression becomes true.
    resetValueIf: q.resetValueIf,
  }
  switch (q.type) {
    case 'DISPLAY':
      // html questions hold no value, so they never appear in survey.data.
      return {
        type: 'html',
        name: q.name,
        html: q.html ?? '',
        visibleIf: q.visibleIf,
      }
    case 'TEXT':
      return q.multiline
        ? { ...base, type: 'comment', autoGrow: true, maxLength: q.maxLength }
        : {
            ...base,
            type: 'text',
            placeholder: q.placeholder,
            maxLength: q.maxLength,
            validators: q.validators,
          }
    case 'NUMBER':
      return {
        ...base,
        type: 'text',
        inputType: 'number',
        min: q.min,
        max: q.max,
        validators: [
          { type: 'numeric', minValue: q.min, maxValue: q.max },
          ...(q.validators ?? []),
        ],
      }
    case 'EMAIL':
      return {
        ...base,
        type: 'text',
        inputType: 'email',
        maxLength: q.maxLength,
        validators: [{ type: 'email' }, ...(q.validators ?? [])],
      }
    case 'PHONE':
      return {
        ...base,
        type: 'text',
        inputType: 'tel',
        maxLength: PHONE_MAX_LENGTH,
        validators: [PHONE_VALIDATOR, ...(q.validators ?? [])],
      }
    case 'BOOLEAN':
      // A single labelled checkbox (e.g. "Enter address manually"). The title
      // is rendered as the checkbox label rather than a question heading.
      return {
        ...base,
        type: 'boolean',
        renderAs: 'checkbox',
        titleLocation: 'hidden',
        label: q.title,
      }
    case 'DATE':
      // Native date input emits the wire format (YYYY-MM-DD) directly.
      return { ...base, type: 'text', inputType: 'date' }
    case 'CHOICE_SINGLE':
      return {
        ...base,
        type: 'radiogroup',
        choices: q.choices,
        ...choiceColumns(q),
      }
    case 'CHOICE_SINGLE_TEXT':
      // With storeOthersAsComment disabled on the survey, the free text
      // replaces the choice value in survey.data - the old form's semantics.
      return {
        ...base,
        type: 'radiogroup',
        choices: q.choices,
        showOtherItem: true,
        otherText: q.placeholder ?? 'Prefer to self-describe',
        ...choiceColumns(q),
      }
    case 'CHOICE_MULTI':
      return {
        ...base,
        type: 'checkbox',
        choices: q.choices,
        ...choiceColumns(q),
      }
    case 'UPLOAD':
      return {
        ...base,
        type: 'file',
        storeDataAsText: false,
        allowMultiple: true,
        waitForUpload: true,
        acceptedTypes: ACCEPTED_UPLOAD_TYPES,
        needConfirmRemoveFile: false,
      }
  }
}

export const buildSurveyModel = (): Model => {
  // SurveyJS's built-in element animations (a visibleIf question fading/sliding
  // in, error boxes growing) have no prefers-reduced-motion handling of their
  // own, so honour the OS setting here - our page-slide already does (see
  // global.css). Guarded for the non-browser test environment.
  settings.animationEnabled = !(
    typeof window !== 'undefined' &&
    typeof window.matchMedia === 'function' &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches
  )
  const survey = new Model({
    // Questions are grouped into pages (see questions/pages.ts). A page-level
    // visibleIf skips a whole branch's pages via the built-in Next/Previous
    // buttons; element-level visibleIf hides individual questions within a
    // visible page. Together they replace the old form's askCondition loop.
    // The leading WELCOME page holds the intro. It is an ordinary page (its
    // Next button is relabelled "Let's get started" in FormPage): it carries no
    // value, is not part of any section (so the stepper hides on it), and the
    // question flow begins on the page after it.
    pages: [
      {
        name: WELCOME_PAGE,
        elements: [{ type: 'html', name: 'WELCOME_INTRO', html: WELCOME_HTML }],
      },
      ...PAGES.map((page) => ({
        name: page.name,
        visibleIf: page.visibleIf,
        elements: page.questions.map((name) =>
          toElement(QUESTIONS_BY_NAME[name])
        ),
      })),
    ],
    showQuestionNumbers: 'off',
    // Text fragments interpolated into question copy (e.g. {RENT_IS}), so a
    // single wire question can read differently per branch. Not answers: they
    // are never serialized or persisted.
    calculatedValues: [
      {
        // Bonds users may already have moved out of the property; every other
        // branch is a current tenancy.
        name: 'RENT_IS',
        expression: "iif({ISSUES} = 'BONDS', 'is (or was)', 'is')",
      },
    ],
    // The built-in per-page progress bar is switched off - the form renders
    // its own section-based navigation around the survey (see views/FormPage).
    showProgressBar: false,
    // Auto-advance once every visible question on a page is answered (SurveyJS
    // waits for the whole page, and never fires when the last answer is a
    // checkbox, long text or file upload).
    autoAdvanceEnabled: true,
    autoAdvanceAllowComplete: false,
    // On each page change move keyboard focus to the first question, so tabbing
    // after Previous / Next continues into the new page instead of past the
    // button that was just activated.
    autoFocusFirstQuestion: true,
    // Keep answers when the user goes back and changes a branching answer;
    // serializeAnswers filters out answers from branches no longer taken.
    clearInvisibleValues: 'none',
    checkErrorsMode: 'onNextPage',
    // Show validation errors below the question's input (as on the no-email
    // form) instead of between the question title and the field.
    questionErrorLocation: 'bottom',
    // GENDER free text replaces the choice value rather than being stored
    // in a separate comment field.
    storeOthersAsComment: false,
    // Cap the "other" self-describe text (GENDER is the only such question) to
    // the gender DB column's length, so it can't overflow during processing.
    maxOthersLength: 64,
    // The design's footer reads Back / Continue; setup.ts and syncPage manage
    // the forward label per page ("Let's get started" on WELCOME).
    pagePrevText: 'Back',
    completeText: 'Submit',
    // On completion FormPage replaces the survey with its own SubmitStatus
    // splash, so this completed page is only a one-frame guard before that
    // swap. Keep it neutral - SurveyJS's default "Thank you for completing the
    // survey" would flash as success even when the submit then fails.
    completedHtml: '<h1>Submitting your answers...</h1>',
  })
  // The panelless variant of the default light theme: questions render flat on
  // the page background instead of each sitting in its own white card.
  // applyTheme writes the theme's variables as inline styles on the survey
  // root, which would override the brand-accent and contrast variables
  // global.css sets on .intake-form (they still cover the no-email splash
  // survey, which is unthemed) - so merge those same overrides into the theme.
  survey.applyTheme({
    ...DefaultLightPanelless,
    cssVariables: {
      ...DefaultLightPanelless.cssVariables,
      '--sjs-primary-backcolor': 'var(--color-primary)',
      '--sjs-primary-backcolor-light':
        'color-mix(in oklab, var(--color-primary) 10%, transparent)',
      '--sjs-primary-forecolor': 'var(--color-primary-content)',
      '--sjs-general-forecolor-light': 'rgba(0, 0, 0, 0.6)',
    },
  })
  // Render the built-in navigation buttons (Previous / Next / Submit) as
  // daisyUI primary buttons so they match the public website. The default
  // per-button classes carry SurveyJS's own `sd-btn` styles, which outrank
  // daisyUI's low-specificity :where() rules, so clear them and keep only the
  // daisyUI classes. Previous additionally takes the outline look (white,
  // bordered - see .intake-btn-outline in global.css), so the footer reads
  // Back (secondary) then the primary action, and the forward buttons are
  // marked so both directions carry the design's sliding hover arrows (see
  // the directional-hover rules in global.css).
  survey.css = {
    navigationButton: 'd-btn d-btn-primary',
    bodyNavigationButton: '',
    navigation: {
      prev: 'intake-btn-outline',
      next: 'intake-btn-forward',
      complete: 'intake-btn-forward',
      start: '',
      preview: '',
      edit: '',
    },
  }
  // Allow inline HTML (links etc) in question titles and descriptions.
  survey.onTextMarkdown.add((_, options) => {
    if (options.text.includes('<')) {
      options.html = options.text
    }
  })
  return survey
}
