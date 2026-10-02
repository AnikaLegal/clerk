import { Modal, ModalProps } from '@mantine/core'
import React from 'react'
import { ServiceForm, ServiceFormProps } from './service-form'

interface ServiceFormModalProps extends ServiceFormProps {
  modal: Omit<ModalProps, 'onClose'>
}

export const ServiceFormModal = ({
  modal,
  onCancel,
  ...props
}: ServiceFormModalProps) => {
  return (
    <Modal
      opened={modal.opened}
      title={modal.title}
      onClose={onCancel}
      size="lg"
    >
      <ServiceForm onCancel={onCancel} {...props} />
    </Modal>
  )
}
