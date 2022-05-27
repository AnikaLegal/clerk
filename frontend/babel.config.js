const presets = ["@babel/preset-react"];
const plugins = ["@babel/transform-runtime", "babel-plugin-styled-components"];

module.exports = (api) => {
  api.cache(true);
  return { presets, plugins };
};
