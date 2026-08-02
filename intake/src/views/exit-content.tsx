import { ReactNode } from 'react'
import { OffboardPrimary, OffboardReferral } from '../comps/Offboard'
import { LINKS, ROUTES } from '../consts'

// Content for one exit page, rendered on the offboarding template (see
// comps/Offboard and views/ExitPage).
export interface ExitPageContent {
  headline: string
  explanation: ReactNode
  body?: ReactNode
  primary?: OffboardPrimary
  dataNote?: ReactNode
}

// The referral shared by most exits: Victoria Legal Aid, as a referral card
// in the body slot.
const VLA_REFERRAL = (
  <div className="intake-offboard__referrals">
    <OffboardReferral
      name="Victoria Legal Aid"
      description="Find legal help available in your area"
      href={LINKS.VIC_LEGAL_AID}
    />
  </div>
)

// Keyed by client route (see consts.ts ROUTES). Copy is ported from the old
// intake repo's splash views (src/views/splash/), re-cut to the template's
// slots: the apologetic title prefixes are dropped, and each page's trailing
// "you may wish to contact ..." pointer becomes a referral card.
export const EXIT_PAGES: Record<string, ExitPageContent> = {
  [ROUTES.INELIGIBLE_OUTSIDE_VICTORIA]: {
    headline:
      'We can currently only help with residential rental issues in Victoria, Australia',
    explanation:
      'Follow the links below to find local community legal centres in ' +
      'your state or territory that may be better placed to look into ' +
      'your matter.',
    body: (
      <div className="intake-offboard__referrals">
        <OffboardReferral
          name="ACT Law Society"
          description="Find a community legal centre in the Australian Capital Territory"
          href="https://www.actlawsociety.asn.au/for-the-public/legal-help/community-legal-centres"
          tag="ACT"
        />
        <OffboardReferral
          name="Community Legal Centres NSW"
          description="Free legal help across New South Wales"
          href="https://www.clcnsw.org.au/"
          tag="NSW"
        />
        <OffboardReferral
          name="NT.GOV.AU"
          description="The Northern Territory Government's guide to getting legal advice"
          href="https://nt.gov.au/law/processes/get-legal-advice/introduction"
          tag="NT"
        />
        <OffboardReferral
          name="Community Legal Centres Queensland"
          description="Free legal help across Queensland"
          href="https://www.clcq.org.au/"
          tag="QLD"
        />
        <OffboardReferral
          name="Community Legal Centres South Australia"
          description="Free legal advice, assistance and referrals across South Australia"
          href="https://www.clcsa.org.au/"
          tag="SA"
        />
        <OffboardReferral
          name="Community Legal Centres Tasmania"
          description="Free legal help across Tasmania"
          href="https://clctas.org.au/"
          tag="TAS"
        />
        <OffboardReferral
          name="Community Legal WA"
          description="Find free legal help in Western Australia"
          href="https://communitylegalwa.org.au/need-legal-help/"
          tag="WA"
        />
      </div>
    ),
  },
  [ROUTES.INELIGIBLE_COMPENSATION]: {
    headline: 'Compensation claims are outside Anika’s current scope',
    explanation:
      'As your matter is about seeking compensation from your landlord, we ' +
      'are not able to assist you at this time.',
    body: VLA_REFERRAL,
  },
  [ROUTES.INELIGIBLE_INCOME]: {
    headline: 'Your income is above our eligibility requirements',
    explanation:
      'Due to our limited capacity, we must prioritise people who fall ' +
      'within our eligibility criteria. We hope you understand.',
    body: (
      <div className="intake-offboard__referrals">
        <OffboardReferral
          name="Consumer Affairs Victoria"
          description="Get legal information about renting"
          href="https://www.consumer.vic.gov.au/contact-us"
        />
        <OffboardReferral
          name="Law Institute of Victoria"
          description="Engage a private lawyer through their referral service"
          href="https://www.liv.asn.au/legalhelp"
        />
      </div>
    ),
  },
  [ROUTES.EXIT_VCAT_REPRESENTATION]: {
    headline: 'We cannot represent you at VCAT',
    explanation:
      'You may wish to contact Victoria Legal Aid to find legal help ' +
      'available in your area.',
    body: VLA_REFERRAL,
  },
  [ROUTES.INELIGIBLE_REPAIRS_ORDER_OBTAINED]: {
    headline:
      'We are unable to help further once a Repairs Order has been obtained',
    explanation:
      'Our Repairs service focuses on helping renters write a formal ' +
      'compliance request to their real estate agent or rental provider, ' +
      'and our service ends once a Repairs Order has been obtained. Based ' +
      "on what you've told us, you have already obtained one.",
    body: VLA_REFERRAL,
  },
  [ROUTES.INELIGIBLE_NO_NOTICE_TO_VACATE]: {
    headline:
      'We can only help once your landlord or real estate agent has sent you a Notice to Vacate',
    explanation:
      'If you receive a Notice to Vacate, please come back and let us know.',
    body: (
      <div className="intake-offboard__referrals">
        <OffboardReferral
          name="Consumer Affairs Victoria"
          description="Learn more about the evictions process"
          href={LINKS.EVICTIONS_AND_POSSESSION_ORDERS_INFO}
        />
      </div>
    ),
  },
  [ROUTES.INELIGIBLE_ALREADY_EVICTED]: {
    headline:
      'We are unable to assist if you have already been evicted from the property',
    explanation:
      'You may wish to contact Victoria Legal Aid to find legal help ' +
      'available in your area.',
    body: VLA_REFERRAL,
  },
  [ROUTES.INELIGIBLE_URGENT_HEARING]: {
    headline: 'We are unable to assist you in time for your next VCAT hearing',
    explanation: 'Our evictions service is not an urgent advice service.',
    body: (
      <div className="intake-offboard__referrals">
        <OffboardReferral
          name="Victoria Legal Aid Legal Help"
          description="Contact them about urgent legal advice"
          href="https://www.legalaid.vic.gov.au/speak-to-us"
        />
      </div>
    ),
  },
  [ROUTES.INELIGIBLE_BOND_OUT_OF_SCOPE]: {
    headline: 'Your bond issue is outside our current scope',
    explanation:
      'Our bond recovery service focuses on helping you negotiate a ' +
      'settlement with your landlord once they have applied to VCAT to ' +
      'claim your bond held at the RTBA.',
    body: (
      <>
        <p>
          Due to resource constraints, we are currently unable to assist when:
        </p>
        <ul>
          <li>
            you have general questions about bonds before leaving the property
          </li>
          <li>your bond is not held by the RTBA</li>
          <li>your dispute is with a co-tenant</li>
          <li>your landlord has not applied to VCAT yet</li>
        </ul>
      </>
    ),
    primary: { label: 'See our bonds resources', href: LINKS.BONDS_RESOURCES },
  },
}
