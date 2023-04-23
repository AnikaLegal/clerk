// Client intake for Housing Health Check
import React from 'react'
import styled from 'styled-components'

import { mount } from 'utils'

import { Splash, Text, theme } from 'intake/design'
import { IMAGES, LINKS } from 'intake/consts'

export const App = () => {
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
          <a href={LINKS.START_FORM}>
            <Splash.Button primary>Let’s get started</Splash.Button>
          </a>
        </Splash.ButtonGroup>
      </Splash.Content>
      <Splash.Image src={IMAGES.HEROES.PHONE_LADY} />
    </Splash.Container>
  )
}

// Used for warning messages for stuff like Christmas closures.
const WarningBody = styled(Text.Body)`
  background-color: ${theme.color.marigold};
  color: ${theme.color.grey.dark};
  font-size: 14px;
  line-height: 1.4;
  padding: 1rem;
  border-radius: 10px;
  & > strong {
    color: #d72207;
  }
`

const LogoEl = styled.img`
  height: 122px;
  margin-bottom: 39px;
  @media (max-width: ${theme.screen.mobile}) {
    display: none;
  }
`

mount(App)
