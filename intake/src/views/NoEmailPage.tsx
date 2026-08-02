import { useEffect, useMemo, useRef, useState } from 'react'
import { Model } from 'survey-core'
import { Survey } from 'survey-react-ui'

import { api } from '../api'
import { Offboard } from '../comps/Offboard'
import { PHONE_MAX_LENGTH, PHONE_VALIDATOR } from '../form/phone'
import { logException } from '../utils'

// A small SurveyJS form so the no-email contact fields get the same validation
// behaviour and styling as the rest of the intake form. Only name and phone
// are submitted; the consent checkbox is a required gate. The offboard
// template's primary action submits the form, so the survey's own navigation
// buttons are hidden.
const buildNoEmailModel = (): Model => {
  const survey = new Model({
    showQuestionNumbers: 'off',
    showProgressBar: false,
    showNavigationButtons: false,
    questionErrorLocation: 'bottom',
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
                isRequired: true,
                requiredErrorText: 'Please enter your phone number.',
                maxLength: PHONE_MAX_LENGTH,
                validators: [PHONE_VALIDATOR],
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
  return survey
}

/**
 * Contact fallback for users without an email address: takes a name and phone
 * number and asks the coordinators to call them back. Feeds the same
 * WebflowContact pipeline as the public site's landing contact form. Rendered
 * on the offboarding template with the form card in the body slot; the
 * template swaps to a plain success fill once the details are sent.
 */
export const NoEmailPage = () => {
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
      <Offboard
        headline="Thanks, we'll be in touch"
        explanation="We've received your details and one of our team will call
        you to see if we're able to help."
      />
    )
  }

  return (
    <Offboard
      headline="Contact us"
      explanation="Anika Legal is an online service, so we usually communicate
      by email. If you don't have an email address, leave your details below
      and we'll call you to see if we're able to help. If not, we'll point you
      to another organisation."
      primary={{
        label: 'Send my details',
        // Validates the form and fires onCompleting above.
        onClick: () => survey.tryComplete(),
      }}
    >
      <Survey model={survey} />
      {error && (
        <p className="intake-form-error" role="alert">
          {error}
        </p>
      )}
    </Offboard>
  )
}
