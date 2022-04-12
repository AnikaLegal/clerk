export const URLS = {
  PERSON: {
    LIST: "/clerk/parties/",
    CREATE: "/clerk/parties/create/",
  },
  ACCOUNTS: {
    SEARCH: "/clerk/accounts/",
  },
};

export const STAGES = {
  UNSTARTED: "Not started",
  CLIENT_AGREEMENT: "Client agreement",
  ADVICE: "Drafting advice",
  FORMAL_LETTER: "Formal letter sent",
  NEGOTIATIONS: "Negotiations",
  VCAT_CAV: "VCAT/CAV",
  POST_CASE_INTERVIEW: "Post-case interview",
  CLOSED: "Closed",
};
export const OUTCOMES = {
  OUT_OF_SCOPE: "Out of scope",
  CHANGE_OF_SCOPE: "Change of scope",
  RESOLVED_EARLY: "Resolved early",
  CHURNED: "Churned",
  UNKNOWN: "Unknown",
  SUCCESSFUL: "Successful",
  UNSUCCESSFUL: "Unsuccessful",
};
export const CASE_TYPES = {
  REPAIRS: "Repairs",
  BONDS: "Bonds",
  EVICTION: "Eviction",
};
