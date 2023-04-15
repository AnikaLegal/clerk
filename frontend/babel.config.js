const presets = ['@babel/preset-react', "@babel/preset-typescript"]
const plugins = ['@babel/transform-runtime', 'babel-plugin-styled-components']

module.exports = (api) => {
  if (api.env('development')) {
    plugins.push('react-refresh/babel')
  }
  return { presets, plugins }
}
