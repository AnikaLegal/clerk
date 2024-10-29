import { useClickOutside, useDebouncedCallback } from '@mantine/hooks'
import api, { Issue, Service, ServiceCreate } from 'api'
import { CASE_TABS, CaseHeader, CaseTabUrls } from 'comps/case-header'
import { RichTextDisplay } from 'comps/rich-text/rich-text-display'
import { Formik, FormikHelpers } from 'formik'
import {
  FormikDiscreteServiceFields,
  FormikOngoingServiceFields,
  FormikServiceErrorMessages,
  ServiceCategory,
} from 'forms/case-service'
import { enqueueSnackbar } from 'notistack'
import React, { useState } from 'react'
import {
  Button,
  ButtonProps,
  Container,
  Form,
  Grid,
  Header,
  Icon,
  IconProps,
  Loader,
  Modal,
  Segment,
  Table,
} from 'semantic-ui-react'
import { CaseFormServiceChoices } from 'types'
import {
  choiceToMap,
  filterEmpty,
  getAPIErrorMessage,
  getAPIFormErrors,
  mount,
} from 'utils'

interface DjangoContext {
  case_pk: string
  choices: CaseFormServiceChoices
  urls: CaseTabUrls
}
const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext
const DISCRETE_TYPE_LABELS = choiceToMap(CONTEXT.choices.type_DISCRETE)
const ONGOING_TYPE_LABELS = choiceToMap(CONTEXT.choices.type_ONGOING)

const App = () => {
  const caseId = CONTEXT.case_pk
  const urls = CONTEXT.urls

  const caseResult = api.useGetCaseQuery({ id: caseId })
  if (caseResult.isFetching) return null

  const issue = caseResult.data!.issue
  return (
    <Container>
      <CaseHeader issue={issue} activeTab={CASE_TABS.SERVICES} urls={urls} />
      <Segment basic>
        <DiscreteServices issue={issue} choices={CONTEXT.choices} />
      </Segment>
      <Segment basic>
        <OngoingServices issue={issue} choices={CONTEXT.choices} />
      </Segment>
    </Container>
  )
}

interface ServiceProps {
  issue: Issue
  choices: CaseFormServiceChoices
}

interface ServiceTableProps {
  issue: Issue
  fields: React.ReactNode
}

export const DiscreteServices = ({ issue, choices }: ServiceProps) => {
  const initialValues = {
    category: ServiceCategory.Discrete,
    count: 1,
    started_at: '',
  } as ServiceCreate
  const fields: React.ReactNode = (
    <FormikDiscreteServiceFields choices={choices} />
  )

  return (
    <>
      <Grid>
        <Grid.Row>
          <Grid.Column style={{ flexGrow: '1' }}>
            <Header as="h2">Discrete services</Header>
          </Grid.Column>
          {issue.is_open && (
            <Grid.Column style={{ width: 'auto' }}>
              <AddServiceButton
                floated="right"
                size="tiny"
                issue={issue}
                initialValues={initialValues}
                fields={fields}
              >
                Add discrete service
              </AddServiceButton>
            </Grid.Column>
          )}
        </Grid.Row>
      </Grid>
      <DiscreteServicesTable issue={issue} fields={fields} />
    </>
  )
}

export const DiscreteServicesTable = ({ issue, fields }: ServiceTableProps) => {
  const result = api.useGetCaseServicesQuery({
    id: issue.id,
    category: ServiceCategory.Discrete,
  })
  if (result.isLoading) {
    return <Loader active inline="centered" />
  }
  if (result.data.length == 0) {
    return (
      <Segment textAlign="center" secondary>
        <p>No discrete services exist for this case.</p>
      </Segment>
    )
  }
  return (
    <Table celled>
      <Table.Header>
        <Table.Row>
          <Table.HeaderCell>Type</Table.HeaderCell>
          <Table.HeaderCell>Date</Table.HeaderCell>
          <Table.HeaderCell>Count</Table.HeaderCell>
          <Table.HeaderCell>Notes</Table.HeaderCell>
          {issue.is_open && <Table.HeaderCell></Table.HeaderCell>}
        </Table.Row>
      </Table.Header>
      <Table.Body>
        {result.data.map((service) => (
          <Table.Row key={service.id}>
            <Table.Cell>{DISCRETE_TYPE_LABELS.get(service.type)}</Table.Cell>
            <Table.Cell>{service.started_at}</Table.Cell>
            <Table.Cell>{service.count}</Table.Cell>
            <Table.Cell>
              <RichTextDisplay content={service.notes} />
            </Table.Cell>
            {issue.is_open && (
              <Table.Cell collapsing textAlign="center">
                <ServiceActionIcons
                  issue={issue}
                  service={service}
                  fields={fields}
                />
              </Table.Cell>
            )}
          </Table.Row>
        ))}
      </Table.Body>
    </Table>
  )
}

