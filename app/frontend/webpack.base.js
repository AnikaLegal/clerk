const path = require('path')
const webpack = require('webpack')
const BundleTracker = require('webpack-bundle-tracker')
module.exports = {
  // Where Webpack looks to load your JavaScript
  entry: {
    email: path.resolve(__dirname, 'src/email'),
  },
  // Where find modules that can be imported (eg. React)
  resolve: {
    extensions: ['*', '.js', '.jsx'],
    modules: [
      path.resolve(__dirname, 'src'),
      path.resolve(__dirname, 'node_modules'),
    ],
  },
  plugins: [
    // Don't output new files if there is an error
    new webpack.NoEmitOnErrorsPlugin(),
    new BundleTracker({
      path: path.resolve(__dirname),
      filename: 'webpack-bundle.json',
    }),
  ],
}
