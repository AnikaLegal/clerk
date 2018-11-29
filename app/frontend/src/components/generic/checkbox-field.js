import React from 'react'

// Pretend the click event is getting fired
const onClick = (onChange, value) => e =>
  onChange({ target: { value: !value } })

export default ({ label, value, onChange, disabled }) => (
  <div
    style={{ userSelect: 'none' }}
    className="form-group form-check"
    onClick={onClick(onChange, value)}
  >
    <input
      disabled={disabled}
      type="checkbox"
      className="form-check-input"
      checked={value}
      readOnly
    />
    <label className="form-check-label">{label}</label>
  </div>
)
