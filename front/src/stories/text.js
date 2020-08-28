// @flow
// https://github.com/storybooks/storybook/tree/master/addons/knobs
import React from 'react'
import { storiesOf } from '@storybook/react'
import { text, boolean, number } from '@storybook/addon-knobs'
import { Text } from '../design'

export const stories = storiesOf('Text', module)

stories.add('Typography', () => (
  <>
    <Text.Header>Are you sure you want to abandon your case?</Text.Header>
    <Text.Body>
      Life can get busy quick and we appreciate the effort you have taken to
      start your journey with Anika. You are only a few steps away from creating
      a case and then we will take care of everthing else.
    </Text.Body>
  </>
))
