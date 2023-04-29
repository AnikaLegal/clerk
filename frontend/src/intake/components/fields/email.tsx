import React, { useState } from 'react'
import styled from 'styled-components'

import {
  Button,
  Icon,
  TextInput,
  ErrorMessage,
  Form,
  theme,
} from 'intake/design'
import { FormFieldProps } from './types'

// Grabbed a regex off the internet.
// https://html.form.guide/best-practices/validate-email-address-using-javascript/
const EMAIL_REGEX =
  /^(?:[a-z0-9!#$%&amp;'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&amp;'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])$/

const checkIsEmailValid = (email: string): boolean => {
  if (!email) return true
  return EMAIL_REGEX.test(email)
}

export const EmailField = ({
  onNext,
  onSkip,
  field,
  value,
  onChange,
  children,
}: FormFieldProps) => {
  // Determine whether the confirm button is active
  const [hasAttemptSubmit, setAttemptSubmit] = useState(false)
  const isSubmitDisabled = !value
  const isEmailValid = checkIsEmailValid(value)
  const shouldShowError = !isEmailValid && hasAttemptSubmit
  const onSubmit = (e) => {
    if (isEmailValid) {
      onNext(e)
    } else {
      e.preventDefault()
      setAttemptSubmit(true)
    }
  }

  return (
    <Form.Outer>
      <FormContent>
        {children}
        <form onSubmit={onSubmit}>
          <TextInput
            placeholder="Type your email here..."
            type="email"
            value={value ? value.toLowerCase() : ''}
            onChange={onChange}
            autoFocus={false}
          />
          {shouldShowError && (
            <ErrorWrapper>
              <ErrorMessage>
                Hold on, that email doesn't look valid
              </ErrorMessage>
            </ErrorWrapper>
          )}
        </form>
      </FormContent>
      <Form.Footer>
        <FooterForm invalid={shouldShowError} onSubmit={onSubmit}>
          <Button
            primary
            disabled={isSubmitDisabled}
            type="submit"
            Icon={field.button ? field.button.Icon : Icon.Tick}
          >
            {field.button ? field.button.text : 'OK'}
          </Button>
          {!field.required && (
            <Button onClick={onSkip}>{field.skipText || 'Skip'}</Button>
          )}
        </FooterForm>
      </Form.Footer>
    </Form.Outer>
  )
}

const ErrorWrapper = styled.div`
  position: absolute;
  left: 0;
  right: 0;
  bottom: -40px;
`

const FooterForm = styled.form`
  ${theme.switch({ invalid: `opacity: 0; pointer-events: none;` })}
`

const FormContent = styled(Form.Content)`
  position: relative;
`
