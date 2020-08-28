// @flow
// https://github.com/storybooks/storybook/tree/master/addons/knobs
import React from 'react'
import { storiesOf } from '@storybook/react'
import { text, boolean, number } from '@storybook/addon-knobs'
import { BigButton, Button, LeftSwoosh, RightSwoosh, Icon } from '../design'

export const stories = storiesOf('Inputs', module)

stories.add('Big Button', () => (
  <>
    <BigButton disabled={boolean('Disabled', false)} primary>
      Let's get started
    </BigButton>
    <BigButton disabled={boolean('Disabled', false)}>Abandon case</BigButton>
  </>
))

stories.add('Button', () => (
  <>
    <Button disabled={boolean('Disabled', false)} primary Icon={Icon.Tick}>
      OK
    </Button>
    <Button disabled={boolean('Disabled', false)}>Cancel</Button>
  </>
))

stories.add('Left Swoosh', () => <LeftSwoosh height={number('height', 300)} />)

stories.add('Right Swoosh', () => (
  <RightSwoosh height={number('height', 300)} />
))
