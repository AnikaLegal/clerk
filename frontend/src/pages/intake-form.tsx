// Client intake for Housing Health Check
import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'

import { mount } from 'utils'
import { LandingView } from 'intake/views/LandingView'
import { ROUTES } from 'intake/consts'
import { IneligibleView } from 'intake/views/IneligibleView'
import { NotFoundView } from 'intake/views/NotFoundView'
import { EligibilityFormView } from 'intake/views/EligibilityFormView'
import { ImpactFormView } from 'intake/views/ImpactFormView'
import { LandlordFormView } from 'intake/views/LandlordFormView'
import { PersonalFormView } from 'intake/views/PersonalFormView'
import { ProblemFormView } from 'intake/views/ProblemFormView'

export const App = () => (
  <BrowserRouter basename="/launch/">
    <Routes>
      <Route path={ROUTES.LANDING} Component={LandingView} />
      <Route path={ROUTES.INELIGIBLE} Component={IneligibleView} />
      <Route path={ROUTES.ELIGBILITY_FORM} Component={EligibilityFormView} />
      <Route path={ROUTES.IMPACT_FORM} Component={ImpactFormView} />
      <Route path={ROUTES.LANDLORD_FORM} Component={LandlordFormView} />
      <Route path={ROUTES.PERSONAL_FORM} Component={PersonalFormView} />
      <Route path={ROUTES.PROBLEM_FORM} Component={ProblemFormView} />
      <Route path="*" Component={NotFoundView} />
    </Routes>
  </BrowserRouter>
)

mount(App)
