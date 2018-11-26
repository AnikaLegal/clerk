import React from 'react'
import PropTypes from 'prop-types'

import Modal from 'components/generic/modal'
import Button from 'components/generic/button'
import styles from 'styles/modals/error.module.scss'

const DEFAULT_ERROR = { error: ['Something went wrong.'] }

const ErrorModal = ({ onClose, errors }) => (
  <Modal zIndex={100}>
    <h2>Web Request Error</h2>
    <div className={styles.message}>
      {Object.entries(errors || DEFAULT_ERROR).map(([name, messages]) => (
        <div key={name}>
          {name.toUpperCase()}:{messages.reduce((str, msg) => `${str} ${msg}`, '')}
        </div>
      ))}
    </div>
    <Button onClick={onClose}>close</Button>
  </Modal>
)

ErrorModal.propTypes = {
  onClose: PropTypes.func.isRequired,
  errors: PropTypes.object.isRequired,
}

export default ErrorModal
