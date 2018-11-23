import React from 'react'

export default ({ errors }) => (
  <div>
    {errors.map(msg => (
      <div key={msg} className="alert alert-danger">
        {msg}
      </div>
    ))}
  </div>
)
