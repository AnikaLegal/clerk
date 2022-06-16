import React from "react";
import { Label } from "semantic-ui-react";

const GROUP_COLORS = {
  Admin: "green",
  Lawyer: "orange",
  Coordinator: "teal",
  Paralegal: "blue",
};

export const GroupLabels = ({ groups, isSuperUser }) => (
  <>
    {groups.map((groupName) => (
      <Label color={GROUP_COLORS[groupName]} key={groupName}>
        {groupName}
      </Label>
    ))}
    {isSuperUser && <Label color="black">Superuser 😎</Label>}
  </>
);
