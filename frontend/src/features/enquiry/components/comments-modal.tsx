import {
  Button,
  Group,
  Modal,
  NumberInput,
  Text,
  Textarea,
} from '@mantine/core'
import { Call, Contact, EnquiryUpdate } from 'api'
import React, { useState } from 'react'

interface CommentsModalProps {
  opened: boolean
  record: Call | Contact
  subtitle: string
  onClose: () => void
  onSave: (update: EnquiryUpdate) => Promise<unknown>
}

const CommentsModal = ({
  opened,
  record,
  subtitle,
  onClose,
  onSave,
}: CommentsModalProps) => (
  <Modal
    opened={opened}
    onClose={onClose}
    size="lg"
    title={
      <>
        Update enquiry
        <Text component="div" c="dimmed" size="sm" fw={400} mt={4}>
          {subtitle}
        </Text>
      </>
    }
  >
    {/* Remount on each open so the form starts from the saved values. */}
    {opened && (
      <CommentsForm record={record} onClose={onClose} onSave={onSave} />
    )}
  </Modal>
)

const CommentsForm = ({
  record,
  onClose,
  onSave,
}: Omit<CommentsModalProps, 'opened' | 'subtitle'>) => {
  const [comments, setComments] = useState(record.comments)
  const [attempts, setAttempts] = useState<number>(record.number_callbacks)
  const [isSaving, setIsSaving] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setIsSaving(true)
    // Send attempts only when edited, so this can't overwrite an attempt
    // logged from the row while the modal was open.
    const update: EnquiryUpdate = { comments }
    if (attempts !== record.number_callbacks) {
      update.number_callbacks = attempts
    }
    onSave(update)
      .then(onClose)
      .catch(() => setIsSaving(false))
  }

  return (
    <form autoComplete="off" onSubmit={handleSubmit}>
      <NumberInput
        label="Callbacks"
        size="md"
        w={140}
        autoComplete="off"
        min={0}
        allowDecimal={false}
        allowNegative={false}
        value={attempts}
        onChange={(value) => setAttempts(Number(value) || 0)}
      />
      <Textarea
        label="Comments"
        size="md"
        mt="md"
        autoComplete="off"
        autosize
        minRows={4}
        value={comments}
        onChange={(e) => setComments(e.currentTarget.value)}
      />
      <Group justify="right" mt="lg">
        <Button
          variant="default"
          size="md"
          onClick={onClose}
          disabled={isSaving}
        >
          Close
        </Button>
        <Button type="submit" size="md" loading={isSaving}>
          Update enquiry
        </Button>
      </Group>
    </form>
  )
}

export default CommentsModal
