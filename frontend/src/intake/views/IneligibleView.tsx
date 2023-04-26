// @flow
import React from 'react'
import { Splash, Text } from 'intake/design'
import { IMAGES } from 'intake/consts'
import { useScrollTop } from 'intake/utils'

export const IneligibleView = () => {
  useScrollTop()
  return (
    <Splash.Container left>
      <Splash.Image src={IMAGES.HEROES.SHRUB_GUY} />
      <Splash.Content>
        <Text.Header splash>Ineligible case</Text.Header>
        <Text.Body splash>
          It looks like the person you're trying to refer is not receiving
          casework support from you. If you are supporting a friend or family,
          please ask them to apply for help from{' '}
          <a href="https://intake.anikalegal.com">our intake form</a> directly.
        </Text.Body>
      </Splash.Content>
    </Splash.Container>
  )
}
