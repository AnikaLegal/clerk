import { useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Model } from 'survey-core'
import { Survey } from 'survey-react-ui'

import { api } from '../api'
import { LINKS } from '../consts'
import { logException } from '../utils'

// A small SurveyJS form so the no-email contact fields get the same live
// validation (errors that clear as they are fixed) and styling as the rest of
// the intake form. Only name and phone are submitted; the consent checkbox is
// a required gate.
const buildNoEmailModel = (): Model => {
  const survey = new Model({
    showQuestionNumbers: 'off',
    showProgressBar: false,
    completeText: 'Contact us',
    questionErrorLocation: 'bottom',
    // Re-validate on every value change, so a shown error clears as soon as
    // the field is corrected (the default only re-checks on the next submit).
    checkErrorsMode: 'onValueChanged',
    textUpdateMode: 'onTyping',
    // A single page, so the form renders with the same page/card styling as the
    // main intake form's pages.
    pages: [
      {
        name: 'CONTACT',
        elements: [
          {
            // Group the fields in a single panel so they read as one card.
            type: 'panel',
            name: 'CONTACT_PANEL',
            elements: [
              {
                type: 'text',
                name: 'NAME',
                title: 'Name',
                isRequired: true,
                requiredErrorText: 'Please enter your name.',
                maxLength: 255,
              },
              {
                type: 'text',
                name: 'PHONE',
                title: 'Phone number',
                inputType: 'tel',
                // A tel input is excluded from the survey-wide onTyping commit
                // (SurveyJS only live-commits text/number/password), so validate
                // it on blur - the error then clears when the field is left with
                // a valid number, with no per-keystroke nagging while typing.
                textUpdateMode: 'onBlur',
                isRequired: true,
                requiredErrorText: 'Please enter your phone number.',
                maxLength: 255,
                validators: [
                  {
                    type: 'regex',
                    regex: '^\\+?[0-9]{8,}$',
                    text: 'Please enter a valid phone number.',
                  },
                ],
              },
              {
                // A single-choice checkbox: isRequired forces it to be ticked.
                type: 'checkbox',
                name: 'CONSENT',
                titleLocation: 'hidden',
                isRequired: true,
                requiredErrorText:
                  'Please agree to share your details so we can contact you.',
                choices: [
                  {
                    value: 'agree',
                    text: 'I agree to share my details with Anika Legal.',
                  },
                ],
              },
            ],
          },
        ],
      },
    ],
  })
  // Match the main intake form's navigation styling: render the Complete
  // ("Contact us") button as a daisyUI primary button and clear SurveyJS's own
  // sd-btn classes (which otherwise outrank the daisyUI rules and force a
  // smaller radius) so the daisyUI look fully applies.
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
  return survey
}

/**
 * Contact fallback for users without an email address: takes a name and phone
 * number and asks the coordinators to call them back. Feeds the same
 * WebflowContact pipeline as the public site's landing contact form.
 */
export const NoEmailPage = () => {
  const navigate = useNavigate()
  const survey = useMemo(buildNoEmailModel, [])
  const [isSubmitted, setIsSubmitted] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const isSubmitting = useRef(false)

  useEffect(() => {
    const onCompleting: Parameters<typeof survey.onCompleting.add>[0] = (
      sender,
      options
    ) => {
      // Handle submission ourselves and block SurveyJS's own completion, so its
      // built-in "saving"/completion page never flashes before our success
      // view. Validation has already passed by the time onCompleting fires.
      options.allow = false
      if (isSubmitting.current) return
      isSubmitting.current = true
      setError(null)
      const name = String(sender.getValue('NAME') ?? '')
      const phone = String(sender.getValue('PHONE') ?? '')
      api.noemail
        .create(name, phone)
        .then(() => setIsSubmitted(true))
        .catch((err) => {
          logException(err)
          // Let the user retry and tell them it failed - they have no other way
          // to reach us from here.
          isSubmitting.current = false
          setError(
            'Sorry, something went wrong and your details were not sent. Please try again.'
          )
        })
    }
    survey.onCompleting.add(onCompleting)
    return () => survey.onCompleting.remove(onCompleting)
  }, [survey])

  if (isSubmitted) {
    return (
      <div className="intake-splash">
        <h1>Thanks, we&apos;ll be in touch.</h1>
        <p>
          We&apos;ve received your details and one of our team will call you to
          see if we&apos;re able to help.
        </p>
        <div className="intake-button-group">
          <button
            type="button"
            className="d-btn intake-btn-secondary"
            onClick={() => navigate(-1)}
          >
            Go back
          </button>
          <a href={LINKS.HOME}>
            <button type="button" className="d-btn intake-btn-secondary">
              Return home
            </button>
          </a>
        </div>
      </div>
    )
  }

  return (
    <div className="intake-splash">
      <h1>Contact us</h1>
      <p>
        Anika Legal is an online service, so we usually communicate by email. If
        you don&apos;t have an email address, leave your details below and
        we&apos;ll call you to see if we&apos;re able to help. If not,
        we&apos;ll point you to another organisation.
      </p>
      <div className="intake-form intake-form--contact">
        <Survey model={survey} />
      </div>
      {error && (
        <p className="intake-form-error" role="alert">
          {error}
        </p>
      )}
      <div className="intake-button-group">
        <button
          type="button"
          className="d-btn intake-btn-secondary"
          onClick={() => navigate(-1)}
        >
          Go back
        </button>
        <a href={LINKS.HOME}>
          <button type="button" className="d-btn intake-btn-secondary">
            Return home
          </button>
        </a>
      </div>
    </div>
  )
}
