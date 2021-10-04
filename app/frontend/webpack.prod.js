const base = require("./webpack.base.js");
const path = require("path");

module.exports = {
  ...base,
  mode: "production",
  devtool: "source-map",
  // Where Webpack spits out the results (the myapp static folder)
  output: {
    path: path.resolve("/app/case/static/build/"),
    filename: "[name].js",
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
  optimization: {
    minimize: true,
  },
};
