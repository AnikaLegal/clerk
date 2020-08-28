const path = require('path')
const base = require('../webpack/webpack.base.js')
const babel = require('../webpack/babel.js')

module.exports = async ({ config, mode }) => {
  const babelRule = babel(false)
  const fileRule = base.module.rules[1]
  const cssRule = base.module.rules[0]
  config.module.rules = [
    babelRule,
    fileRule,
    {
      ...cssRule,
      use: [cssRule.use[0], cssRule.use[2], cssRule.use[3]],
    },
  ]
  config.resolve = base.resolve
  config.plugins = config.plugins.concat(base.plugins)
  return config
}
