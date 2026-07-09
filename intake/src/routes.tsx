import { Route, Routes } from 'react-router-dom'

import { ROUTES } from './consts'
import { AbandonPage } from './views/AbandonPage'
import { EXIT_PAGES } from './views/exit-content'
import { ExitPage } from './views/ExitPage'
import { FormPage } from './views/FormPage'
import { LandingPage } from './views/LandingPage'
import { NoEmailPage } from './views/NoEmailPage'
import { NotFoundPage } from './views/NotFoundPage'
import { ResumePage } from './views/ResumePage'
import { SubmittedPage } from './views/SubmittedPage'

export const AppRoutes = () => (
  <Routes>
    <Route path={ROUTES.LANDING} element={<LandingPage />} />
    <Route path={ROUTES.FORM} element={<FormPage />} />
    <Route path={ROUTES.RESUME} element={<ResumePage />} />
    <Route path={ROUTES.NO_EMAIL} element={<NoEmailPage />} />
    <Route path={ROUTES.SUBMITTED} element={<SubmittedPage />} />
    <Route path={ROUTES.ABANDON} element={<AbandonPage />} />
    {Object.keys(EXIT_PAGES).map((path) => (
      <Route key={path} path={path} element={<ExitPage />} />
    ))}
    <Route path="*" element={<NotFoundPage />} />
  </Routes>
)
