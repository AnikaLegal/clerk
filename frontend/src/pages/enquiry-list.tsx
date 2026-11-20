import { Container, Text, Title } from '@mantine/core'
import api from 'api'
import { EnquiryTable } from 'features/enquiry'
import React from 'react'
import { mount } from 'utils'

const App = () => {
  // Page size 1: only the total is needed.
  const pending = api.useGetEnquiriesQuery({
    requiresCallback: true,
    pageSize: 1,
  }).data?.item_count

  return (
    <Container size="xl">
      <Title order={1}>Enquiries</Title>
      <Text c="dimmed" fz="lg" mt={2}>
        {pending === undefined
          ? ' '
          : `${pending} ${pending === 1 ? 'enquiry' : 'enquiries'} pending`}
      </Text>
      <EnquiryTable />
    </Container>
  )
}

mount(App)
