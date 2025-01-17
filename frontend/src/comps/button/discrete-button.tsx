import React from 'react'
import { Button, ButtonProps } from 'semantic-ui-react'
import styled from 'styled-components'

interface DiscreteButtonProps {
  children: React.ReactNode
}

export const DiscreteButton = ({
  children,
  ...props
}: DiscreteButtonProps | ButtonProps) => {
  return (
    <StyledButton compact {...props}>
      {children}
    </StyledButton>
  )
}

const StyledButton = styled(Button)`
  && {
    background-color: var(--mantine-color-body);
    font-size: var(--mantine-font-size-sm);
    color: var(--mantine-color-dark-2);
    &:focus {
      background-color: var(--mantine-color-body);
      color: var(--mantine-color-dark-2);
    }
    &:hover {
      background-color: var(--mantine-color-gray-light-hover);
      color: var(--mantine-color-text);
    }
  }
`
