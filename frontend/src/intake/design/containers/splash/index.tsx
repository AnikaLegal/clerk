import * as React from 'react'
import styled from 'styled-components'

import { IMAGES } from 'intake/consts'
import { theme } from '../../theme'
import { Navbar } from '../../navbar'
import { BigButton } from '../../inputs'
import { FadeFooter } from '../../footer'

import { SplashSwoosh } from './swoosh'

const SplashOuterEl = styled.div`
  width: 100%;
  height: 100vh;
  position: relative;
  overflow: hidden;
  box-sizing: border-box;
  @media (max-width: ${theme.screen.mobile}) {
    overflow: auto;
    padding: 0 16px 0 16px;
  }
`
const SplashInnerEl = styled.div`
  width: 86vw;
  max-width: 1227px;
  margin: 0 auto 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  @media (max-width: ${theme.screen.mobile}) {
    height: auto;
    width: 100%;
    padding-top: 161px;
    flex-direction: column-reverse;
    ${theme.switch({ left: `flex-direction: column;` })}
  }
  @media (max-width: ${theme.screen.small}), (max-height: 700px) {
    padding-top: 89px;
  }
`

const SplashImage = styled.img`
  @media (max-width: ${theme.screen.mobile}) {
    width: 100%;
    width: calc(100% - 2 * 16px);
    margin-bottom: 80px;
    max-height: 300px;
  }
  @media (max-width: ${theme.screen.small}), (max-height: 700px) {
    margin-bottom: 43px;
  }
  @media (max-height: 600px) and (max-width: ${theme.screen.mobile}) {
    max-height: 180px;
  }
`
const SplashContent = styled.div`
  max-width: 589px;
  @media (max-width: ${theme.screen.mobile}) {
    max-width: 400px;
  }
`

const SplashButtonGroup = styled.div`
  margin-top: 50px;

  @media (max-width: ${theme.screen.mobile}) {
    margin-top: 32px;
  }
  @media (max-width: ${theme.screen.small}) {
    margin-top: 27px;
  }
`

const SplashButton = styled(BigButton)`
  cursor: pointer;
  margin-right: 30px;
  ${theme.switch({ last: `margin-right: 0;` })}
  @media (max-width: ${theme.screen.mobile}) {
    margin-right: 0;
    margin-bottom: 16px;
    ${theme.switch({ last: `margin-bottom: 0;` })}
  }
`

type SplashProps = {
  children: React.ReactNode
  left?: boolean
}

const SplashContainer = ({ children, left }: SplashProps) => (
  <SplashOuterEl left={left}>
    {left ? (
      <>
        <SplashSwoosh className="left desktop" src={IMAGES.SWOOSH.LEFT} />
        <SplashSwoosh className="left mobile" src={IMAGES.SWOOSH.LEFT_MOBILE} />
        <SplashSwoosh
          className="left mobile-small"
          src={IMAGES.SWOOSH.LEFT_MOBILE_SMALL}
        />
      </>
    ) : (
      <>
        <SplashSwoosh className="right desktop" src={IMAGES.SWOOSH.RIGHT} />
        <SplashSwoosh
          className="right mobile"
          src={IMAGES.SWOOSH.RIGHT_MOBILE}
        />
        <SplashSwoosh
          className="right mobile-small"
          src={IMAGES.SWOOSH.RIGHT_MOBILE_SMALL}
        />
      </>
    )}
    <Navbar />
    <SplashInnerEl left={left}>{children}</SplashInnerEl>
    <FadeFooter />
  </SplashOuterEl>
)

export const Splash = {
  Container: SplashContainer,
  Image: SplashImage,
  Content: SplashContent,
  Button: SplashButton,
  ButtonGroup: SplashButtonGroup,
}
