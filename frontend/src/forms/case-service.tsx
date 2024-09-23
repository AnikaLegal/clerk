import { Formik } from 'formik'
import moment from 'moment'
import { enqueueSnackbar } from 'notistack'
import React from 'react'
import {
  Button,
  Dropdown,
  Form,
  Header,
  Input,
  Message,
  Segment,
} from 'semantic-ui-react'

import { ServiceCreate, useCreateCaseServiceMutation } from 'api'
import DateInput from 'comps/date-input'
import { TextArea } from 'comps/textarea'
import { CaseDetailFormProps } from 'types'
import { choiceToOptions, getAPIErrorMessage, getAPIFormErrors } from 'utils'

export const ServiceForm: React.FC<CaseDetailFormProps> = ({
  issue,
  onCancel,
  choices,
}) => {
  const [createService] = useCreateCaseServiceMutation()

  const submitService = (values, { setSubmitting, setErrors }) => {
    createService({ id: issue.id, serviceCreate: values })
      .unwrap()
      .then(() => {
        setSubmitting(false)
        enqueueSnackbar('Service created', { variant: 'success' })
      })
      .catch((err) => {
        enqueueSnackbar(getAPIErrorMessage(err, 'Failed to create service'), {
          variant: 'error',
        })
        const requestErrors = getAPIFormErrors(err)
        if (requestErrors) {
          setErrors(requestErrors)
        }
        setSubmitting(false)
      })
  }
  return (
    <Segment>
      <Header>Add a service</Header>
      <p>
        Record a unit of work to facilitate the collection of consistent and
        comparable data.
      </p>
      <p>
        Consistent and comparable data collection provides the foundation for a
        strong, reliable evidence base that informs legal assistance policy and
        supports planning and resource allocation decisions to ensure that
        limited resources are directed to areas where services will have the
        greatest benefit.
      </p>
      <Formik
        initialValues={{
          category: '',
          type: '',
          started_at: '',
          notes: '',
        }}
        onSubmit={submitService}
      >
        {({
          values,
          errors,
          handleSubmit,
          isSubmitting,
          setFieldValue,
        }: {
          values: ServiceCreate
          errors: any
          handleSubmit: any
          isSubmitting: any
          setFieldValue: any
        }) => (
          <Form onSubmit={handleSubmit} error={Object.keys(errors).length > 0}>
            <Dropdown
              fluid
              selection
              loading={isSubmitting}
              placeholder="Select the service category"
              options={choiceToOptions(choices.service.category)}
              onChange={(e, { value }) => {
                setFieldValue('category', value, false)
                setFieldValue('type', '', false)
              }}
              style={{ marginBottom: '1rem' }}
            />
            {values.category && (
              <>
                <Dropdown
                  name="type"
                  fluid
                  selection
                  loading={isSubmitting}
                  placeholder="Select the service type"
                  options={
                    values.category
                      ? choiceToOptions(
                          choices.service['type_' + values.category]
                        )
                      : []
                  }
                  onChange={(e, { name, value }) =>
                    setFieldValue(name, value, false)
                  }
                />
                {values.category == 'DISCRETE' ? (
                  <>
                    <DateInput
                      name="started_at"
                      dateFormat="DD/MM/YYYY"
                      autoComplete="off"
                      placeholder="Date"
                      onChange={(e, { name, value }) =>
                        setFieldValue(name, value, false)
                      }
                      value={values.started_at}
                      style={{ marginTop: '1rem' }}
                    />
                    <Input
                      fluid
                      name="count"
                      type="number"
                      min="1"
                      placeholder="Count"
                      onChange={(e, { name, value }) =>
                        setFieldValue(name, value, false)
                      }
                      value={values.count}
                      style={{ marginBottom: '1rem' }}
                    />
                  </>
                ) : (
                  <>
                    <DateInput
                      name="started_at"
                      dateFormat="DD/MM/YYYY"
                      autoComplete="off"
                      placeholder="Start date"
                      onChange={(e, { name, value }) =>
                        setFieldValue(name, value, false)
                      }
                      value={values.started_at}
                      style={{ marginTop: '1rem' }}
                    />
                    <DateInput
                      name="finished_at"
                      dateFormat="DD/MM/YYYY"
                      autoComplete="off"
                      placeholder="Finish date"
                      onChange={(e, { name, value }) =>
                        setFieldValue(name, value, false)
                      }
                      value={values.finished_at}
                    />
                  </>
                )}
                <TextArea
                  onChange={(e) => setFieldValue('notes', e.target.value)}
                  disabled={isSubmitting}
                  rows={2}
                  placeholder="Add a note"
                  value={values.notes}
                  style={{ marginBottom: '1rem' }}
                />
              </>
            )}
            {Object.entries(errors).map(([k, v]) => (
              <Message error key={k}>
                <div className="header">{k}</div>
                <p>{v}</p>
              </Message>
            ))}
            <Button
              loading={isSubmitting}
              disabled={isSubmitting}
              positive
              type="submit"
            >
              Create service
            </Button>
            <Button disabled={isSubmitting} onClick={onCancel}>
              Close
            </Button>
          </Form>
        )}
      </Formik>
    </Segment>
  )
}
