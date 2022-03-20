const http = {
  get: (url, query) => {
    let finalURL = url;
    if (query) {
      const qs = new URLSearchParams(query).toString();
      finalURL = `${url}?${qs}`;
    }
    const config = {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    };
    return fetch(finalURL, config)
      .then((response) => response.json())
      .catch((err) => {
        console.error("Error when fetching results:", err.message);
      });
  },
};

export const api = {
  templates: {
    email: {
      search: (query) => {
        const url = "/clerk/templates/email/search/";
        return http.get(url, query);
      },
    },
  },
};
