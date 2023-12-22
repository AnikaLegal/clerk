import React from 'react'
import { Formik } from 'formik'
import { Container, Header, Button, Table } from 'semantic-ui-react'
import { useSnackbar } from 'notistack'

import { mount, getAPIErrorMessage, getAPIFormErrors } from 'utils'
import { TenancyForm } from 'forms'
import { Tenancy, useUpdateTenancyMutation } from 'apiNew'

interface DjangoContext {
  tenancy: Tenancy
}

const { tenancy: initialTenancy } = (window as any)
  .REACT_CONTEXT as DjangoContext

const App = () => {
  const [isEditing, setIsEditing] = React.useState<boolean>(false)
  const [tenancy, setTenancy] = React.useState<Tenancy>(initialTenancy)
  const { enqueueSnackbar } = useSnackbar()
  const [updateTenancy] = useUpdateTenancyMutation()

  const propertyData = {
    Address: tenancy.address,
    Suburb: tenancy.suburb,
    Postcode: tenancy.postcode,
    'Tenancy Start Date': tenancy.started,
    'Is Client On Lease': tenancy.is_on_lease ? tenancy.is_on_lease.display : "",
  }
  return (
    <Container>
      <Header as="h1">Tenancy</Header>
      <Header as="h2">Property Details</Header>
      {!isEditing && (
        <div>
          <Table className="definition small">
            <Table.Body>
              {Object.entries(propertyData).map(([label, value]) => (
                <Table.Row key={label}>
                  <Table.Cell className="three wide">{label}</Table.Cell>
                  <Table.Cell>{value}</Table.Cell>
                </Table.Row>
              ))}
            </Table.Body>
          </Table>
          <Button primary onClick={() => setIsEditing(true)}>
            Edit tenancy
          </Button>
        </div>
      )}
      {isEditing && (
        <div>
          <Formik
            initialValues={{
              address: tenancy.address,
              suburb: tenancy.suburb,
              postcode: tenancy.postcode,
              started: tenancy.started,
              is_on_lease: tenancy.is_on_lease.value,
            }}
            validate={(values) => {}}
            onSubmit={(values, { setSubmitting, setErrors }) => {
              updateTenancy({ id: tenancy.id, tenancyCreate: values })
                .unwrap()
                .then((tenancy) => {
                  enqueueSnackbar('Updated tenancy', { variant: 'success' })
                  setTenancy(tenancy)
                  setSubmitting(false)
                })
                .catch((err) => {
                  enqueueSnackbar(
                    getAPIErrorMessage(err, 'Failed to update tenancy'),
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
            }}
          >
            {(formik) => (
              <TenancyForm
                formik={formik}
                isOnLeaseChoices={tenancy.is_on_lease.choices}
                onCancel={() => setIsEditing(false)}
              />
            )}
          </Formik>
        </div>
      )}
      <Header as="h2">Property People</Header>
      <Table className="definition small">
        <Table.Body>
          <Table.Row>
            <Table.Cell className="three wide">Client</Table.Cell>
            <Table.Cell>
              {tenancy.client ? (
                <a href={tenancy.client.url}>{tenancy.client.full_name}</a>
              ) : (
                'No client'
              )}
            </Table.Cell>
          </Table.Row>
          <Table.Row>
            <Table.Cell className="three wide">Agent</Table.Cell>
            <Table.Cell>
              {tenancy.agent ? (
                <a href={tenancy.agent.url}>{tenancy.agent.full_name}</a>
              ) : (
                'No agent'
              )}
            </Table.Cell>
          </Table.Row>
          <Table.Row>
            <Table.Cell className="three wide">Landlord</Table.Cell>
            <Table.Cell>
              {tenancy.landlord ? (
                <a href={tenancy.landlord.url}>{tenancy.landlord.full_name}</a>
              ) : (
                'No landlord'
              )}
            </Table.Cell>
          </Table.Row>
        </Table.Body>
      </Table>
    </Container>
  )
}

mount(App)
