import { Modal, ModalProps } from '@mantine/core'
import { DateForm, DateFormProps } from 'features/date'
import React from 'react'

interface DateFormModalProps extends DateFormProps {
  modal: Omit<ModalProps, 'onClose'>
}

const DateFormModal = ({
  input,
  onSubmit,
  onCancel,
  controls,
  modal,
}: DateFormModalProps) => {
  return (
    <Modal
      opened={modal.opened}
      title={modal.title}
      onClose={onCancel}
      size="lg"
    >
      <DateForm
        input={{
          initialValues: input.initialValues,
        }}
        onSubmit={onSubmit}
        onCancel={onCancel}
        controls={controls}
      />
    </Modal>
  )
}

export default DateFormModal
