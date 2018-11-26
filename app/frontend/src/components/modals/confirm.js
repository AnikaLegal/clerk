import React from 'react'
import PropTypes from 'prop-types'

import Modal from 'components/generic/modal'
import Button from 'components/generic/button'
import styles from 'styles/modals/confirm.module.scss'


const ConfirmationModal = ({ isVisible, onConfirm, onCancel, children }) => {
  if (!isVisible) return null
  return (
    <Modal maxWidth="500px" maxHeight="290px">
      <div className={styles.message}>
        {children}
      </div>
      <div className={styles.buttons}>
        <Button onClick={onConfirm}>
          Confirm
        </Button>
        <Button btnStyle="danger" onClick={onCancel}>
          Cancel
        </Button>
      </div>
    </Modal>
  )
}
ConfirmationModal.propTypes = {
  isVisible: PropTypes.bool.isRequired,
  onConfirm: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired,
}

export default ConfirmationModal
