import { URLS } from "consts";

const getCookie = (name) => {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) {
    return parts.pop().split(";").shift();
  }
};

const BASE_CONFIG = {
  method: null,
  credentials: "include",
  headers: {
    "X-React": "true",
    "X-CSRFToken": getCookie("csrftoken"),
    "Content-Type": "application/json",
  },
};

const handleResponse = async (resp) => {
  let data = {};
  if (resp.status !== 204) {
    try {
      data = await resp.json();
    } catch {
      console.error("Could not parse response JSON.");
    }
  }
  return { resp, data };
};

const sendData = async (url, data, method) => {
  const config = {
    ...BASE_CONFIG,
    method: method,
    body: JSON.stringify(data),
  };
  const resp = await fetch(url, config);
  return handleResponse(resp);
};

const http = {
  post: (url, data) => sendData(url, data, "POST"),
  patch: (url, data) => sendData(url, data, "PATCH"),
  put: (url, data) => sendData(url, data, "PUT"),
  get: async (url, query) => {
    let finalURL = url;
    if (query) {
      const qs = new URLSearchParams(query).toString();
      finalURL = `${url}?${qs}`;
    }
    const config = { ...BASE_CONFIG, method: "GET" };
    const resp = await fetch(finalURL, config);
    return handleResponse(resp);
  },
  delete: async (url) => {
    const config = { ...BASE_CONFIG, method: "DELETE" };
    const resp = await fetch(url, config);
    return handleResponse(resp);
  },
};

export const api = {
  person: {
    list: () => {
      return http.get(URLS.PERSON.LIST);
    },
  },
  case: {
    update: (caseId, issue) => {
      const url = `/clerk/cases/detail/${caseId}/update/`;
      return http.post(url, issue);
    },
    // Assign a paralegal + lawyer
    assign: (caseId, issue) => {
      const url = `/clerk/cases/detail/${caseId}/assign/`;
      return http.post(url, issue);
    },
    note: {
      add: (caseId, note) => {
        const url = `/clerk/cases/detail/${caseId}/note/`;
        return http.post(url, note);
      },
    },
    agent: {
      add: (caseId, agentId) => {
        const url = `/clerk/cases/detail/${caseId}/agent/`;
        return http.post(url, { person_id: agentId });
      },
      remove: (caseId) => {
        const url = `/clerk/cases/detail/${caseId}/agent/`;
        return http.delete(url);
      },
    },
    landlord: {
      add: (caseId, landlordId) => {
        const url = `/clerk/cases/detail/${caseId}/landlord/`;
        return http.post(url, { person_id: landlordId });
      },
      remove: (caseId) => {
        const url = `/clerk/cases/detail/${caseId}/landlord/`;
        return http.delete(url);
      },
    },
  },
  accounts: {
    search: (query) => {
      const url = "/clerk/accounts/";
      return http.get(URLS.ACCOUNTS.SEARCH, query);
    },
  },
  templates: {
    doc: {
      search: (query) => {
        const url = "/clerk/templates/doc/search/";
        return http.get(url, query);
      },
      delete: (pk) => {
        const url = `/clerk/templates/doc/${pk}/delete/`;
        return http.delete(url);
      },
    },
    email: {
      search: (query) => {
        const url = "/clerk/templates/email/search/";
        return http.get(url, query);
      },
      create: (data) => {
        const url = "/clerk/templates/email/create/";
        return http.post(url, data);
      },
      update: (pk, data) => {
        const url = `/clerk/templates/email/${pk}/`;
        return http.put(url, data);
      },
    },
  },
};
