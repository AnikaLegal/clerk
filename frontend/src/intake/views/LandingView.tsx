// Client intake for Housing Health Check
import React from 'react'
import { Link } from 'react-router-dom'

import { IMAGES, LINKS, ROUTES } from 'intake/consts'
import { Splash, Text } from 'intake/design'
import { useScrollTop } from 'intake/utils'
import { events } from 'intake/analytics'

export const LandingView = () => {
  useScrollTop()
  return (
    <Splash.Container>
      <Splash.Content>
        <Text.Header splash>
          Welcome to the Anika Legal intake form!
        </Text.Header>
        <Text.Body splash>
          We’re here to help you with your rental problem. In order for us to
          help you, we need to ask you a series of simple questions to see
          whether you're eligible. This questionnaire takes approximately 10
          minutes to complete.
        </Text.Body>
        <Text.Body splash>
          Before starting the intake form, please have the information ready
          about:
        </Text.Body>
        <ul>
          <li>Your rental property</li>
          <li>Your rental provider</li>
          <li>Your agent, if applicable</li>
          <li>Your income</li>
        </ul>
        <Text.Body splash>
          You can have a look at our{' '}
          <a href={LINKS.COLLECTIONS_STATEMENT}>collection statement</a> if you
          have any questions about why we need your information, and what we do
          with it.
        </Text.Body>
        <Splash.ButtonGroup>
          <Link
            to={ROUTES.build(ROUTES.FORM, { ':qIdx': 0 }, {})}
            onClick={events.onStartIntake}
          >
            <Splash.Button primary>Let’s get started</Splash.Button>
          </Link>
          <a href={LINKS.SERVICES}>
            <Splash.Button last>Learn more</Splash.Button>
          </a>
        </Splash.ButtonGroup>
      </Splash.Content>
      <Splash.Image src={IMAGES.HEROES.PHONE_LADY} />
    </Splash.Container>
  )
}
