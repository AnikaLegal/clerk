import React from 'react'
import { createRoot } from 'react-dom/client'

import { App } from 'intake/main'

const domNode = document.getElementById('app')
if (domNode && !domNode.hasChildNodes()) {
  const root = createRoot(domNode)
  root.render(<App />)
}
