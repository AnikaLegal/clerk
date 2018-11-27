import React from 'react'
import classNames from 'classnames/bind'

import styles from 'styles/generic/fade-in.module.scss'
const cx = classNames.bind(styles)

const FadeIn = ({ children, duration, className }) => (
  <div
    className={cx('wrapper', className)}
    style={{ animationDuration: `${duration}s` }}
  >
    {children}
  </div>
)
FadeIn.defaultProps = {
  duration: '0.2',
}

export default FadeIn
