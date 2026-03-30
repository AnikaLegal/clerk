import {
  Box,
  Button,
  Container,
  Grid,
  Group,
  Loader,
  Pagination,
  Select,
  Stack,
  Text,
  TextInput,
  Title,
  Transition,
} from '@mantine/core'
import { useDebouncedCallback, useToggle } from '@mantine/hooks'
import { GetCasesApiArg, useGetCasesQuery } from 'api'
import { CaseListTable } from 'comps/case-table'
import { UserSelect } from 'comps/user-select'
import React, { useState } from 'react'
import { UserPermission } from 'types'
import { mount } from 'utils'

interface DjangoContext {
  user: UserPermission
  choices: {
    stage: string[][]
    topic: string[][]
    outcome: string[][]
    is_open: string[][]
  }
  create_url: string
}
const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext

const TABLE_FIELDS = [
  'fileref',
  'topic',
  'client',
  'paralegal',
  'lawyer',
  'created_at',
  'stage',
  'provided_legal_services',
  'outcome',
]

const App = () => {
  const [showAdvancedSearch, toggleAdvancedSearch] = useToggle()
  const [args, setArgs] = useState<GetCasesApiArg>({})
  const handleFilterChange = useDebouncedCallback((value: string) => {
    setArgs((prev) => ({ ...prev, search: value, page: 1 }))
  }, 300)

  const casesResult = useGetCasesQuery(args)
  const issues = casesResult.data?.results ?? []
  const totalIssues = casesResult.data?.item_count
  const currentPage = casesResult.data?.current
  const totalPages = casesResult.data?.page_count

  return (
    <Container size="xl">
      <Title order={1} mb="md">
        <Group wrap="nowrap" gap="sm" justify="space-between">
          <span>Cases</span>
          {CONTEXT.user.is_coordinator_or_better && (
            <Button component="a" href={CONTEXT.create_url}>
              Create a new case
            </Button>
          )}
        </Group>
        <Text className="subtitle">
          Showing {issues.length} of {totalIssues} cases
        </Text>
      </Title>
      <Stack gap="md">
        <TextInput
          placeholder="Find cases with the name or email of paralegals and clients, or by using the file ref"
          onChange={(event) => handleFilterChange(event.currentTarget.value)}
          rightSection={casesResult.isFetching ? <Loader size="xs" /> : null}
          size="md"
        />
        <Group>
          <Button
            variant="filled"
            onClick={() => toggleAdvancedSearch()}
            size="compact-sm"
            color="gray.3"
            fw="normal"
            autoContrast
          >
            {showAdvancedSearch ? 'Hide advanced search' : 'Advanced search'}
          </Button>
        </Group>
        {showAdvancedSearch && (
          <Grid>
            <Grid.Col span={6}>
              <Select
                clearable
                placeholder="Is case open?"
                data={choiceToOptions(CONTEXT.choices.is_open)}
                onChange={(value) =>
                  setArgs({ ...args, isOpen: value || undefined, page: 1 })
                }
                size="md"
              />
            </Grid.Col>
            <Grid.Col span={6}>
              <Select
                clearable
                placeholder="Case stage"
                data={choiceToOptions(CONTEXT.choices.stage)}
                onChange={(value) =>
                  setArgs({ ...args, stage: value || undefined, page: 1 })
                }
                size="md"
              />
            </Grid.Col>
            <Grid.Col span={6}>
              <Select
                clearable
                placeholder="Case outcome"
                data={choiceToOptions(CONTEXT.choices.outcome)}
                onChange={(value) =>
                  setArgs({ ...args, outcome: value || undefined, page: 1 })
                }
                size="md"
              />
            </Grid.Col>
            <Grid.Col span={6}>
              <Select
                clearable
                placeholder="Case topic"
                data={choiceToOptions(CONTEXT.choices.topic)}
                onChange={(value) =>
                  setArgs({ ...args, topic: value || undefined, page: 1 })
                }
                size="md"
              />
            </Grid.Col>
            <Grid.Col span={6}>
              <UserSelect
                searchable
                clearable
                placeholder="Select a paralegal"
                onChange={(value) =>
                  setArgs({ ...args, paralegal: value || undefined, page: 1 })
                }
                params={{
                  group: 'Paralegal',
                  sort: 'email',
                }}
                size="md"
              />
            </Grid.Col>
            <Grid.Col span={6}>
              <UserSelect
                searchable
                clearable
                placeholder="Select a lawyer"
                onChange={(value) =>
                  setArgs({ ...args, lawyer: value || undefined, page: 1 })
                }
                params={{
                  group: 'Lawyer',
                  sort: 'email',
                }}
                size="md"
              />
            </Grid.Col>
          </Grid>
        )}
      </Stack>
      <Box mt="md">
        <Transition
          mounted={!casesResult.isFetching}
          transition="fade"
          duration={300}
          timingFunction="ease"
        >
          {(styles) => (
            <Box style={styles}>
              <CaseListTable issues={issues} fields={TABLE_FIELDS} />
              {!!totalPages && (
                <Pagination
                  total={totalPages}
                  value={currentPage || 1}
                  onChange={(page) => setArgs({ ...args, page })}
                  mt="md"
                  withEdges
                  withControls
                />
              )}
            </Box>
          )}
        </Transition>
      </Box>
    </Container>
  )
}

const choiceToOptions = (choices: string[][]) =>
  choices.map(([value, label]) => ({
    value,
    label,
  }))

mount(App)
