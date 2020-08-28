//@flow
import React from 'react'
import { render } from 'react-dom'

import { App } from './app'
import './styles.css'

const rootEl = document.getElementById('app')
if (rootEl) render(<App />, rootEl)
