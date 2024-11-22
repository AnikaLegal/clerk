const glob = require('glob')
const path = require('path')
const webpack = require('webpack')
const BundleTracker = require('webpack-bundle-tracker')
const ReactRefreshWebpackPlugin = require('@pmmmwh/react-refresh-webpack-plugin')
const MiniCssExtractPlugin = require('mini-css-extract-plugin')
const CssMinimizerPlugin = require("css-minimizer-webpack-plugin");

const entry = glob
  .sync('./src/pages/*.{js,jsx,ts,tsx}')
  .map((s) => [s.split('/').pop().split('.')[0], s])
  .reduce((acc, val) => ({ ...acc, [val[0]]: val[1] }), {})
const config = {
  entry,
  output: {
    path: '/build/bundles',
    filename: '[name].[chunkhash].js',
  },
  plugins: [
    new webpack.NoEmitOnErrorsPlugin(),
    new MiniCssExtractPlugin(),
    new CssMinimizerPlugin(),
    new BundleTracker({
      path: '/build',
      filename: 'webpack-stats.json',
    }),
  ],
  resolve: {
    extensions: ['*', '.js', '.jsx', '.ts', '.tsx'],
    modules: [
      path.resolve(__dirname, 'src'),
      path.resolve(__dirname, 'node_modules'),
    ],
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx|ts|tsx)$/,
        exclude: /node_modules/,
        use: ['babel-loader'],
      },
      {
        test: /\.css$/i,
        use: [MiniCssExtractPlugin.loader, 'css-loader', 'postcss-loader'],
      },
    ],
  },
}

module.exports = (env, argv) => {
  const isDevelopment = argv.mode === 'development'
  if (isDevelopment) {
    // Setup dev server for hot reload
    config.devtool = 'inline-source-map'
    config.devServer = {
      port: 3000,
      host: '0.0.0.0',
      hot: true,
      headers: { 'Access-Control-Allow-Origin': '*' },
    }
    config.output = {
      publicPath: 'http://localhost:3000/build/',
    }
    // Add React refresh plugin.
    config.plugins = [
      ...config.plugins,
      new webpack.HotModuleReplacementPlugin(),
      new ReactRefreshWebpackPlugin(),
    ]
  } else {
    config.devtool = 'source-map'
    config.optimization = {
      splitChunks: {
        chunks: 'all',
      },
      minimizer: [
        `...`,
        new CssMinimizerPlugin(),
      ],
      minimize: true,
    }
  }
  return config
}