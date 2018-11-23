import React from 'react'

export default ({ label, type, placeholder, value, onChange }) => (
  <div className="input-group">
    <div className="input-group-prepend">
      <span className="input-group-text">{label}</span>
    </div>
    <input type={type} className="form-control" placeholder={placeholder} value={value} onChange={onChange} />
  </div>
)
