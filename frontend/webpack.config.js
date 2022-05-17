const glob = require("glob");
const path = require("path");
const webpack = require("webpack");
const BundleTracker = require("webpack-bundle-tracker");
const ReactRefreshWebpackPlugin = require("@pmmmwh/react-refresh-webpack-plugin");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");

const entry = glob
  .sync("./src/pages/*.js")
  .map((s) => [s.split("/").pop().split(".")[0], s])
  .reduce((acc, val) => ({ ...acc, [val[0]]: val[1] }), {});
const config = {
  entry,
  output: {
    path: "/build/bundles",
    filename: "[name].[chunkhash].js",
  },
  plugins: [
    new webpack.NoEmitOnErrorsPlugin(),
    new MiniCssExtractPlugin(),
    new BundleTracker({ filename: "/build/webpack-stats.json" }),
  ],
  resolve: {
    extensions: ["*", ".js", ".jsx"],
    modules: [
      path.resolve(__dirname, "src"),
      path.resolve(__dirname, "node_modules"),
    ],
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: ["babel-loader"],
      },
      {
        test: /\.css$/i,
        use: [MiniCssExtractPlugin.loader, "style-loader", "css-loader"],
      },
    ],
  },
};

module.exports = (env, argv) => {
  const isDeveopment = argv.mode === "development";
  if (isDeveopment) {
    // Setup dev server for hot reload
    config.devtool = "inline-source-map";
    config.devServer = {
      port: 3000,
      host: "0.0.0.0",
      hot: true,
      headers: { "Access-Control-Allow-Origin": "*" },
    };
    config.output = {
      publicPath: "http://0.0.0.0:3000/build/",
    };
    // Add React refresh plugin.
    config.plugins = [
      ...config.plugins,
      new webpack.HotModuleReplacementPlugin(),
      new ReactRefreshWebpackPlugin(),
    ];
  }
  return config;
};
