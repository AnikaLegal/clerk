import { Model } from 'survey-core'

import { QUESTIONS } from '../questions'
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
  }
  switch (q.type) {
    case 'DISPLAY':
      // html questions hold no value, so they never appear in survey.data.
      return { type: 'html', name: q.name, html: q.html ?? '' }
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
    // One page per question: page name == question name, and page-level
    // visibleIf means the built-in Next/Previous buttons skip non-matching
    // branches (this replaces the old form's askCondition loop).
    pages: QUESTIONS.map((q) => ({
      name: q.name,
      visibleIf: q.visibleIf,
      elements: [toElement(q)],
    })),
    showQuestionNumbers: 'off',
    showProgressBar: true,
    progressBarType: 'pages',
    // Auto-advance after answering (the old form advanced on radio click).
    // Checkboxes, long text and file uploads are excluded by SurveyJS.
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
  // Allow inline HTML (links etc) in question titles and descriptions.
  survey.onTextMarkdown.add((_, options) => {
    if (options.text.includes('<')) {
      options.html = options.text
    }
  })
  return survey
}
