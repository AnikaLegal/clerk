import React from "react"
import { Issue } from "api"
import { Header, Grid, Card } from "semantic-ui-react"

export const CaseSummaryCard = ({ issue }: { issue: Issue }) => {
    return (
        <Card fluid>
            <Card.Content header='Case' />
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
                            ) : ("-")}
                        </Grid.Column>
                        <Grid.Column>
                            <Header sub>Supervised by</Header>
                            {issue.lawyer ? (
                                <a href={issue.lawyer.url}>{issue.lawyer.full_name}</a>
                            ) : ("-")}
                        </Grid.Column>
                    </Grid.Row>
                </Grid>
            </Card.Content>
        </Card>
    )
}