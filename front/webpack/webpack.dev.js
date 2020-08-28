const path = require('path')
const webpack = require('webpack')
const base = require('./webpack.base.js')
const ReactRefreshWebpackPlugin = require('@pmmmwh/react-refresh-webpack-plugin')
const babel = require('./babel.js')

module.exports = {
  ...base,
  mode: 'development',
  devtool: 'inline-source-map',
  optimization: {
    minimize: false,
  },
  output: {
    publicPath: 'http://localhost:3000/build/',
  },
  module: {
    rules: [...base.module.rules, babel(true)],
  },
  devServer: {
    port: 3000,
    hot: true,
    headers: { 'Access-Control-Allow-Origin': '*' },
  },
  plugins: [
    ...base.plugins,
    new webpack.HotModuleReplacementPlugin(),
    new ReactRefreshWebpackPlugin(),
    new webpack.DefinePlugin({
      SENTRY_JS_DSN: JSON.stringify(''),
      SENTRY_RELEASE: JSON.stringify(''),
      GA_ID: JSON.stringify(''),
    }),
  ],
}
