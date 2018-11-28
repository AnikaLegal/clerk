import React from 'react'
import classNames from 'classnames/bind'
import styles from 'styles/generic/sub-field.module.scss'

const cx = classNames.bind(styles)

// A field that contains a form within it
export default ({ label, className, children }) => (
  <div className={cx('wrapper', className)}>
    <div className={cx('label')}>{label}</div>
    <div className={cx('sub')}>{children}</div>
  </div>
)
