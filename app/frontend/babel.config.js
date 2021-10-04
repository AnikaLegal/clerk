const presets = ["@babel/preset-react"];
const plugins = [];

if (process.env["ENV"] === "DEV") {
  plugins.push("react-refresh/babel");
}

module.exports = { presets, plugins };
