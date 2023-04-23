import * as React from 'react'
import styled from 'styled-components'

import { IMAGES } from 'intake/consts'
import { Icon } from './icons'
import { theme } from './theme'
import { StepProgress } from './progress'

type Props = {
  onClose?: () => void
  onBack?: () => void
  progress?: {
    current: number
    steps: Array<string>
  }
}

export const Navbar = ({ onClose, onBack, progress }: Props) => {
  return (
    <NavbarEl>
      <div>{onBack && <Icon.Back onClick={onBack} />}</div>
      <div>
        <img className="logo" src={IMAGES.LOGO.TEXT.COLOR.SVG} />
        {progress && (
          <StepProgress current={progress.current} steps={progress.steps} />
        )}
      </div>
      <div>{onClose && <Icon.Close onClick={onClose} />}</div>
    </NavbarEl>
  )
}

const NavbarEl = styled.div`
  /* Default to small mobile screen */
  position: absolute;
  display: flex;
  justify-content: space-between;
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
