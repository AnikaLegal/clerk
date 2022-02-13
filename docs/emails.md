# Emails

We use SendGrid to send and receive emails.

Emails are sent using the [Django email API](https://docs.djangoproject.com/en/3.2/topics/email/) via SendGrid's SMTP servers.

Emails are received via SendGrid's [inbound parse webhook](https://docs.sendgrid.com/for-developers/parsing-email/setting-up-the-inbound-parse-webhook#default-parameters),
where they send us a POST request to an endpoint of ours (`/email/receive/`) whenever we get an email.

Each environment (dev/test/prod) has its own email subdomain.

## Development setup

To listen for inbound emails in your development environment run [ngrok](https://ngrok.com/). This will print the public endpoint, e.g "https://90c8-194-193-130-131.ngrok.io".

```bash
# Start ngrok (https://ngrok.com/) and take note of the address
ngrok http 8000
```

Then, in a separate terminal session, update dev Sendgrid settings via API

```
inv ngrok https://90c8-194-193-130-131.ngrok.io
```

Then wait a minute or so for these settings to propagate. You can see these settings in the SendGrid web UI [here](https://app.sendgrid.com/settings/parse).

Dev emails can be sent to the subdomain `em9463.dev-mail.anikalegal.com`. Check the case email tab in the Clerk web UI to get a test email.
