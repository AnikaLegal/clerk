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

const checkIsPhoneValid = (phone: string): boolean => {
  return Boolean(phone) && phone.length < 16
}

export const PhoneField = ({
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
  const isPhoneValid = checkIsPhoneValid(value)
  const shouldShowError = !isPhoneValid && hasAttemptSubmit
  const onSubmit = (e) => {
    if (isPhoneValid) {
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
            placeholder="Type your phone number here..."
            type="tel"
            value={value || ''}
            onChange={onChange}
            autoFocus={false}
          />
          {shouldShowError && (
            <ErrorWrapper>
              <ErrorMessage>
                Hold on, that phone number doesn't look valid
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
