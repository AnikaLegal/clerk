from collections import Counter

from accounts.models import CASE_GROUPS_BY_PRIVILEGE, CaseGroups


def test_case_groups_by_privilege_lists_every_group_once():
    # A new group must be ranked explicitly, not slotted in by declaration order.
    assert Counter(CASE_GROUPS_BY_PRIVILEGE) == Counter(CaseGroups)