export const OngoingServices = ({ issue, choices }: ServiceProps) => {
  const initialValues = {
    category: ServiceCategory.Ongoing,
    started_at: '',
    finished_at: '',
  } as ServiceCreate
  const fields: React.ReactNode = (
    <FormikOngoingServiceFields choices={choices} />
  )

  return (
    <>
      <Grid>
        <Grid.Row>
          <Grid.Column style={{ flexGrow: '1' }}>
            <Header as="h2">Ongoing services</Header>
          </Grid.Column>
          {issue.is_open && (
            <Grid.Column style={{ width: 'auto' }}>
              <AddServiceButton
                floated="right"
                size="tiny"
                issue={issue}
                initialValues={initialValues}
                fields={fields}
              >
                Add ongoing service
              </AddServiceButton>
            </Grid.Column>
          )}
        </Grid.Row>
      </Grid>
      <OngoingServicesTable issue={issue} fields={fields} />
    </>
  )
}

export const OngoingServicesTable = ({ issue, fields }: ServiceTableProps) => {
  const result = api.useGetCaseServicesQuery({
    id: issue.id,
    category: ServiceCategory.Ongoing,
  })
  if (result.isLoading) {
    return <Loader active inline="centered" />
  }
  if (result.data.length == 0) {
    return (
      <Segment textAlign="center" secondary>
        <p>No ongoing services exist for this case.</p>
      </Segment>
    )
  }
  return (
    <Table celled>
      <Table.Header>
        <Table.Row>
          <Table.HeaderCell>Type</Table.HeaderCell>
          <Table.HeaderCell>Start date</Table.HeaderCell>
          <Table.HeaderCell>Finish date</Table.HeaderCell>
          <Table.HeaderCell>Notes</Table.HeaderCell>
          {issue.is_open && <Table.HeaderCell></Table.HeaderCell>}
        </Table.Row>
      </Table.Header>
      <Table.Body>
        {result.data.map((service) => (
          <Table.Row key={service.id}>
            <Table.Cell>{ONGOING_TYPE_LABELS.get(service.type)}</Table.Cell>
            <Table.Cell>{service.started_at}</Table.Cell>
            <Table.Cell>{service.finished_at}</Table.Cell>
            <Table.Cell>
              <RichTextDisplay content={service.notes} />
            </Table.Cell>
            {issue.is_open && (
              <Table.Cell collapsing textAlign="center">
                <ServiceActionIcons
                  issue={issue}
                  service={service}
                  fields={fields}
                />
              </Table.Cell>
            )}
          </Table.Row>
        ))}
      </Table.Body>
    </Table>
  )
}

export const ServiceActionIcons = ({
  issue,
  service,
  fields,
}: {
  issue: Issue
  service: Service
  fields: React.ReactNode
}) => {
  const [showConfirmDelete, setShowConfirmDelete] = useState(false)
  const [deleteService] = api.useDeleteCaseServiceMutation()

  /* Handle a situation where a click event does not trigger due to element
   * resizing when attempting to click an action icon on another row of the same
   * table when a confirm delete button is already showing. This delays the
   * element resize which allows the click event to trigger. This feels nasty and
   * probably is and I presume it might not always work but gets the job done
   * most of the time */
  const delayedHideConfirmDelete = useDebouncedCallback(() => {
    setShowConfirmDelete(false)
  }, 100)
  const ref = useClickOutside(() => delayedHideConfirmDelete())

  const handleDelete = () => {
    deleteService({ id: issue.id, serviceId: service.id })
      .unwrap()
      .then(() => {
        enqueueSnackbar('Service deleted', { variant: 'success' })
      })
      .catch((e) => {
        enqueueSnackbar(getAPIErrorMessage(e, 'Failed to delete service'), {
          variant: 'error',
        })
      })
  }

  if (showConfirmDelete) {
    return (
      <div ref={ref}>
        <Button negative compact size="mini" onClick={handleDelete}>
          Confirm delete
        </Button>
      </div>
    )
  }
  return (
    <>
      <EditServiceIcon
        link
        name="pencil"
        issue={issue}
        service={service}
        fields={fields}
      />
      <Icon
        link
        name="trash alternate outline"
        onClick={() => setShowConfirmDelete(true)}
      />
    </>
  )
}

