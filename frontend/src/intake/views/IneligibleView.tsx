// @flow
import React from 'react'
import { useLocation } from 'react-router'
import { Splash, Text } from 'intake/design'
import { IMAGES, ROUTES } from 'intake/consts'
import { useScrollTop } from 'intake/utils'

export const IneligibleView = () => {
  useScrollTop()
  const location = useLocation()
  const content = INELIGIBLE_REASONS[location.pathname] || null
  return (
    <Splash.Container left>
      <Splash.Image src={IMAGES.HEROES.SHRUB_GUY} />
      {content}
    </Splash.Container>
  )
}

const INELIGIBLE_REASONS: { [key: string]: React.ReactElement } = {
  [ROUTES.INELIGIBLE.NOT_SOCIAL_WORK_CLIENT]: (
    <Splash.Content>
      <Text.Header splash>Ineligible case</Text.Header>
      <Text.Body splash>
        It looks like the person you're trying to refer is not receiving
        casework support from you. If you are supporting a friend or family,
        please ask them to apply for help from{' '}
        <a href="https://intake.anikalegal.com">our intake form</a> directly.
      </Text.Body>
    </Splash.Content>
  ),
  [ROUTES.INELIGIBLE.TENANCY_TOO_LATE]: (
    <Splash.Content>
      <Text.Header splash>Ineligible case</Text.Header>
      <Text.Body splash>
        Unfortunately the tenancy that you are referring started more than three
        weeks ago. We are unable to help them in this case.
      </Text.Body>
    </Splash.Content>
  ),
  [ROUTES.INELIGIBLE.NO_TENANCY_YET]: (
    <Splash.Content>
      <Text.Header splash>Ineligible case</Text.Header>
      <Text.Body splash>
        Our Service focuses on helping renters under their rights and duties as
        they enter new tenancy arrangements. If a new rental has not yet been
        found, the service will not yet be able to assist.
      </Text.Body>
    </Splash.Content>
  ),
}
