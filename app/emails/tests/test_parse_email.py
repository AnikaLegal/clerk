"""
state
'subject': ['Re: Try again?']
'charsets': ['{"to":"UTF-8","html":"UTF-8","subject":"UTF-8","from":"UTF-8","text":"UTF-8"}']
"text (replace \r\n\ with \n"
    'Hi Matt\r\n\r\nOn Sun, Jul 18, 2021 at 12:51 PM Matt Segal <matt@anikalegal.com> wrote:\r\n\r\n> hmmm\r\n>\r\n> --\r\n>\r\n> Matthew Segal\r\n>\r\n> Head of Technology\r\n>\r\n> mobile: 0431 417 373\r\n>\r\n> email: matt@anikalegal.com\r\n>\r\n> site: www.anikalegal.com\r\n>\r\n> Level 2/520 Bourke Street\r\n>\r\n> Melbourne VIC 3000\r\n>\r\n> <https://www.facebook.com/anikalegal/>\r\n> <https://au.linkedin.com/company/anika-legal>\r\n> <https://www.instagram.com/anikalegal/?hl=en>\r\n>\n'

# WHO AM I
'envelope': ['{"to":["foo@em7221.test-mail.anikalegal.com"],"from":"matt@anikalegal.com"}']

# WHO WAS THIS SENT TO
data["to"]
'foo@em7221.test-mail.anikalegal.com, bar@em7221.test-mail.anikalegal.com,  matthew segal <mattdsegal@gmail.com>'
data['cc']
'baz@em7221.test-mail.anikalegal.com'

html: ... some html

    TODO: Try with CC and multiple senders

to
    'foo@em7221.test-mail.anikalegal.com'
request.FILES
'attachments': ['1'], 'subject': ['Re: Try again?'], 'attachment-info': ['{"attachment1":{"filename":"nickagenda.txt","name":"nickagenda.txt","charset":"US-ASCII","type":"text/plain","content-id":"f_kr8lt7gd0"}}']
<MultiValueDict: {'attachment1': [<InMemoryUploadedFile: evictions-questions.txt (text/plain)>]}>
request.FILES['attachment1'].read().decode('utf-8')


abc = { 'a': [1], 'b':[1,2,3]}
mdict = MultiValueDict(abc)


data.get("cc")
data.get("from")
'Matt Segal <matt@anikalegal.com>'

"""
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.datastructures import MultiValueDict

from emails.models import Email, EmailAttachment, EmailState
from emails.service import process_inbound_email


def test_parse_email__with_no_files():
    data = MultiValueDict(
        subject=["Hello World!"],
        envelope=[
            '{"to":["foo@em7221.test-mail.anikalegal.com"],"from":"matt@anikalegal.com"}'
        ],
        to=[
            "foo@em7221.test-mail.anikalegal.com, bar@em7221.test-mail.anikalegal.com,  joe blow <joe@gmail.com>"
        ],
        text=[
            "Hi Matt\r\n\r\nOn Sun, Jul 18, 2021 at 12:51 PM Matt Segal <matt@anikalegal.com> wrote:\r\n\r\n> hmmm\r\n>\r\n> --\r\n>\r\n> Matthew Segal\r\n>\r\n> Head of Technology\r\n>\r\n> mobile: 0431 417 373\r\n>\r\n> email: matt@anikalegal.com\r\n>\r\n> site: www.anikalegal.com\r\n>\r\n> Level 2/520 Bourke Street\r\n>\r\n> Melbourne VIC 3000\r\n>\n"
        ],
        html=["<div><h1>Hello World</h1></div>"],
    )
    files = MultiValueDict()
    assert Email.objects.count() == 0
    process_inbound_email(data, files)
    assert Email.objects.count() == 1
    email = Email.objects.last()
    assert email.from_addr == "matt@anikalegal.com"
    assert email.to_addr == "foo@em7221.test-mail.anikalegal.com"
    assert (
        email.to_addrs
        == "foo@em7221.test-mail.anikalegal.com, bar@em7221.test-mail.anikalegal.com,  joe blow <joe@gmail.com>"
    )
    assert email.cc_addrs == ""
    assert email.subject == "Hello World!"
    assert email.state == EmailState.RECEIVED
    assert (
        email.text
        == "Hi Matt\n\nOn Sun, Jul 18, 2021 at 12:51 PM Matt Segal <matt@anikalegal.com> wrote:\n\n> hmmm\n>\n> --\n>\n> Matthew Segal\n>\n> Head of Technology\n>\n> mobile: 0431 417 373\n>\n> email: matt@anikalegal.com\n>\n> site: www.anikalegal.com\n>\n> Level 2/520 Bourke Street\n>\n> Melbourne VIC 3000\n>\n"
    )
    assert email.html == "<div><h1>Hello World</h1></div>"


def test_parse_email__with_cc_addresses():
    data = MultiValueDict(
        subject=["Hello World!"],
        envelope=[
            '{"to":["foo@em7221.test-mail.anikalegal.com"],"from":"matt@anikalegal.com"}'
        ],
        cc=["bar@em7221.test-mail.anikalegal.com"],
        to=[
            "foo@em7221.test-mail.anikalegal.com, bar@em7221.test-mail.anikalegal.com,  joe blow <joe@gmail.com>"
        ],
        text=[
            "Hi Matt\r\n\r\nOn Sun, Jul 18, 2021 at 12:51 PM Matt Segal <matt@anikalegal.com> wrote:\r\n\r\n> hmmm\r\n>\r\n> --\r\n>\r\n> Matthew Segal\r\n>\r\n> Head of Technology\r\n>\r\n> mobile: 0431 417 373\r\n>\r\n> email: matt@anikalegal.com\r\n>\r\n> site: www.anikalegal.com\r\n>\r\n> Level 2/520 Bourke Street\r\n>\r\n> Melbourne VIC 3000\r\n>\n"
        ],
        html=["<div><h1>Hello World</h1></div>"],
    )
    files = MultiValueDict()
    assert Email.objects.count() == 0
    process_inbound_email(data, files)
    assert Email.objects.count() == 1
    email = Email.objects.last()
    assert email.from_addr == "matt@anikalegal.com"
    assert email.to_addr == "foo@em7221.test-mail.anikalegal.com"
    assert (
        email.to_addrs
        == "foo@em7221.test-mail.anikalegal.com, bar@em7221.test-mail.anikalegal.com,  joe blow <joe@gmail.com>"
    )
    assert email.cc_addrs == "bar@em7221.test-mail.anikalegal.com"
    assert email.subject == "Hello World!"
    assert email.state == EmailState.RECEIVED
    assert (
        email.text
        == "Hi Matt\n\nOn Sun, Jul 18, 2021 at 12:51 PM Matt Segal <matt@anikalegal.com> wrote:\n\n> hmmm\n>\n> --\n>\n> Matthew Segal\n>\n> Head of Technology\n>\n> mobile: 0431 417 373\n>\n> email: matt@anikalegal.com\n>\n> site: www.anikalegal.com\n>\n> Level 2/520 Bourke Street\n>\n> Melbourne VIC 3000\n>\n"
    )
    assert email.html == "<div><h1>Hello World</h1></div>"


def test_parse_email__with_files():
    pass
