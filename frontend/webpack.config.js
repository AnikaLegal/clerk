const glob = require("glob");
const path = require("path");
const webpack = require("webpack");
const BundleTracker = require("webpack-bundle-tracker");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");

const baseConfig = {
  plugins: [new webpack.NoEmitOnErrorsPlugin(), new MiniCssExtractPlugin()],
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

const clientConfig = {
  ...baseConfig,
  target: "web",
  entry: glob
    .sync("./src/pages/*.js")
    .map((s) => [s.split("/").pop().split(".")[0], s])
    .reduce((acc, val) => ({ ...acc, [val[0]]: val[1] }), {}),
  output: {
    path: "/build/bundles",
    filename: "[name].[chunkhash].js",
  },
  plugins: [
    ...baseConfig.plugins,
    new BundleTracker({ filename: "/build/webpack-stats.json" }),
  ],
};
const serverConfig = {
  ...baseConfig,
  target: "node",
  entry: {
    server: path.resolve(__dirname, "src/server.js"),
  },
  output: {
    path: "/build/",
    filename: "[name].js",
  },
};

module.exports = (env, argv) => {
  const isDevelopment = argv.mode === "development";
  if (isDevelopment) {
    clientConfig.devtool = "inline-source-map";
    clientConfig.output.filename = "[name].js";
  }
  return [clientConfig, serverConfig];
};
