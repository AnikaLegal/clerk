import { Button, Group } from '@mantine/core'
import React from 'react'
import { ServiceFormControlProps } from './service-form'

const ModalControls = ({
  form,
  onCancel,
  verb,
}: ServiceFormControlProps & { verb: string }) => (
  <Group justify="right" mt="lg">
    <Button
      variant="default"
      onClick={onCancel}
      disabled={form.submitting}
      size="md"
    >
      Close
    </Button>
    <Button
      type="submit"
      disabled={form.submitting}
      loading={form.submitting}
      size="md"
    >
      {verb} {form.getValues().category.toLowerCase()} service
    </Button>
  </Group>
)

export const AddServiceControls = (props: ServiceFormControlProps) => (
  <ModalControls {...props} verb="Add" />
)

export const UpdateServiceControls = (props: ServiceFormControlProps) => (
  <ModalControls {...props} verb="Update" />
)
