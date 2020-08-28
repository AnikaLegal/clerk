const babelOptions = {
  presets: [
    [
      '@babel/preset-env',
      {
        targets: '> 0.25%, not dead',
      },
    ],
    '@babel/preset-react',
    '@babel/preset-flow',
  ],
  plugins: ['@babel/transform-runtime', 'babel-plugin-styled-components'],
}

module.exports = (isDev) => ({
  test: /\.js$/,
  exclude: /node_modules/,
  use: [
    {
      loader: 'babel-loader',
      options: isDev
        ? {
            ...babelOptions,
            plugins: [...babelOptions.plugins, 'react-refresh/babel'],
          }
        : babelOptions,
    },
  ],
})
