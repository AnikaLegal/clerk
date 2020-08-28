import { configure, addDecorator } from '@storybook/react'
import { withKnobs } from '@storybook/addon-knobs'

addDecorator(withKnobs)

function loadStories() {
  require('../src/styles.css')
  require('../src/stories/index.js')
}

configure(loadStories, module)
