// Client intake for Housing Health Check
import React from 'react'
import styled from 'styled-components'
import { Link } from 'react-router-dom'

import { Splash, Text, theme } from 'intake/design'
import { IMAGES, LINKS, ROUTES } from 'intake/consts'
import { useScrollTop } from 'intake/utils'

export const LandingView = () => {
  useScrollTop()
  return (
    <Splash.Container>
      <Splash.Content>
        <LogoEl src={IMAGES.LOGO.TEXT.COLOR.SVG} />
        <Text.Header splash>Housing Health Check Referrals</Text.Header>
        <Text.Body splash>
          We’re here to help you with your client as they enter their new
          rental. In order to help you, we need to ask you some questions to see
          whether they're eligible. This will take about 5 minutes.
        </Text.Body>
        <Text.Body splash>
          Before starting the intake form, please have the information ready
          about:
          <ul>
            <li>Your client's contact details</li>
            <li>Your client's PRAP application</li>
          </ul>
          You can have a look at our{' '}
          <a href={LINKS.COLLECTIONS_STATEMENT}>collection statement</a> if you
          have any questions about why we need this information, and what we do
          with it.{' '}
        </Text.Body>

        <Text.Body splash>
          <strong>
            By proceeding you confirm that you have consent from your client to
            make this referral and share their personal information.
          </strong>
        </Text.Body>
        <Text.Header splash></Text.Header>
        <Splash.ButtonGroup>
          <Link to={ROUTES.FORM.replace(':qIdx', '0')}>
            <Splash.Button primary>Let’s get started</Splash.Button>
          </Link>
        </Splash.ButtonGroup>
      </Splash.Content>
      <Splash.Image src={IMAGES.HEROES.PHONE_LADY} />
    </Splash.Container>
  )
}

const LogoEl = styled.img`
  height: 122px;
  margin-bottom: 39px;
  @media (max-width: ${theme.screen.mobile}) {
    display: none;
  }
`
