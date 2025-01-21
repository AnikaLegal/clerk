import React from 'react'
import { Button, ButtonProps } from 'semantic-ui-react'
import styled from 'styled-components'

interface TextButtonProps {
  children: React.ReactNode
}

export const TextButton = ({
  children,
  ...props
}: TextButtonProps | ButtonProps) => {
  return (
    <StyledButton compact {...props}>
      {children}
    </StyledButton>
  )
}

const StyledButton = styled(Button)`
  &&&& {
    background-color: inherit;
    color: inherit;
    padding: 0;
    &:focus {
      background-color: inherit;
      color: inherit;
    }
    &:hover {
      background-color: inherit;
      color: inherit;
    }
  }
`
