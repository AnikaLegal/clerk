import React from 'react'
import { Issue } from 'api'
import { Header, Grid, Card } from 'semantic-ui-react'

export const CaseSummaryCard = ({ issue }: { issue: Issue }) => {
  return (
    <Card fluid>
      <Card.Content header="Case summary" />
      <Card.Content>
        <Grid>
          <Grid.Row columns={2}>
            <Grid.Column>
              <Header sub>Fileref</Header>
              <a href={issue.url}>{issue.fileref}</a>
            </Grid.Column>
            <Grid.Column>
              <Header sub>Topic</Header>
              {issue.topic_display}
            </Grid.Column>
          </Grid.Row>
          <Grid.Row columns={2}>
            <Grid.Column>
              <Header sub>Assigned to</Header>
              {issue.paralegal ? (
                <a href={issue.paralegal.url}>{issue.paralegal.full_name}</a>
              ) : (
                '-'
              )}
            </Grid.Column>
            <Grid.Column>
              <Header sub>Supervised by</Header>
              {issue.lawyer ? (
                <a href={issue.lawyer.url}>{issue.lawyer.full_name}</a>
              ) : (
                '-'
              )}
            </Grid.Column>
          </Grid.Row>
        </Grid>
      </Card.Content>
      <Card.Content>
        <Grid>
          <Grid.Row columns={2}>
            <Grid.Column>
              <Header sub>Client</Header>
              <a href={issue.client.url}>{issue.client.full_name}</a>
            </Grid.Column>
            <Grid.Column>
              <Header sub>Preferred name</Header>
              {issue.client.preferred_name || '-'}
            </Grid.Column>
          </Grid.Row>
          <Grid.Row columns={1}>
            <Grid.Column>
              <Header sub>Email</Header>
              {issue.client.email || '-'}
            </Grid.Column>
          </Grid.Row>
          <Grid.Row columns={1}>
            <Grid.Column>
              <Header sub>Phone</Header>
              {issue.client.phone_number || '-'}
            </Grid.Column>
          </Grid.Row>
        </Grid>
      </Card.Content>
      <Card.Content>
        <Grid>
          <Grid.Row columns={1}>
            <Grid.Column>
              <Header sub>Tenancy</Header>
              <a href={issue.tenancy.url}>{issue.tenancy.address}</a>
            </Grid.Column>
          </Grid.Row>
          <Grid.Row columns={2}>
            <Grid.Column>
              <Header sub>Agent</Header>
              {issue.tenancy.agent ? (
                <a href={issue.tenancy.agent.url}>
                  {issue.tenancy.agent.full_name}
                </a>
              ) : (
                '-'
              )}
            </Grid.Column>
            <Grid.Column>
              <Header sub>Landlord</Header>
              {issue.tenancy.landlord ? (
                <a href={issue.tenancy.landlord.url}>
                  {issue.tenancy.landlord.full_name}
                </a>
              ) : (
                '-'
              )}
            </Grid.Column>
          </Grid.Row>
        </Grid>
      </Card.Content>
    </Card>
  )
}
