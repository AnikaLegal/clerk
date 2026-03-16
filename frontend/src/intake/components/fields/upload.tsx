// @flow
import React from 'react'
import styled from 'styled-components'

import { Button, Icon, UploadInput, Form } from 'intake/design'
import { FormFieldProps } from './types'

export const UploadField = ({
  onNext,
  onSkip,
  field,
  value,
  onChange,
  onUpload,
  children,
}: FormFieldProps) => {
  // Determine whether the confirm button is active
  const isDisabled = !value
  if (!onUpload) {
    throw Error('onUpload required for UploadField')
  }
  return (
    <Form.Outer>
      <Form.Content>
        {children}
        <form onSubmit={onNext}>
          <UploadInput
            onUpload={onUpload}
            values={value || []}
            onChange={onChange}
            disabled={isDisabled}
          />
          <ButtonGroupEl>
            <Button
              primary
              disabled={isDisabled}
              type="submit"
              Icon={field.button ? field.button.Icon : Icon.Tick}
            >
              {field.button ? field.button.text : 'OK'}
            </Button>
            {!field.required && (
              <Button onClick={onNext}>{field.skipText || 'Skip'}</Button>
            )}
          </ButtonGroupEl>
        </form>
      </Form.Content>
    </Form.Outer>
  )
}

const ButtonGroupEl = styled.div`
  margin-top: 24px;
`
