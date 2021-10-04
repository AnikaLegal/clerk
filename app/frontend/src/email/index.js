import React from 'react'
import { hydrate, render } from 'react-dom'

import { App } from './app'

const rootEl = document.getElementById('app')
if (rootEl.hasChildNodes()) {
  hydrate(<App />, rootEl)
} else {
  render(<App />, rootEl)
}
