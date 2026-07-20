import { ReactNode } from 'react'
import { LINKS, ROUTES } from '../consts'

export interface ExitPageContent {
  title: string
  body: ReactNode
}

// Keyed by client route (see consts.ts ROUTES). Copy is ported verbatim from
// the old intake repo's splash views (src/views/splash/).
export const EXIT_PAGES: Record<string, ExitPageContent> = {
  [ROUTES.INELIGIBLE_OUTSIDE_VICTORIA]: {
    title:
      'Unfortunately, we can currently only help with residential rental issues in Victoria, Australia.',
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
              href="https://www.clcq.org.au/"
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
              href="https://communitylegalwa.org.au/need-legal-help/"
            >
              WA
            </a>
          </li>
          <li>
            <a
              target="_blank"
              rel="noreferrer"
              href="https://nt.gov.au/law/processes/get-legal-advice/introduction"
            >
              NT
            </a>
          </li>
          <li>
            <a
              target="_blank"
              rel="noreferrer"
              href="https://clctas.org.au/"
            >
              TAS
            </a>
          </li>
        </ul>
      </>
    ),
  },
  [ROUTES.INELIGIBLE_COMPENSATION]: {
    title: 'Unfortunately, compensation claims are outside Anika’s current scope.',
    body: (
      <>
        <p>
          As your matter is about seeking compensation from your landlord, we
          are not able to assist you at this time.
        </p>
        <p>
          You may wish to contact{' '}
          <a href={LINKS.VIC_LEGAL_AID} target="_blank" rel="noreferrer">
            Victoria Legal Aid
          </a>{' '}
          to find legal help available in your area.
        </p>
      </>
    ),
  },
  [ROUTES.INELIGIBLE_INCOME]: {
    title: 'Unfortunately, your income is above our eligibility requirements.',
    body: (
      <>
        <p>
          Due to our limited capacity, we must prioritise people who fall
          within our eligibility criteria. We hope you understand.
        </p>
        <p>
          If you are not eligible for free legal help, you can get legal
          information from{' '}
          <a
            href="https://www.consumer.vic.gov.au/contact-us"
            target="_blank"
            rel="noreferrer"
          >
            Consumer Affairs Victoria
          </a>{' '}
          or engage a{' '}
          <a
            href="https://www.liv.asn.au/legalhelp"
            target="_blank"
            rel="noreferrer"
          >
            private lawyer
          </a>
          .
        </p>
      </>
    ),
  },
  [ROUTES.EXIT_VCAT_REPRESENTATION]: {
    title: 'We are sorry we cannot represent you at VCAT.',
    body: (
      <p>
        You may wish to contact{' '}
        <a href={LINKS.VIC_LEGAL_AID} target="_blank" rel="noreferrer">
          Victoria Legal Aid
        </a>{' '}
        to find legal help available in your area.
      </p>
    ),
  },
  [ROUTES.INELIGIBLE_REPAIRS_ORDER_OBTAINED]: {
    title:
      'Unfortunately, we are unable to help further once a Repairs Order has been obtained.',
    body: (
      <>
        <p>
          Our Repairs service focuses on helping renters write a formal
          compliance request to their real estate agent or rental provider, and
          our service ends once a Repairs Order has been obtained. Based on
          what you&apos;ve told us, you have already obtained one.
        </p>
        <p>
          You may wish to contact{' '}
          <a href={LINKS.VIC_LEGAL_AID} target="_blank" rel="noreferrer">
            Victoria Legal Aid
          </a>{' '}
          to find legal help available in your area.
        </p>
      </>
    ),
  },
  [ROUTES.INELIGIBLE_NO_NOTICE_TO_VACATE]: {
    title:
      'Unfortunately, we can only help once your landlord or real estate agent has sent you a Notice to Vacate.',
    body: (
      <>
        <p>If you receive a Notice to Vacate, please come back and let us know.</p>
        <p>
          For more information about the evictions process, see the{' '}
          <a
            href={LINKS.EVICTIONS_AND_POSSESSION_ORDERS_INFO}
            target="_blank"
            rel="noreferrer"
          >
            Consumer Affairs Victoria website
          </a>
          .
        </p>
      </>
    ),
  },
  [ROUTES.INELIGIBLE_ALREADY_EVICTED]: {
    title:
      'Unfortunately, we are unable to assist if you have already been evicted from the property.',
    body: (
      <p>
        You may wish to contact{' '}
        <a href={LINKS.VIC_LEGAL_AID} target="_blank" rel="noreferrer">
          Victoria Legal Aid
        </a>{' '}
        to find legal help available in your area.
      </p>
    ),
  },
  [ROUTES.INELIGIBLE_URGENT_HEARING]: {
    title:
      'Unfortunately, we are unable to assist you in time for your next VCAT hearing.',
    body: (
      <>
        <p>Our evictions service is not an urgent advice service.</p>
        <p>
          We suggest you contact{' '}
          <a
            href="https://www.legalaid.vic.gov.au/speak-to-us"
            target="_blank"
            rel="noreferrer"
          >
            Victoria Legal Aid&apos;s Legal Help
          </a>{' '}
          for advice.
        </p>
      </>
    ),
  },
  [ROUTES.INELIGIBLE_BOND_OUT_OF_SCOPE]: {
    title: 'Unfortunately, your bond issue is outside our current scope.',
    body: (
      <>
        <p>
          Our bond recovery service focuses on helping you negotiate a
          settlement with your landlord once they have applied to VCAT to claim
          your bond held at the RTBA.
        </p>
        <p>Due to resource constraints, we are currently unable to assist when:</p>
        <ul>
          <li>you have general questions about bonds before leaving the property</li>
          <li>your bond is not held by the RTBA</li>
          <li>your dispute is with a co-tenant</li>
          <li>your landlord has not applied to VCAT yet</li>
        </ul>
        <p>
          Depending on your situation, you may wish to have a look at our{' '}
          <a href={LINKS.BONDS_RESOURCES}>bonds resources</a>.
        </p>
      </>
    ),
  },
}
