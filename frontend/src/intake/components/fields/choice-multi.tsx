// @flow
import React from 'react'

import { Button, Icon, MultiSelectInput, Form } from 'intake/design'
import { FormFieldProps } from './types'

export const ChoiceMultiField = ({
  onNext,
  onSkip,
  field,
  value,
  onChange,
  children,
}: FormFieldProps) => {
  // Determine whether the confirm button is active
  let isDisabled
  try {
    isDisabled = typeof value === 'object' ? value.length < 1 : !value
  } catch {
    isDisabled = !value
  }

  return (
    <Form.Outer>
      <Form.Content>
        {children}
        <form onSubmit={onNext}>
          <MultiSelectInput
            values={value}
            onChange={onChange}
            options={field.choices}
          />
        </form>
      </Form.Content>
      <Form.Footer>
        <form onSubmit={onNext}>
          <Button
            primary
            disabled={isDisabled}
            type="submit"
            Icon={field.button ? field.button.Icon : Icon.Tick}
          >
            {field.button ? field.button.text : 'OK'}
          </Button>
          {!field.required && (
            <Button onClick={onSkip}>{field.skipText || 'Skip'}</Button>
          )}
        </form>
      </Form.Footer>
    </Form.Outer>
  )
}
