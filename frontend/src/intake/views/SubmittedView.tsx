import React from 'react'

import { IMAGES, LINKS } from 'intake/consts'
import { Splash, Text } from 'intake/design'
import { useScrollTop } from 'intake/utils'

export const SubmittedView = () => {
  useScrollTop()
  return (
    <Splash.Container left>
      <Splash.Image src={IMAGES.HEROES.PAPER_GUY} />
      <Splash.Content>
        <Text.Header splash>
          <strong>Success!</strong> Your case has been submitted.
        </Text.Header>
        <Text.Body splash>
          Our paralegals will contact your client soon to discuss how we can
          help them.
        </Text.Body>
        <Splash.ButtonGroup>
          <a href={LINKS.HOME}>
            <Splash.Button primary last>
              Return home
            </Splash.Button>
          </a>
        </Splash.ButtonGroup>
      </Splash.Content>
    </Splash.Container>
  )
}
