import {
  Button,
  Center,
  Container,
  Grid,
  Group,
  Loader,
  Select,
  Table,
  Text,
  TextInput,
  Title,
} from '@mantine/core'
import { useDebouncedCallback } from '@mantine/hooks'
import { IconExclamationCircle, IconSearch } from '@tabler/icons-react'
import {
  EmailTemplate,
  GetEmailTemplatesApiArg,
  useGetEmailTemplatesQuery,
} from 'api'
import { enqueueSnackbar } from 'notistack'
import React, { useEffect, useState } from 'react'
import { choiceToMap, getAPIErrorMessage, mount } from 'utils'

import '@mantine/core/styles.css'

interface DjangoContext {
  choices: {
    topic: [string, string][]
  }
  create_url: string
}

const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext
const TopicLabels = choiceToMap(CONTEXT.choices.topic)
const CreateUrl = CONTEXT.create_url

const App = () => {
  const [args, setArgs] = useState<GetEmailTemplatesApiArg>({})

  const result = useGetEmailTemplatesQuery(args)

  const setArgByName = (name: keyof GetEmailTemplatesApiArg, value: string) => {
    setArgs((prev) => {
      return { ...prev, [name]: value }
    })
  }

  const onChange = useDebouncedCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      setArgByName('name', event.target.value.trim())
    },
    300
  )

  return (
    <Container size="xl">
      <Title order={1}>Email Templates</Title>
      <Button component="a" href={CreateUrl} size="md" mt="sm">
        Create email template
      </Button>
      <Grid mt="md">
        <Grid.Col span={6}>
          <TextInput
            placeholder="Search by template name or subject..."
            rightSection={<IconSearch size={16} stroke={4} />}
            size="md"
            onChange={onChange}
          />
        </Grid.Col>
        <Grid.Col span={6}>
          <Select
            clearable
            searchable
            size="md"
            placeholder="Select a case type"
            data={Array.from(TopicLabels, ([key, value]) => ({
              value: key,
              label: value,
            }))}
            onChange={(value) => setArgByName('topic', (value as string) || '')}
            withCheckIcon={false}
          />
        </Grid.Col>
      </Grid>
      <Table
        withColumnBorders
        withTableBorder
        verticalSpacing="md"
        fz="md"
        mt="md"
      >
        <Table.Thead>
          <Table.Tr>
            <Table.Th>Name</Table.Th>
            <Table.Th>Topic</Table.Th>
            <Table.Th>Subject</Table.Th>
            <Table.Th>Created</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          <EmailTemplateTableBody result={result} />
        </Table.Tbody>
      </Table>
    </Container>
  )
}

const ErrorState = ({ error }: { error: any }) => {
  useEffect(() => {
    const message = getAPIErrorMessage(error, 'Could not load email templates')
    enqueueSnackbar(message, { variant: 'error' })
  }, [error])

  return (
    <Table.Tr>
      <td colSpan={5}>
        <Group justify="center" gap="xs" m="sm" c="red">
          <IconExclamationCircle />
          <Text>Could not load email templates</Text>
        </Group>
      </td>
    </Table.Tr>
  )
}

const LoadingState = () => (
  <Table.Tr>
    <td colSpan={5}>
      <Center m="sm">
        <Loader />
      </Center>
    </td>
  </Table.Tr>
)

const EmptyState = () => (
  <Table.Tr>
    <td colSpan={5}>
      <Center m="sm">No templates found</Center>
    </td>
  </Table.Tr>
)

interface EmailTemplateTableBodyProps {
  result: ReturnType<typeof useGetEmailTemplatesQuery>
}

const EmailTemplateTableBody = ({ result }: EmailTemplateTableBodyProps) => {
  if (result.isError) {
    return <ErrorState error={result.error} />
  }
  if (result.isLoading) {
    return <LoadingState />
  }

  const data: EmailTemplate[] = result.data || []
  if (data.length < 1) {
    return <EmptyState />
  }

  return (
    <>
      {data.map((template) => (
        <Table.Tr key={template.url}>
          <Table.Td>
            <a href={template.url}>{template.name}</a>
          </Table.Td>
          <Table.Td>{TopicLabels.get(template.topic)}</Table.Td>
          <Table.Td>{template.subject}</Table.Td>
          <Table.Td>{template.created_at}</Table.Td>
        </Table.Tr>
      ))}
    </>
  )
}

mount(App)
