import { SerializedError } from '@reduxjs/toolkit'
import { FetchBaseQueryError } from '@reduxjs/toolkit/query'
import React from 'react'
import { Icon, Message, StrictMessageProps } from 'semantic-ui-react'

export interface ErrorMessageProps extends Omit<StrictMessageProps, 'error'> {
  error: FetchBaseQueryError | SerializedError
}

export const ErrorMessage = ({ error, ...props }: ErrorMessageProps) => {
  // TODO: fix the following mess:
  let message = 'Unknown error.'
  if (
    'data' in error &&
    error.data &&
    typeof error.data === 'object' &&
    'detail' in error.data
  ) {
    message = error.data.detail as string
  }
  return (
    <Message error icon {...props}>
      <Icon name="exclamation" size="mini" />
      <Message.Content>
        <Message.Header>Oops! There was an error</Message.Header>
        {message}
      </Message.Content>
    </Message>
  )
}
