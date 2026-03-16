import React from 'react'

import { Button, Icon, NumberInput, Form } from 'intake/design'
import { FormFieldProps } from './types'

export const NumberField = ({
  onNext,
  onSkip,
  field,
  value,
  onChange,
  children,
}: FormFieldProps) => {
  // Determine whether the confirm button is active
  const isDisabled = !value && value !== 0
  return (
    <Form.Outer>
      <Form.Content>
        {children}
        <form onSubmit={onNext}>
          <NumberInput
            placeholder="Enter a number here..."
            value={value}
            onChange={onChange}
            autoFocus={false}
            type="tel"
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
