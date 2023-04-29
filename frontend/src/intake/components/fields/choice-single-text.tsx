// @flow
import React, { useState } from 'react'
import styled from 'styled-components'

import {
  Icon,
  SelectInput,
  ButtonOptions,
  TextInputOptions,
  Form,
  theme,
} from 'intake/design'
import { timeout } from 'intake/utils'
import { FormFieldProps } from './types'

export const ChoiceSingleTextField = ({
  onNext,
  field,
  value,
  onChange,
  children,
}: FormFieldProps) => {
  const onClick = async (val) => {
    onChange(val)
    await timeout(200)
    onNext({ preventDefault: () => {} })
  }
  // Determine whether the confirm button is active
  const [hasAttemptSubmit, setAttemptSubmit] = useState(false)
  const isSubmitDisabled = !value
  const onSubmit = (e) => {
    onNext(e)
  }

  return (
    <Form.Outer>
      <Form.Content>
        {children}
        <SelectInput value={value} onChange={onClick} options={field.choices} />
        <TextInputOptions
          placeholder={field.placeholderText}
          value={value}
          onChange={onChange}
          autoFocus={false}
        />
      </Form.Content>
      <Form.Footer>
        <FooterForm onSubmit={onSubmit}>
          <ButtonOptions
            primary
            disabled={isSubmitDisabled}
            type="submit"
            Icon={field.button ? field.button.Icon : Icon.Tick}
          >
            {field.button ? field.button.text : 'OK'}
          </ButtonOptions>
        </FooterForm>
      </Form.Footer>
    </Form.Outer>
  )
}

const FooterForm = styled.form`
  ${theme.switch({ invalid: `opacity: 0; pointer-events: none;` })}
`
