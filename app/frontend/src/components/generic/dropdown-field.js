import React from 'react'
import classNames from 'classnames/bind'
import styles from 'styles/generic/dropdown-field.module.scss'

const cx = classNames.bind(styles)

const DropdownField = ({
  label,
  placeholder,
  value,
  onChange,
  options,
  disabled,
  readOnly,
  nullable,
}) => (
  <div className={cx('wrapper')}>
    <div className={cx('label')}>{label}</div>
    <select
      disabled={disabled}
      className={cx('input', { placeholder: !value })}
      onChange={onChange}
      value={value}
      readOnly={readOnly}
    >
      {(!value || nullable) && <option value="">{placeholder}</option>}
      {options.map(([val, display]) => (
        <option key={val} value={val}>
          {display}
        </option>
      ))}
    </select>
  </div>
)
DropdownField.defualtProps = {
  nullable: false,
}

export default DropdownField
