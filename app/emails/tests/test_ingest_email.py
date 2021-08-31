import pytest

from emails.service import parse_clerk_address, build_clerk_address
from emails.models import EmailState
from core.factories import EmailFactory, IssueFactory, UserFactory


@pytest.mark.django_db
def _test_parse_email_address():
    issue_pk = "0e62ccc2-b9ee-4a07-979a-da8a9d450404"
    issue = IssueFactory(pk=issue_pk)
    sent_email = EmailFactory(
        to_addr="mattdsegal@gmail.com",
        to_addrs="mattdsegal@gmail.com",
        state=EmailState.SENT,
        issue=issue,
        sender=None,
    )
    issue_addr = build_clerk_address(sent_email)
    assert issue_addr == "case.0e62ccc2@fake.anikalegal.com"
    to_addrs = f"{issue_addr},  Matt Segal <matt@anikalegal.com>"
    received_email = EmailFactory(to_addrs=to_addrs, issue=None, sender=None)
    import pdb

    pdb.set_trace()


# data = {
#     "subject": ["Hello World!"],
#     "envelope": [
#         '{"to":["foo@em7221.test-mail.anikalegal.com"],"from":"matt@anikalegal.com"}'
#     ],
#     "to": [
#         "foo@em7221.test-mail.anikalegal.com, bar@em7221.test-mail.anikalegal.com,  joe blow <joe@gmail.com>"
#     ],
#     "text": [
#         "Hi Matt\r\n\r\nOn Sun, Jul 18, 2021 at 12:51 PM Matt Segal <matt@anikalegal.com> wrote:\r\n\r\n> hmmm\r\n>\r\n> --\r\n>\r\n> Matthew Segal\r\n>\r\n> Head of Technology\r\n>\r\n> mobile: 0431 417 373\r\n>\r\n> email: matt@anikalegal.com\r\n>\r\n> site: www.anikalegal.com\r\n>\r\n> Level 2/520 Bourke Street\r\n>\r\n> Melbourne VIC 3000\r\n>\n"
#     ],
#     "html": ["<div><h1>Hello World</h1></div>"],
# }

# data = {
#     "subject": ["Hello World!"],
#     "envelope": [
#         '{"to":["foo@em7221.test-mail.anikalegal.com"],"from":"matt@anikalegal.com"}'
#     ],
#     "cc": ["bar@em7221.test-mail.anikalegal.com"],
#     "to": [
#         "foo@em7221.test-mail.anikalegal.com, bar@em7221.test-mail.anikalegal.com,  joe blow <joe@gmail.com>"
#     ],
#     "text": [
#         "Hi Matt\r\n\r\nOn Sun, Jul 18, 2021 at 12:51 PM Matt Segal <matt@anikalegal.com> wrote:\r\n\r\n> hmmm\r\n>\r\n> --\r\n>\r\n> Matthew Segal\r\n>\r\n> Head of Technology\r\n>\r\n> mobile: 0431 417 373\r\n>\r\n> email: matt@anikalegal.com\r\n>\r\n> site: www.anikalegal.com\r\n>\r\n> Level 2/520 Bourke Street\r\n>\r\n> Melbourne VIC 3000\r\n>\n"
#     ],
#     "html": ["<div><h1>Hello World</h1></div>"],
# }
