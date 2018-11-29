import React from 'react'
import styles from 'styles/generic/modal.module.scss'

const Modal = ({ children, maxWidth, maxHeight, zIndex }) => (
  <div className={styles.wrapper} style={{ zIndex }}>
    <div className={styles.content} style={{ maxWidth, maxHeight, zIndex }}>
      {children}
    </div>
  </div>
)

Modal.defaultProps = {
  maxWidth: null,
  maxHeight: null,
  zIndex: null,
}

export default Modal
