import React from 'react'
import { Button, Modal } from 'semantic-ui-react'

interface DiscardChangesConfirmationModalProps {
  open: boolean
  onConfirm: () => void
  onCancel: () => void
}

export const DiscardChangesConfirmationModal = ({
  open,
  onConfirm,
  onCancel,
}: DiscardChangesConfirmationModalProps) => {
  return (
    <Modal size="mini" open={open} onClose={null}>
      <Modal.Header>Discard changes?</Modal.Header>
      <Modal.Content>
        Change that you have made will not be saved.
      </Modal.Content>
      <Modal.Actions>
        <Button negative onClick={onConfirm}>
          Discard changes
        </Button>
        <Button onClick={onCancel}>Keep changes</Button>
      </Modal.Actions>
    </Modal>
  )
}
