export const theme = {
  screen: {
    half: '1440px',
    mobile: '1220px',
    small: '350px',
  },
  color: {
    white: '#fff',
    marigold: '#FFE1A6',
    green: '#476261',
    teal: {
      primary: '#06879A',
      secondary: '#5DB5B3',
      tertiary: '#98D0CE',
      quaternary: '#CEE9E8',
      quinary: '#EFF7F7',
    },
    error: {
      primary: '#B56576',
      secondary: '#FFDBE3',
    },
    grey: {
      dark: '#3D3D3D',
      mid: '#929292',
      light: '#E8E8E8',
    },
  },
  text: {
    title: '1.2rem',
    subtitle: '1rem',
  },
  shadow:
    '0px 10px 20px rgba(0, 0, 0, 0.06), 0px 2px 6px rgba(0, 0, 0, 0.04), 0px 0px 1px rgba(0, 0, 0, 0.04);',
  switch: (args: { [key: string]: string }) => (props: Object) => {
    let s = ''
    for (const k in args) {
      if (props[k]) {
        s += args[k]
      }
    }
    return s
  },
}
