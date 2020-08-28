const webpack = require('webpack')
const TerserPlugin = require('terser-webpack-plugin')
const OptimizeCSSAssetsPlugin = require('optimize-css-assets-webpack-plugin')
const babel = require('./babel.js')
const base = require('./webpack.base.js')

module.exports = {
  ...base,
  mode: 'production',
  devtool: 'source-map',
  output: {
    path: __dirname + '/dist/build',
    filename: '[name].js',
  },
  optimization: {
    minimizer: [
      new TerserPlugin({ sourceMap: true }),
      new OptimizeCSSAssetsPlugin(),
    ],
  },
  module: {
    rules: [...base.module.rules, babel(false)],
  },

  plugins: [
    ...base.plugins,
    new webpack.DefinePlugin({
      SENTRY_JS_DSN: JSON.stringify(process.env.SENTRY_JS_DSN),
      SENTRY_ENV: JSON.stringify(process.env.SENTRY_ENV),
      GA_ID: JSON.stringify(process.env.GA_ID),
    }),
  ],
}
