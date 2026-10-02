import { Center, Loader, Paper, Table, Text } from '@mantine/core'
import api, { Issue, Service, ServiceCategory } from 'api'
import { RichTextDisplay } from 'comps/rich-text'
import { enqueueSnackbar } from 'notistack'
import React, { useEffect } from 'react'
import { ErrorResult, getAPIErrorMessage } from 'utils'
import { SERVICE_TYPES } from '../schema'
import { ServiceActionIconGroup } from './service-actions'

interface ServiceTableProps {
  issue: Issue
  category: ServiceCategory
  canChange: boolean
}

const COLUMNS: Record<ServiceCategory, string[]> = {
  DISCRETE: ['Type', 'Date', 'Count', 'Notes'],
  ONGOING: ['Type', 'Start date', 'Finish date', 'Notes'],
}

export const ServiceTable = ({
  issue,
  category,
  canChange,
}: ServiceTableProps) => {
  const result = api.useGetCaseServicesQuery({ id: issue.id, category })
  const noun = category.toLowerCase()

  useEffect(() => {
    if (result.isError) {
      enqueueSnackbar(
        getAPIErrorMessage(
          result.error as ErrorResult,
          `Could not load ${noun} services`
        ),
        { variant: 'error' }
      )
    }
  }, [result.isError, result.error, noun])

  if (result.isLoading) {
    return (
      <Center m="sm">
        <Loader />
      </Center>
    )
  }
  if (result.isError) {
    return (
      <Text c="red" ta="center" m="sm">
        Could not load {noun} services
      </Text>
    )
  }
  if (!result.data || result.data.length == 0) {
    return (
      <Paper withBorder p="md" mt="lg">
        <Text ta="center" c="dimmed">
          No {noun} services exist for this case.
        </Text>
      </Paper>
    )
  }

  return (
    <Table
      withColumnBorders
      withTableBorder
      verticalSpacing="xs"
      fz="md"
      mt="lg"
    >
      <Table.Thead>
        <Table.Tr>
          {COLUMNS[category].map((label) => (
            <Table.Th key={label}>{label}</Table.Th>
          ))}
          {canChange && <Table.Th w="1%"></Table.Th>}
        </Table.Tr>
      </Table.Thead>
      <Table.Tbody>
        {result.data.map((service) => (
          <ServiceTableRow
            key={service.id}
            issue={issue}
            service={service}
            canChange={canChange}
          />
        ))}
      </Table.Tbody>
    </Table>
  )
}

const ServiceTableRow = ({
  issue,
  service,
  canChange,
}: {
  issue: Issue
  service: Service
  canChange: boolean
}) => (
  <Table.Tr>
    <Table.Td>{SERVICE_TYPES[service.category][service.type]}</Table.Td>
    <Table.Td>{service.started_at}</Table.Td>
    <Table.Td>
      {service.category === 'DISCRETE' ? service.count : service.finished_at}
    </Table.Td>
    <Table.Td maw="300px">
      {service.notes && <RichTextDisplay content={service.notes} />}
    </Table.Td>
    {canChange && (
      <Table.Td w="1%">
        <ServiceActionIconGroup issue={issue} service={service} />
      </Table.Td>
    )}
  </Table.Tr>
)
