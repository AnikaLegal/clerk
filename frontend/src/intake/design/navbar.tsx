import * as React from 'react'
import styled from 'styled-components'

import { IMAGES } from 'intake/consts'
import { Icon } from './icons'
import { theme } from './theme'
import { StepProgress } from './progress'

interface Props {
  current?: number
  steps?: Array<string>
  onBack: () => void
}

export const Navbar: React.FC<Props> = ({ current, steps, onBack }) => (
  <NavbarEl>
    <Icon.Back onClick={onBack} />
    <div>
      <img className="logo" src={IMAGES.LOGO.TEXT.COLOR.SVG} />
      {steps && <StepProgress current={current} steps={steps} />}
    </div>
    <div />
  </NavbarEl>
)

const NavbarEl = styled.div`
  /* Default to small mobile screen */
  position: absolute;
  display: flex;
  justify-content: space-around;
  align-items: center;
  top: 21.3px;
  left: 16px;
  right: 16px;
  .logo {
    height: 27.4px;
    user-select: none;
  }
  svg {
    height: 20.5px;
  }
  @media (min-width: ${theme.screen.small}) {
    /* Larger than small mobile screen */
    top: 40px;
    .logo {
      height: 32px;
    }
    svg {
      height: 24px;
    }
  }

  @media (min-width: ${theme.screen.mobile}), {
    /* Larger than mobile */
    top: 35px;
    left: 60px;
    right: 60px;
    height: 29px;
    .logo {
      display: none;
    }

    svg {
      height: 29px;
    }
  }
`
