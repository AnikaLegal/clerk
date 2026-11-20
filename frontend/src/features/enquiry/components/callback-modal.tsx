import { Button, Group, Modal, Text, Textarea, TextInput } from '@mantine/core'
import { useForm } from '@mantine/form'
import api, { CallbackCreate, Enquiry } from 'api'
import { yupResolver } from 'mantine-form-yup-resolver'
import { enqueueSnackbar } from 'notistack'
import React from 'react'
import { getAPIErrorMessage } from 'utils'
import { CallbackFormValues, CallbackSchema } from '../schema'

export interface CallbackModalTarget {
  enquiry: Enquiry
  isAnswered: boolean
  // Shown under the title so staff can see who they're logging for.
  details: string
}

interface CallbackModalProps {
  target: CallbackModalTarget | null
  onClose: () => void
}

export const CallbackModal = ({ target, onClose }: CallbackModalProps) => (
  <Modal
    opened={target !== null}
    onClose={onClose}
    size="lg"
    title={
      target && (
        <>
          <Text fw={700} fz="lg">
            {target.isAnswered ? 'Log answered call' : 'Log missed call'}
          </Text>
          <Text c="dimmed" fz="sm" mt={4}>
            {target.details}
          </Text>
        </>
      )
    }
  >
    {/* Keyed so each opening starts from a fresh form. */}
    {target && (
      <CallbackForm
        key={`${target.enquiry.id}-${target.isAnswered}`}
        target={target}
        onClose={onClose}
      />
    )}
  </Modal>
)

const CallbackForm = ({
  target,
  onClose,
}: {
  target: CallbackModalTarget
  onClose: () => void
}) => {
  const { enquiry, isAnswered } = target
  // Contact form submissions already hold the name and email they gave.
  const isCall = enquiry.source === 'CALL'
  const [createCallback] = api.useCreateCallbackMutation()
  const form = useForm<CallbackFormValues>({
    mode: 'uncontrolled',
    validate: yupResolver(CallbackSchema),
    initialValues: {
      name: enquiry.name,
      email: enquiry.email,
      purpose: '',
      summary: '',
      action_items: '',
    },
  })

  const handleSubmit = (values: CallbackFormValues) => {
    const callbackCreate: CallbackCreate = {
      enquiry: enquiry.id,
      is_answered: isAnswered,
      summary: values.summary,
    }
    if (isAnswered) {
      callbackCreate.purpose = values.purpose
      callbackCreate.action_items = values.action_items
      if (isCall) {
        callbackCreate.name = values.name
        callbackCreate.email = values.email
      }
    }
    return createCallback({ callbackCreate })
      .unwrap()
      .then(() => {
        enqueueSnackbar('Callback logged', { variant: 'success' })
        onClose()
      })
      .catch((e) =>
        enqueueSnackbar(getAPIErrorMessage(e, 'Failed to log callback'), {
          variant: 'error',
        })
      )
  }

  return (
    <form autoComplete="off" onSubmit={form.onSubmit(handleSubmit)}>
      {isAnswered && isCall && (
        <>
          <TextInput
            {...form.getInputProps('name')}
            key={form.key('name')}
            label="Caller's name"
            size="md"
            autoComplete="off"
          />
          <TextInput
            {...form.getInputProps('email')}
            key={form.key('email')}
            label="Email (if needed)"
            description="If we need to contact the caller again, consider getting their email address."
            size="md"
            mt="md"
            autoComplete="off"
          />
        </>
      )}
      {isAnswered && (
        <Textarea
          {...form.getInputProps('purpose')}
          key={form.key('purpose')}
          label="Purpose of the call"
          size="md"
          mt={isCall ? 'md' : 0}
          autosize
          minRows={2}
          autoComplete="off"
        />
      )}
      <Textarea
        {...form.getInputProps('summary')}
        key={form.key('summary')}
        label={isAnswered ? 'Summary of the call' : 'Note'}
        placeholder={isAnswered ? undefined : 'For example, left a voicemail'}
        size="md"
        mt={isAnswered ? 'md' : 0}
        autosize
        minRows={2}
        autoComplete="off"
        data-autofocus={!isAnswered || undefined}
      />
      {isAnswered && (
        <Textarea
          {...form.getInputProps('action_items')}
          key={form.key('action_items')}
          label="Action items"
          size="md"
          mt="md"
          autosize
          minRows={2}
          autoComplete="off"
        />
      )}
      <Group justify="right" mt="lg">
        <Button
          variant="default"
          onClick={onClose}
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
          Log callback
        </Button>
      </Group>
    </form>
  )
}
