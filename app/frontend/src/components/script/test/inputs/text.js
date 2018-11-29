import React from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames/bind'
import styles from 'styles/test/text.module.scss'

const cx = classNames.bind(styles)

const TextInput = ({ prompt, value, onChange, autoFocus }) => (
  <div className={cx('wrapper')}>
    <div className={cx('prompt')}>{prompt}</div>
    <input
      type="text"
      className={cx('input')}
      autoFocus={autoFocus}
      value={value}
      onChange={onChange}
    />
  </div>
)
TextInput.propTypes = {
  prompt: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  autoFocus: PropTypes.bool,
}
TextInput.defaultProps = {
  autoFocus: false,
}

export default TextInput
