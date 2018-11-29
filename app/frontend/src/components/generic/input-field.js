import React from 'react'
import classNames from 'classnames/bind'
import styles from 'styles/generic/input-field.module.scss'

const cx = classNames.bind(styles)

export default ({
  label,
  type,
  placeholder,
  value,
  onChange,
  autoFocus,
  disabled,
}) => (
  <div className={cx('wrapper')}>
    <div className={cx('label')}>{label}</div>
    <input
      type={type}
      className={cx('input')}
      autoFocus={autoFocus}
      placeholder={placeholder}
      value={value}
      disabled={disabled}
      onChange={onChange}
    />
  </div>
)
