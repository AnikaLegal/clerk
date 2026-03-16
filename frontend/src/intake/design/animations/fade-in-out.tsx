import React from 'react'
import CSSTransition from 'react-transition-group/CSSTransition'
import styled from 'styled-components'

type Props = {
  visible: boolean
  children: any
}

export const ANIMATION_TIME = 400 // ms

export const FadeInOut = ({ visible, children }: Props) => (
  <AnimationStyles>
    <CSSTransition
      in={visible}
      timeout={ANIMATION_TIME}
      classNames="fade-in-out"
      unmountOnExit
    >
      {children}
    </CSSTransition>
  </AnimationStyles>
)

const AnimationStyles = styled.div`
  .fade-in-out-enter {
    opacity: 0.6;
    /* transform: translateX(2vw); */
  }
  .fade-in-out-enter-active {
    opacity: 1;
    /* transform: translateX(0px); */
    transition: all ${ANIMATION_TIME}ms ease-out;
  }
  .fade-in-out-exit {
    opacity: 1;
    /* transform: translateX(0px); */
  }
  .fade-in-out-exit-active {
    opacity: 0.6;
    transition: all ${ANIMATION_TIME / 2}ms ease-in;
    /* transform: translateX(-2vw); */
  }
`
