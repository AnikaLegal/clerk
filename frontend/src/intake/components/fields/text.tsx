// @flow
import React from 'react'

import { Button, Icon, TextInput, Form } from 'intake/design'
import { FormFieldProps } from './types'

export const TextField = ({
  onNext,
  onSkip,
  field,
  value,
  onChange,
  children,
}: FormFieldProps) => {
  // Determine whether the confirm button is active
  const isDisabled = !value
  return (
    <Form.Outer>
      <Form.Content>
        {children}
        <form onSubmit={onNext}>
          <TextInput
            placeholder="Type your answer here..."
            value={value}
            onChange={onChange}
            autoFocus={false}
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
