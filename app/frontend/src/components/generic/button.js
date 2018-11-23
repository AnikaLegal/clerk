import React from 'react'

export default ({ onClick, children, disabled, className, btnStyle }) => (
  <button className={`btn btn-${btnStyle || 'primary'} mb-2 ${className}`} onClick={onClick} disabled={disabled}>
    {children}
  </button>
)