export interface EditServiceIconProps {
  issue: Issue
  service: Service
  fields: React.ReactNode
}

export const EditServiceIcon = ({
  issue,
  service,
  fields,
  ...props
}: EditServiceIconProps & IconProps) => {
  const [open, setOpen] = useState(false)
  const [updateService] = api.useUpdateCaseServiceMutation()

  const handleSubmit = (
    values: ServiceCreate,
    { setSubmitting, setErrors }: FormikHelpers<ServiceCreate>
  ) => {
    updateService({
      id: issue.id,
      serviceId: service.id,
      serviceCreate: values,
    })
      .unwrap()
      .then(() => {
        enqueueSnackbar('Service updated', { variant: 'success' })
        setOpen(false)
      })
      .catch((e) => {
        enqueueSnackbar(getAPIErrorMessage(e, 'Failed to update service'), {
          variant: 'error',
        })
        const requestErrors = getAPIFormErrors(e)
        if (requestErrors) {
          setErrors(requestErrors)
        }
      })
      .finally(() => {
        setSubmitting(false)
      })
  }

  return (
    <>
      <ServiceModal
        open={open}
        setOpen={setOpen}
        fields={fields}
        initialValues={service}
        handleSubmit={handleSubmit}
        label={'Update ' + service.category.toLowerCase() + ' service'}
      />
      <Icon {...props} onClick={() => setOpen(true)} />
    </>
  )
}

export interface AddServiceButtonProps {
  issue: Issue
  initialValues: ServiceCreate
  fields: React.ReactNode
  children: string | number
}

export const AddServiceButton = ({
  issue,
  initialValues,
  children,
  fields,
  ...props
}: AddServiceButtonProps & ButtonProps) => {
  const [open, setOpen] = useState(false)
  const [createService] = api.useCreateCaseServiceMutation()

  const handleSubmit = (
    values: ServiceCreate,
    { setSubmitting, setErrors, resetForm }: FormikHelpers<ServiceCreate>
  ) => {
    createService({ id: issue.id, serviceCreate: filterEmpty(values) })
      .unwrap()
      .then(() => {
        enqueueSnackbar('Service created', { variant: 'success' })
        resetForm()
        setOpen(false)
      })
      .catch((e) => {
        enqueueSnackbar(getAPIErrorMessage(e, 'Failed to create service'), {
          variant: 'error',
        })
        const requestErrors = getAPIFormErrors(e)
        if (requestErrors) {
          setErrors(requestErrors)
        }
      })
      .finally(() => {
        setSubmitting(false)
      })
  }

  return (
    <>
      <ServiceModal
        open={open}
        setOpen={setOpen}
        fields={fields}
        initialValues={initialValues}
        handleSubmit={handleSubmit}
        label={children}
      />
      <Button {...props} onClick={() => setOpen(true)}>
        {children}
      </Button>
    </>
  )
}

export interface ServiceModalProps {
  open: boolean
  setOpen: React.Dispatch<React.SetStateAction<boolean>>
  initialValues: ServiceCreate
  fields: React.ReactNode
  handleSubmit: (
    values: ServiceCreate,
    helpers: FormikHelpers<ServiceCreate>
  ) => void
  label: string | number
}

export const ServiceModal = ({
  open,
  setOpen,
  initialValues,
  fields,
  handleSubmit,
  label,
}: ServiceModalProps) => {
  return (
    <Formik
      enableReinitialize
      initialValues={initialValues}
      onSubmit={handleSubmit}
    >
      {({ handleSubmit, errors, resetForm }) => {
        return (
          <Modal
            size="tiny"
            open={open}
            onClose={() => {
              resetForm()
              setOpen(false)
            }}
          >
            <Modal.Header>{label}</Modal.Header>
            <Modal.Content>
              <Form
                onSubmit={handleSubmit}
                error={Object.keys(errors).length > 0}
              >
                {fields}
                <FormikServiceErrorMessages />
              </Form>
            </Modal.Content>
            <Modal.Actions>
              <Button primary type="submit" onClick={() => handleSubmit()}>
                {label}
              </Button>
              <Button
                onClick={() => {
                  resetForm()
                  setOpen(false)
                }}
              >
                Close
              </Button>
            </Modal.Actions>
          </Modal>
        )
      }}
    </Formik>
  )
}

mount(App)
