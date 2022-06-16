import React, { useState, useEffect } from "react";
import { Table, Label, Button } from "semantic-ui-react";

import { api } from "api";
import { GroupLabels } from "comps/group-label";

export const AccountPermissions = ({ account }) => {
  const [isLoading, setIsLoading] = useState(true);
  const [perms, setPerms] = useState(null);
  useEffect(() => {
    api.accounts.getPermissions(account.id).then(({ resp, data }) => {
      setPerms(data);
      setIsLoading(false);
    });
  }, []);
  return (
    <Table size="small" definition>
      <Table.Body>
        <Table.Row>
          <Table.Cell width={3}>Permission grops</Table.Cell>
          <Table.Cell>
            <GroupLabels
              groups={account.groups}
              isSuperUser={account.is_superuser}
            />
          </Table.Cell>
        </Table.Row>
        <Table.Row>
          <Table.Cell width={3}>Microsoft account</Table.Cell>
          <Table.Cell>
            {account.ms_account_created_at
              ? `Created on ${account.ms_account_created_at}`
              : "No Sharepoint access - account setup in progress"}
          </Table.Cell>
        </Table.Row>
        <Table.Row>
          <Table.Cell width={3}>Sharepoint access</Table.Cell>
          <Table.Cell>
            {isLoading ? (
              "Loading..."
            ) : (
              <>
                {perms.paralegal_perm_issues.map((i) => (
                  <Label color="green" href={i.url}>
                    {i.fileref}
                    <Label.Detail>Has access</Label.Detail>
                  </Label>
                ))}
                {perms.paralegal_perm_missing_issues
                  .filter((i) => i.actionstep_id)
                  .map((i) => (
                    <Label color="olive" href={i.url}>
                      {i.fileref}
                      <Label.Detail>Actionstep</Label.Detail>
                    </Label>
                  ))}
                {perms.paralegal_perm_missing_issues
                  .filter((i) => !i.actionstep_id)
                  .map((i) => (
                    <Label color="yellow" href={i.url}>
                      {i.fileref}
                      <Label.Detail>No access</Label.Detail>
                    </Label>
                  ))}
              </>
            )}
          </Table.Cell>
        </Table.Row>
      </Table.Body>
    </Table>
  );
};
