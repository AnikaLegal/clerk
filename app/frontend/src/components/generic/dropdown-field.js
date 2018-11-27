import React from 'react'

export default ({ label, placeholder, value, onChange, options, disabled, readOnly }) => (
  <div className="input-group">
    <div className="input-group-prepend">
      <span className="input-group-text">{label}</span>
    </div>
    <select disabled={disabled} className="form-control" onChange={onChange} value={value} readOnly={readOnly}>
      {!value && <option value="">{placeholder}</option>}
      {options.map(([val, display]) => (
        <option key={val} value={val}>
          {display}
        </option>
      ))}
    </select>
  </div>
)
