import React from 'react'

import styled from 'styled-components'

import {
  useScrollTop,
  waitSeconds,
  loadFormData,
  storeFormData,
} from 'intake/utils'
import { Navbar } from 'intake/design'
import { PROGRESS } from 'intake/consts'

export const EligibilityFormView = () => {
  useScrollTop()
  return (
    <FormEl>
      <Navbar current={0} steps={PROGRESS} />
    </FormEl>
  )
}

const FormEl = styled.div`
  overflow-x: hidden;
`
