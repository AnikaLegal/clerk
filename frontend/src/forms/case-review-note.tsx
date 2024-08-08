import React, { useState } from 'react'
import { Formik } from 'formik'
import { Header, Form, Button, Message, Segment } from 'semantic-ui-react'
import DateInput from 'comps/date-input'
import moment from 'moment'
import { useSnackbar } from 'notistack'

import { TimelineNote } from 'comps/timeline-item'
import { MarkdownExplainer } from 'comps/markdown-editor'
import { TextArea } from 'comps/textarea'
import { useCreateCaseNoteMutation } from 'api'
import { getAPIErrorMessage, getAPIFormErrors } from 'utils'
import { CaseDetailFormProps } from 'types/case'

export const ReviewForm: React.FC<CaseDetailFormProps> = ({
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
      <Header> Add a coordinator case review note</Header>
      <p>
        Leave a case review note for other coordinators to read. This note is
        not visible to paralegals.
      </p>
      <Formik
        initialValues={{ text: '', event: '', note_type: 'REVIEW' }}
        validate={({ text, event }) => {
          const errors = {}
          if (!text) errors['text'] = 'File note cannot be empty'
          if (!event) errors['event'] = 'Next review date is required'
          return errors
        }}
        onSubmit={submitNote}
      >
        {({
          values,
          errors,
          handleSubmit,
          isSubmitting,
          setFieldValue,
          touched,
        }) => (
          <Form
            onSubmit={handleSubmit}
            success={isSuccess}
            error={Object.keys(errors).length > 0}
          >
            <TextArea
              onChange={(e) => setFieldValue('text', e.target.value, false)}
              disabled={isSubmitting}
              rows={3}
              value={values.text}
              style={{ marginBottom: '1em' }}
              placeholder="Write your review here (this is not a filenote, paralegals cannot see this)"
            />

            <DateInput
              name="event"
              dateFormat="DD/MM/YYYY"
              autoComplete="off"
              minDate={moment()}
              placeholder="Select a next review date"
              onChange={(e, { name, value }) =>
                setFieldValue(name, value, false)
              }
              value={values.event}
            />
            {Object.entries(errors)
              .filter(([k, v]) => touched[k])
              .map(([k, v]) => (
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
                event: moment(values.event, 'DD/MM/YYYY').format(),
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
