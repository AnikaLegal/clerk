import React from 'react'
import { useNavigate } from 'react-router-dom'

import { IMAGES } from 'intake/consts'
import { Splash, Text } from 'intake/design'
import { useScrollTop } from 'intake/utils'

export const ProblemFormView = () => {
  useScrollTop()
  const navigate = useNavigate()
  return (
    <Splash.Container left>
      <Splash.Image src={IMAGES.HEROES.PAPER_GUY} />
      <Splash.Content>
        <Text.Header splash>Page not found</Text.Header>
        <Text.Body splash>We couldn't find this page for you. Sorry!</Text.Body>
        <Splash.ButtonGroup>
          <Splash.Button primary last onClick={() => navigate(-1)}>
            Go back
          </Splash.Button>
        </Splash.ButtonGroup>
      </Splash.Content>
    </Splash.Container>
  )
}
