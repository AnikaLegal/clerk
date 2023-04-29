// Client intake for Housing Health Check
import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'

import { mount } from 'utils'
import { LandingView } from 'intake/views/LandingView'
import { ROUTES } from 'intake/consts'
import { IneligibleView } from 'intake/views/IneligibleView'
import { NotFoundView } from 'intake/views/NotFoundView'
import { FormView } from 'intake/views/FormView'
import { SubmittedView } from 'intake/views/SubmittedView'

export const App = () => (
  <BrowserRouter basename="/launch/">
    <Routes>
      <Route path={ROUTES.LANDING} Component={LandingView} />
      <Route
        path={ROUTES.INELIGIBLE.NOT_SOCIAL_WORK_CLIENT}
        Component={IneligibleView}
      />
      <Route path={ROUTES.SUBMITTED} Component={SubmittedView} />
      <Route path={ROUTES.FORM} Component={FormView} />
      <Route path="*" Component={NotFoundView} />
    </Routes>
  </BrowserRouter>
)

mount(App)
