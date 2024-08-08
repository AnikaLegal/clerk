import React, { useState } from 'react'
import { Formik } from 'formik'
import { Header, Form, Button, Message, Segment } from 'semantic-ui-react'
import moment from 'moment'
import { useSnackbar } from 'notistack'

import { CaseDetailFormProps } from 'types/case'
import { getAPIErrorMessage, getAPIFormErrors } from 'utils'
import { useCreateCaseNoteMutation } from 'api'
import { TextArea } from 'comps/textarea'
import { TimelineNote } from 'comps/timeline-item'
import { MarkdownExplainer } from 'comps/markdown-editor'

export const FilenoteForm: React.FC<CaseDetailFormProps> = ({
  issue,
  onCancel,
}) => {
  const [isSuccess, setSuccess] = useState(false)
  const [createCaseNote] = useCreateCaseNoteMutation()
  const { enqueueSnackbar } = useSnackbar()

  const submitNote = (values, { setSubmitting, setErrors }) => {
    const note = { ...values }
    note.event = note.event
      ? moment.utc(values.event, 'DD/MM/YYYY').format()
      : note.event
    createCaseNote({ id: issue.id, issueNoteCreate: note })
      .unwrap()
      .then(() => {
        setSubmitting(false)
        setSuccess(true)
        enqueueSnackbar('File note created', { variant: 'success' })
      })
      .catch((err) => {
        enqueueSnackbar(
          getAPIErrorMessage(err, 'Failed to create a file note'),
          {
            variant: 'error',
          }
        )
        const requestErrors = getAPIFormErrors(err)
        if (requestErrors) {
          setErrors(requestErrors)
        }
        setSubmitting(false)
      })
  }
  return (
    <Segment>
      <Header>Add a file note</Header>
      <p>
        Leave a note of important case information, events or instructions. This
        note is visible to everybody who has access to the case.
      </p>
      <Formik
        initialValues={{ text: '', note_type: 'PARALEGAL' }}
        validate={({ text }) =>
          text ? null : { 'File note text': 'File note cannot be empty' }
        }
        onSubmit={submitNote}
      >
        {({ values, errors, handleSubmit, isSubmitting, setFieldValue }) => (
          <Form
            onSubmit={handleSubmit}
            success={isSuccess}
            error={Object.keys(errors).length > 0}
          >
            <TextArea
              onChange={(e) => setFieldValue('text', e.target.value)}
              disabled={isSubmitting}
              rows={3}
              placeholder="Write case details here"
              value={values.text}
              style={{ marginBottom: '1em' }}
            />
            {Object.entries(errors).map(([k, v]) => (
              <Message error key={k}>
                <div className="header">{k}</div>
                <p>{v as string}</p>
              </Message>
            ))}
            <Button
              loading={isSubmitting}
              disabled={isSubmitting}
              positive
              type="submit"
            >
              Create note
            </Button>
            <Button disabled={isSubmitting} onClick={onCancel}>
              Close
            </Button>
            <Message success>File note created</Message>
            <MarkdownExplainer />
            <TimelineNote
              note={{
                note_type: values.note_type,
                created_at: 'Now',
                text_display: values.text || 'start typing...',
                creator: {
                  full_name: 'You',
                },
              }}
            />
          </Form>
        )}
      </Formik>
    </Segment>
  )
}
