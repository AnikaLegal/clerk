import { Card, CardProps, Table, Text, Title } from '@mantine/core'
import React from 'react'

export interface StructuredAnswersCardProps {
  title: string
  data: { label: string; value: React.ReactNode }[][]
  card?: CardProps
}

export const StructuredAnswersCard = ({
  title,
  data,
  card,
}: StructuredAnswersCardProps) => {
  return (
    <Card {...card}>
      <Card.Section inheritPadding>
        <Title order={4} p="sm" mt="md" bg="var(--gold-light)">
          {title}
        </Title>
      </Card.Section>
      {data.map(
        (subSection, index) =>
          subSection.some((v) => v.value) && (
            <Table
              key={index}
              variant="vertical"
              withTableBorder
              withColumnBorders
              mt="sm"
            >
              <Table.Tbody>
                {subSection.map(
                  (row) =>
                    row.value != null && (
                      <Table.Tr key={row.label}>
                        <Table.Th w="25%">
                          <Text fw={700} inherit>
                            {row.label}
                          </Text>
                        </Table.Th>
                        <Table.Td>{row.value}</Table.Td>
                      </Table.Tr>
                    )
                )}
              </Table.Tbody>
            </Table>
          )
      )}
    </Card>
  )
}
