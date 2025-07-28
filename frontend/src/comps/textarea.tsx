import React, { useEffect, useState, useRef } from 'react'

export const TextArea = (props) => {
  const textAreaRef = useRef(null)
  const setScrollHeight = () => {
    const el = textAreaRef.current
    if (el && !props.value) {
      el.style.height = ''
    } else if (el && el.scrollHeight > el.clientHeight) {
      el.style.height = el.scrollHeight + 8
    }
  }
  useEffect(() => {
    setScrollHeight()
  }, [props.value])
  return (
    <textarea
      ref={textAreaRef}
      style={{
        overflow: 'hidden',
        resize: 'none !important',
      }}
      {...props}
    />
  )
}
