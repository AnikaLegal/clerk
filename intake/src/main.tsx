import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import 'survey-core/survey-core.css'

import { AppRoutes } from './routes'
import { ErrorBoundary } from './comps/ErrorBoundary'
import { initSentry } from './utils'
import './styles/global.css'

initSentry()

const root = document.getElementById('app')
if (root) {
  createRoot(root).render(
    <ErrorBoundary>
      <BrowserRouter basename="/intake/">
        <AppRoutes />
      </BrowserRouter>
    </ErrorBoundary>
  )
}
