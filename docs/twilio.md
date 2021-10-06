## Twilio

We are using Twilio to handle inbound phone calls in the `caller` app. To test Twilio locally:

- Ensure you have access to the Anika Twilio account
- Ensure you have set the correct Twilio envars in your .env file (see "Getting Started" section)
- Start the Django server
- Install and run [ngrok](https://ngrok.com/) for port 8000: `ngrok http 8000`
- Login to Twilio and [configure the test phone webhook](https://www.twilio.com/console/phone-numbers/PN5ab5df1280aa1456035801dd1a25824a) so that it points to your ngrok endpoint, eg. `http://88b59b03d2fd.ngrok.io/caller/answer/`
- Ring the test number on +61480015687
- When finished, change the webhook back to staging: `https://test-clerk.anikalegal.com/caller/answer/`
