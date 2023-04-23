import styled from 'styled-components'

import { theme } from '../theme'

const FormOuter = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  padding: 120px 0 200px 0;
  box-sizing: border-box;
  @media (max-height: 900px) {
    padding: 120px 0 0 0;
  }

  @media (max-width: ${theme.screen.mobile}) {
    display: grid;
    padding: 0 16px 0 16px;
    grid-template-columns: auto;
    grid-template-rows: minmax(100px, min-content) 1fr min-content;
    grid-template-areas:
      '.'
      'main'
      'footer';
  }
  /* Account for footer padding */
  min-height: 100vh;
  @media (max-width: ${theme.screen.mobile}) {
    min-height: calc(100vh - 76px);
  }
  @media (max-width: ${theme.screen.small}) {
    min-height: calc(100vh - 40px);
  }
  @media (max-height: 700px) {
    min-height: calc(100vh - 120px);
  }
`

const FormChild = styled.div`
  width: 100%;
  max-width: 700px;
  @media (max-width: ${theme.screen.mobile}) {
    width: calc(100vw - 32px);
    justify-self: center;
    align-self: center;
  }
`

const FormContent = styled(FormChild)`
  grid-area: main;
`

const FormFooter = styled(FormChild)`
  margin-top: 30px;
  grid-area: footer;
  @media (max-width: ${theme.screen.mobile}) {
    /* margin-top: 0; */
    align-self: end;
  }
`

export const Form = {
  Outer: FormOuter,
  Content: FormContent,
  Footer: FormFooter,
}
