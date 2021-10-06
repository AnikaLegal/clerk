# Clerk

![Test](https://github.com/AnikaLegal/clerk/workflows/Test/badge.svg?branch=develop)

This site is used by new Anika clients who want to submit their legal problem. Clients may submit the facts of their case using a structured form interface. Their case file is then entered into our case managment system.

> Depending on the job, office clerks might answer phones, filing, data processing, faxing, envelope stuffing and mailing, message delivery, running errands, sorting incoming mail and much more. ([source](https://www.snagajob.com/job-descriptions/office-clerk/))

## Structure

This Django project has several apps:

- accounts: User accounts
- actionstep: Actionstep integration
- admin: Customization of Admin interface
- caller: Call centre
- case: Case management system website
- clerk: Project settings
- core: Core domain models and functionality
- slack: Slack integration
- web: Public website and blog
- webhooks: Webhooks from 3rd party services

## Documentation

See here for documentation:

- [Getting started](docs/setup.md)
- [Testing and linting](docs/tests.md)
- [Infra and deployment](docs/infra.md)
- [Email integration](docs/emails.md)
- [Twilio integration](docs/twilio.md)
