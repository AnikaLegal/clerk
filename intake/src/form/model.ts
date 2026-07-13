import { Model } from 'survey-core'

import { PAGES, QUESTIONS_BY_NAME } from '../questions'
import { IntakeQuestion } from './types'
import './functions'

// Mirrors the old form's allowed upload extensions.
export const ACCEPTED_UPLOAD_TYPES = '.png,.jpg,.jpeg,.pdf,.docx'

const toElement = (q: IntakeQuestion): Record<string, unknown> => {
  const base = {
    name: q.name,
    title: q.title,
    description: q.description,
    isRequired: q.required,
    // Element-level visibility: pages can now hold several questions, so each
    // question shows/hides on its own condition within a visible page.
    visibleIf: q.visibleIf,
  }
  switch (q.type) {
    case 'DISPLAY':
      // html questions hold no value, so they never appear in survey.data.
      return { type: 'html', name: q.name, html: q.html ?? '', visibleIf: q.visibleIf }
    case 'TEXT':
      return q.multiline
        ? { ...base, type: 'comment', autoGrow: true }
        : { ...base, type: 'text', placeholder: q.placeholder }
    case 'NUMBER':
      return {
        ...base,
        type: 'text',
        inputType: 'number',
        validators: [{ type: 'numeric' }],
      }
    case 'EMAIL':
      return {
        ...base,
        type: 'text',
        inputType: 'email',
        validators: [{ type: 'email' }],
      }
    case 'PHONE':
      // The old form validated phone numbers as non-empty and length < 16.
      return {
        ...base,
        type: 'text',
        inputType: 'tel',
        validators: [
          {
            type: 'text',
            maxLength: 15,
            text: "Hold on, that phone number doesn't look valid",
          },
        ],
      }
    case 'DATE':
      // Native date input emits the wire format (YYYY-MM-DD) directly.
      return { ...base, type: 'text', inputType: 'date' }
    case 'CHOICE_SINGLE':
      return { ...base, type: 'radiogroup', choices: q.choices }
    case 'CHOICE_SINGLE_TEXT':
      // With storeOthersAsComment disabled on the survey, the free text
      // replaces the choice value in survey.data - the old form's semantics.
      return {
        ...base,
        type: 'radiogroup',
        choices: q.choices,
        showOtherItem: true,
        otherText: q.placeholder ?? 'Prefer to self-describe',
      }
    case 'CHOICE_MULTI':
      return { ...base, type: 'checkbox', choices: q.choices }
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
  const survey = new Model({
    // Questions are grouped into pages (see questions/pages.ts). A page-level
    // visibleIf skips a whole branch's pages via the built-in Next/Previous
    // buttons; element-level visibleIf hides individual questions within a
    // visible page. Together they replace the old form's askCondition loop.
    pages: PAGES.map((page) => ({
      name: page.name,
      visibleIf: page.visibleIf,
      elements: page.questions.map((name) => toElement(QUESTIONS_BY_NAME[name])),
    })),
    showQuestionNumbers: 'off',
    showProgressBar: true,
    progressBarType: 'pages',
    // Auto-advance once every visible question on a page is answered (SurveyJS
    // waits for the whole page, and never fires when the last answer is a
    // checkbox, long text or file upload).
    autoAdvanceEnabled: true,
    autoAdvanceAllowComplete: false,
    // Keep answers when the user goes back and changes a branching answer;
    // serializeAnswers filters out answers from branches no longer taken.
    clearInvisibleValues: 'none',
    checkErrorsMode: 'onNextPage',
    // GENDER free text replaces the choice value rather than being stored
    // in a separate comment field.
    storeOthersAsComment: false,
    completeText: 'Confirm',
  })
  // Render the built-in navigation buttons (Previous / Next / Confirm) as
  // daisyUI primary buttons so they match the public website. The default
  // per-button classes carry SurveyJS's own `sd-btn` styles, which outrank
  // daisyUI's low-specificity :where() rules, so clear them and keep only the
  // daisyUI classes.
  survey.css = {
    navigationButton: 'd-btn d-btn-primary',
    bodyNavigationButton: '',
    navigation: {
      prev: '',
      next: '',
      complete: '',
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
