import { Route, Routes } from 'react-router-dom'

import { ROUTES } from './consts'
import { EXIT_PAGES } from './views/exit-content'
import { ExitPage } from './views/ExitPage'
import { FormPage } from './views/FormPage'
import { NoEmailPage } from './views/NoEmailPage'
import { NotFoundPage } from './views/NotFoundPage'
import { ResumePage } from './views/ResumePage'

export const AppRoutes = () => (
  <Routes>
    <Route path={ROUTES.LANDING} element={<FormPage />} />
    <Route path={ROUTES.RESUME} element={<ResumePage />} />
    <Route path={ROUTES.NO_EMAIL} element={<NoEmailPage />} />
    {Object.keys(EXIT_PAGES).map((path) => (
      <Route key={path} path={path} element={<ExitPage />} />
    ))}
    <Route path="*" element={<NotFoundPage />} />
  </Routes>
)
