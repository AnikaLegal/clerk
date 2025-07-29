# Clerk

[![Test](https://github.com/AnikaLegal/clerk/actions/workflows/test.yml/badge.svg?branch=develop)](https://github.com/AnikaLegal/clerk/actions/workflows/test.yml)

The Anika Legal case management system & website.

> Depending on the job, office clerks might answer phones, filing, data processing, faxing, envelope stuffing and mailing, message delivery, running errands, sorting incoming mail and much more. ([source](https://www.snagajob.com/job-descriptions/office-clerk/))

## Structure

This Django project has several apps:

- accounts: User accounts
- admin: Customization of Admin interface
- blacklist: List contacts to avoid
- caller: Call centre
- case: Case management system website
- clerk: Project settings
- core: Core domain models and functionality
- emails: Sending and receiving emails
- intake: User intake forms (Housing health check only)
- microsoft: Microsoft integration (Sharepoint)
- office: Alternative communications when the office is closed
- slack: Slack integration
- web: Public website and blog
- webhooks: Webhooks from 3rd party services

## Documentation

See here for documentation:

- [Changelog](docs/changelog.md)
- [Getting started](docs/setup.md)
- [Testing](docs/tests.md)
- [Infra and deployment](docs/infra.md)
- [Email integration](docs/emails.md)
- [Twilio integration](docs/twilio.md)
- [Sharepoint integration](docs/sharepoint.md)
- [Microsoft Graph integration](docs/msgraph.md)
