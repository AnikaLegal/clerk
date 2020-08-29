// @flow
// https://github.com/storybooks/storybook/tree/master/addons/knobs
import React from 'react'
import { storiesOf } from '@storybook/react'
import { number } from '@storybook/addon-knobs'

import {
  ErrorMessage,
  TextContainer,
  Text,
  BigButton,
  StepProgress,
} from '../design'

export const stories = storiesOf('Containers', module)

stories.add('Error Message', () => (
  <>
    <ErrorMessage>Hold on, you forgot your keys</ErrorMessage>
    <ErrorMessage>Also, you forgot your wallet</ErrorMessage>
  </>
))

stories.add('Text Container', () => (
  <div style={{ height: '50vh' }}>
    <TextContainer>
      <Text.Header>
        First of all, congratulations on taking the first step in solving your
        rental issues.
      </Text.Header>
      <BigButton primary> Thank you</BigButton>
    </TextContainer>
  </div>
))

stories.add('Step Progress', () => (
  <StepProgress
    current={number('current step', 2)}
    steps={['Problem', 'Landlord', 'Agency', 'Preferences']}
  />
))
