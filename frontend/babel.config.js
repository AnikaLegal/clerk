const presets = ["@babel/preset-react"];
const plugins = [];

module.exports = (api) => {
  if (api.env("development")) {
    plugins.push("react-refresh/babel");
  }
  return { presets, plugins };
};
