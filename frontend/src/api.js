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
  templates: {
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
