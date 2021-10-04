const base = require("./webpack.base.js");
const webpack = require("webpack");
const ReactRefreshWebpackPlugin = require("@pmmmwh/react-refresh-webpack-plugin");

module.exports = {
  ...base,
  mode: "development",
  devtool: "inline-source-map",
  output: {
    publicPath: `http://0.0.0.0:3000/build/`,
  },
  module: {
    rules: [
      // Webpack reads JavaScript with Babel
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: ["babel-loader"],
      },
    ],
  },
  devServer: {
    port: 3000,
    host: "0.0.0.0",
    hot: true,
    headers: { "Access-Control-Allow-Origin": "*" },
  },
  optimization: {
    minimize: false,
  },
  plugins: [...base.plugins, new ReactRefreshWebpackPlugin()],
};
