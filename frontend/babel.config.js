const presets = ["@babel/preset-react"];
const plugins = ["@babel/transform-runtime"];

module.exports = (api) => {
  if (api.env("development")) {
    plugins.push("react-refresh/babel");
  }
  return { presets, plugins };
};