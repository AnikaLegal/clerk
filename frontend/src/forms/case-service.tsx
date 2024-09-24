import { Field, Formik } from 'formik'
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
import {
  choiceToOptions,
  getAPIErrorMessage,
  getAPIFormErrors,
  filterEmpty,
} from 'utils'

export const ServiceForm: React.FC<CaseDetailFormProps> = ({
  issue,
  onCancel,
  choices,
}) => {
  const [createService] = useCreateCaseServiceMutation()

  const submitService = (values, { setSubmitting, setErrors }) => {
    createService({ id: issue.id, serviceCreate: filterEmpty(values) })
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
        initialValues={{}}
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
        }) => {
          const handleChange = (e, { name, value }) =>
            setFieldValue(name, value, false)

          return (
            <Form
              onSubmit={handleSubmit}
              error={Object.keys(errors).length > 0}
            >
              <Field
                as={Dropdown}
                fluid
                selection
                name="category"
                loading={isSubmitting}
                placeholder="Select the service category"
                options={choiceToOptions(choices.service.category)}
                onChange={(e, data) => {
                  handleChange(e, data)
                  setFieldValue('type', '')
                  setFieldValue('count', 1)
                }}
                style={{ marginBottom: '1rem' }}
              />
              {errors.category && (
                <Message error>
                  <p>{errors.category}</p>
                </Message>
              )}
              {values.category && (
                <>
                  <Field
                    as={Dropdown}
                    fluid
                    selection
                    name="type"
                    loading={isSubmitting}
                    placeholder="Select the service type"
                    options={choiceToOptions(
                      choices.service['type_' + values.category]
                    )}
                    onChange={handleChange}
                  />
                  {values.category == 'DISCRETE' ? (
                    <>
                      <DateInput
                        name="started_at"
                        dateFormat="DD/MM/YYYY"
                        autoComplete="off"
                        placeholder="Date"
                        onChange={handleChange}
                        value={values.started_at}
                        style={{ marginTop: '1rem' }}
                      />
                      <Input
                        fluid
                        name="count"
                        type="number"
                        min="1"
                        placeholder="Count"
                        onChange={handleChange}
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
                        onChange={handleChange}
                        value={values.started_at}
                        style={{ marginTop: '1rem' }}
                      />
                      <DateInput
                        name="finished_at"
                        dateFormat="DD/MM/YYYY"
                        autoComplete="off"
                        placeholder="Finish date"
                        onChange={handleChange}
                        value={values.finished_at}
                      />
                    </>
                  )}
                  <TextArea
                    disabled={isSubmitting}
                    rows={2}
                    placeholder="Add a note"
                    onChange={(e) => setFieldValue('notes', e.target.value)}
                    value={values.notes}
                    style={{ marginBottom: '1rem' }}
                  />
                  {Object.entries(errors).map(([k, v]) => (
                    <Message error key={k}>
                      <div className="header">{k}</div>
                      <p>{v}</p>
                    </Message>
                  ))}
                </>
              )}
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
          )
        }}
      </Formik>
    </Segment>
  )
}
