import {
  ActionIcon,
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
  ThemeIcon,
  Title,
  Tooltip,
} from '@mantine/core'
import { useClickOutside, useDebouncedCallback } from '@mantine/hooks'
import {
  IconExclamationCircle,
  IconSearch,
  IconTrash,
} from '@tabler/icons-react'
import {
  DocumentTemplate,
  GetDocumentTemplatesApiArg,
  useDeleteDocumentTemplateMutation,
  useGetDocumentTemplatesQuery,
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
  const [args, setArgs] = useState<GetDocumentTemplatesApiArg>({})

  const result = useGetDocumentTemplatesQuery(args)

  const setArgByName = (
    name: keyof GetDocumentTemplatesApiArg,
    value: string
  ) => {
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
      <Title order={1}>Document Templates</Title>
      <Button component="a" href={CreateUrl} size="md" mt="sm">
        Upload document template
      </Button>
      <Grid mt="md">
        <Grid.Col span={6}>
          <TextInput
            placeholder="Search by template name..."
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
            placeholder="Select a case topic"
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
            <Table.Th>Created</Table.Th>
            <Table.Th>Modified</Table.Th>
            <Table.Th></Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          <DocumentTemplateTableBody result={result} />
        </Table.Tbody>
      </Table>
    </Container>
  )
}

const ErrorState = ({ error }: { error: any }) => {
  useEffect(() => {
    const message = getAPIErrorMessage(
      error,
      'Could not load document templates'
    )
    enqueueSnackbar(message, { variant: 'error' })
  }, [error])

  return (
    <Table.Tr>
      <td colSpan={5}>
        <Group justify="center" gap="xs" m="sm" c="red">
          <IconExclamationCircle />
          <Text>Could not load document templates</Text>
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

interface DocumentTemplateTableBodyProps {
  result: ReturnType<typeof useGetDocumentTemplatesQuery>
}

const DocumentTemplateTableBody = ({
  result,
}: DocumentTemplateTableBodyProps) => {
  if (result.isError) {
    return <ErrorState error={result.error} />
  }
  if (result.isLoading) {
    return <LoadingState />
  }

  const data: DocumentTemplate[] = result.data || []
  if (data.length < 1) {
    return <EmptyState />
  }
  return (
    <>
      {data.map((template) => (
        <DocumentTemplateTableRow
          key={template.url || template.name}
          template={template}
        />
      ))}
    </>
  )
}

interface DocumentTemplateTableRowProps {
  template: DocumentTemplate
}

const DocumentTemplateTableRow = ({
  template,
}: DocumentTemplateTableRowProps) => {
  const found: boolean = !!template.url
  return (
    <Table.Tr>
      {found ? (
        <>
          <Table.Td>
            <a href={template.url}>{template.name}</a>
          </Table.Td>
          <Table.Td>{TopicLabels.get(template.topic)}</Table.Td>
          <Table.Td>{template.created_at}</Table.Td>
          <Table.Td>{template.modified_at}</Table.Td>
        </>
      ) : (
        <>
          <Table.Td>
            <Group gap="xs">
              <Tooltip label="File Not Found" color="red" withArrow>
                <ThemeIcon variant="transparent" color="red">
                  <IconExclamationCircle />
                </ThemeIcon>
              </Tooltip>
              <span>{template.name}</span>
            </Group>
          </Table.Td>
          <Table.Td>{TopicLabels.get(template.topic)}</Table.Td>
          <Table.Td>-</Table.Td>
          <Table.Td>-</Table.Td>
        </>
      )}
      <Table.Td>
        <DocumentTemplateActionIcons template={template} disabled={!found} />
      </Table.Td>
    </Table.Tr>
  )
}

interface DocumentTemplateActionIconsProps {
  template: DocumentTemplate
  disabled?: boolean
}

const DocumentTemplateActionIcons = ({
  template,
  disabled = false,
}: DocumentTemplateActionIconsProps) => {
  const [showConfirmDelete, setShowConfirmDelete] = useState(false)
  const [deleteDocumentTemplate] = useDeleteDocumentTemplateMutation()

  const delayedHideConfirmDelete = useDebouncedCallback(() => {
    setShowConfirmDelete(false)
  }, 100)
  const ref = useClickOutside(() => delayedHideConfirmDelete())

  const handleDelete = () => {
    deleteDocumentTemplate({ id: template.id })
      .unwrap()
      .then(() => {
        enqueueSnackbar('Document template deleted', { variant: 'success' })
      })
      .catch((e) => {
        enqueueSnackbar(
          getAPIErrorMessage(e, 'Failed to delete document template'),
          {
            variant: 'error',
          }
        )
      })
  }

  if (showConfirmDelete) {
    return (
      <div ref={ref}>
        <Center>
          <Button
            variant="filled"
            color="red"
            size="compact-sm"
            onClick={handleDelete}
          >
            Confirm delete
          </Button>
        </Center>
      </div>
    )
  }

  return (
    <Center>
      <ActionIcon variant="transparent" color="gray" disabled={disabled}>
        <IconTrash stroke={1.5} onClick={() => setShowConfirmDelete(true)} />
      </ActionIcon>
    </Center>
  )
}

mount(App)
