import { ReactNode } from 'react'
import { LINKS, ROUTES } from '../consts'

export interface ExitPageContent {
  title: string
  body: ReactNode
}

// Keyed by client route (see consts.ts ROUTES). Copy is ported verbatim from
// the old intake repo's splash views (src/views/splash/).
export const EXIT_PAGES: Record<string, ExitPageContent> = {
  [ROUTES.GEOGRAPHY]: {
    title:
      'Unfortunately we are currently only able to help with the residential rental issues in Victoria, Australia:',
    body: (
      <>
        <p>
          Follow the links below to find local community legal centres in your
          state or territory that may be better placed to look into your matter.
        </p>
        <ul>
          <li>
            <a
              target="_blank"
              rel="noreferrer"
              href="https://www.clcnsw.org.au/"
            >
              NSW
            </a>
          </li>
          <li>
            <a
              target="_blank"
              rel="noreferrer"
              href="https://www.actlawsociety.asn.au/for-the-public/legal-help/community-legal-centres"
            >
              ACT
            </a>
          </li>
          <li>
            <a
              target="_blank"
              rel="noreferrer"
              href="https://www.communitylegalqld.org.au/"
            >
              QLD
            </a>
          </li>
          <li>
            <a
              target="_blank"
              rel="noreferrer"
              href="https://www.clcsa.org.au/"
            >
              SA
            </a>
          </li>
          <li>
            <a
              target="_blank"
              rel="noreferrer"
              href="https://www.communitylegalwa.org.au/pages/faqs/category/clc-location?Take=26"
            >
              WA
            </a>
          </li>
          <li>
            <a
              target="_blank"
              rel="noreferrer"
              href="https://nt.gov.au/community/multicultural-communities/support-for-communities/community-legal-services"
            >
              NT
            </a>
          </li>
          <li>
            <a
              target="_blank"
              rel="noreferrer"
              href="http://www.clctas.org.au/"
            >
              TAS
            </a>
          </li>
        </ul>
      </>
    ),
  },
  [ROUTES.LEGAL_SCOPE_COMPENSATION]: {
    title:
      'As your matter is about compensation from your landlord, your issue is outside of Anika’s current scope. Unfortunately, we are not able to assist you at this time.',
    body: (
      <>
        <p>
          You may wish to contact your local community legal centres who will be
          better placed to look into your matter. Follow the link below to see
          what is available in your area.
        </p>
        <p>
          <a href={LINKS.VIC_LEGAL_AID} target="_blank" rel="noreferrer">
            Legal centres
          </a>
        </p>
      </>
    ),
  },
  [ROUTES.INELIGIBLE_MEANS]: {
    title:
      'After assessing the facts of your case, we have determined your issue is outside of Anika’s current scope. Unfortunately, we are not able to assist you at this time.',
    body: (
      <>
        <p>
          Based on your responses, your income is above our eligibility
          requirements.
        </p>
        <p>
          Due to our capacity, we must prioritise people who fall within our
          eligibility criteria. We hope that you understand our capacity
          limitations.
        </p>
        <p>
          If you are not eligible for free legal help, you might wish to get
          legal information from&nbsp;
          <a
            href="https://www.consumer.vic.gov.au/contact-us"
            target="_blank"
            rel="noreferrer"
          >
            Consumer Affairs Victoria
          </a>
          &nbsp;or engage a&nbsp;
          <a
            href="https://www.liv.asn.au/Referral"
            target="_blank"
            rel="noreferrer"
          >
            private lawyer.
          </a>
        </p>
      </>
    ),
  },
  [ROUTES.INELIGIBLE_REPAIRS_APPLIED_VCAT]: {
    title: 'We are sorry we cannot represent you at VCAT.',
    body: (
      <>
        <p>
          You may wish to contact your local community legal centres who will be
          better placed to look into your matter. Follow the link below to see
          what is available in your area.
        </p>
        <p>
          <a href={LINKS.VIC_LEGAL_AID} target="_blank" rel="noreferrer">
            Legal centres
          </a>
        </p>
      </>
    ),
  },
  [ROUTES.INELIGIBLE_REPAIRS_GOTTEN_VCAT]: {
    title:
      "Our Repairs service focuses on helping renters write a formal compliance request to their real estate agent and/or rental provider, and our service scope ends once a Repairs Order has been obtained. Based on what you've told us, you have already obtained a Repairs Order.",
    body: (
      <>
        <p>
          You may wish to contact your local community legal centres who will be
          better placed to look into your matter. Follow the link below to see
          what is available in your area.
        </p>
        <p>
          <a href={LINKS.VIC_LEGAL_AID} target="_blank" rel="noreferrer">
            Legal centres
          </a>
        </p>
      </>
    ),
  },
  [ROUTES.INELIGIBLE_NO_EVICTIONS_NOTICE]: {
    title:
      'Unfortunately we are currently only able to help when your landlord or real estate agent has begun the evictions process by sending you a Notice to Vacate. If that happens, please come back and let us know.',
    body: (
      <>
        <p>
          For more information about the evictions process, please see the{' '}
          <a
            href={LINKS.EVICTIONS_AND_POSSESSION_ORDERS_INFO}
            target="_blank"
            rel="noreferrer"
          >
            Consumer Affairs Victoria Website
          </a>
          .
        </p>
      </>
    ),
  },
  [ROUTES.INELIGIBLE_ALREADY_REMOVED]: {
    title:
      'Unfortunately, we are unable to assist if you have already been evicted from the property.',
    body: (
      <>
        <p>
          For legal help, follow the link below to see what is available in your
          area.
        </p>
        <p>
          <a href={LINKS.VIC_LEGAL_AID} target="_blank" rel="noreferrer">
            Legal centres
          </a>
        </p>
      </>
    ),
  },
  [ROUTES.INELIGIBLE_VCAT_HEARING]: {
    title:
      'Unfortunately our evictions service is not an urgent advice service. We do not have capacity to assist you in time for your next VCAT hearing.',
    body: (
      <>
        <p>
          We suggest you contact{' '}
          <a
            href="https://www.legalaid.vic.gov.au/node/11560"
            target="_blank"
            rel="noreferrer"
          >
            Victoria Legal Aid's Legal Help
          </a>{' '}
          for advice.
        </p>
      </>
    ),
  },
  [ROUTES.BONDS_RECOVERY]: {
    title:
      'Our bond recovery service focuses on helping you negotiate a settlement with your landlord once they have applied to VCAT to claim your bond held at the RTBA.',
    body: (
      <>
        <p>
          Due to resource constraints, we are currently unable to assist with
          bond issues where you have general questions about bonds prior to
          leaving the property, the bond is not held by the RTBA, your dispute
          is with a co-tenant, or if your landlord hasn't applied to VCAT yet.
          Depending on your situation, you may wish to have a look at our
          <a href={LINKS.BONDS_RESOURCES}> bonds resources</a>.
        </p>
      </>
    ),
  },
}
