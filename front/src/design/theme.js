// @flow
export const theme = {
  screen: {
    mobile: '600px',
  },
  color: {
    teal: '#06879A',
    tealDark: '#138799',
    tealLight: '#5DB5B3',
    tealInactive: '#CEE9E8',
    tealExtraLight: '#98D0CE',
    marigold: '#FFE1A6',
    white: '#fff',
    text: '#3D3D3D',
    textLight: '#929292',
    textDarkGreen: '#476261',
    error: '#FFDBE3',
    textError: '#B56576',
  },
  text: {
    title: '24px',
    subtitle: '20px',
  },
  shadow:
    '0px 10px 20px rgba(0, 0, 0, 0.06), 0px 2px 6px rgba(0, 0, 0, 0.04), 0px 0px 1px rgba(0, 0, 0, 0.04);',
  switch: (args: { [string]: string }) => (props: Object) => {
    let s = ''
    for (const k in args) {
      if (props[k]) {
        s += args[k]
      }
    }
    return s
  },
}
