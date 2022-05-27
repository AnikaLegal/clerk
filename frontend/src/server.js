import React from "react";
import { renderToString } from "react-dom/server";
import { ServerStyleSheet } from "styled-components";
import express from "express";

const EXPRESS_PORT = process.env.EXPRESS_PORT;
global.document = null;
global.window = {
  IS_SSR: true,
};

const app = express();
app.use(express.json({ limit: "1mb" }));

app.get("/", (req, res) => {
  return res.send("Server is working");
});

app.post("/render/:page/", (req, res) => {
  const pageName = req.params.page;
  try {
    console.log("Rendering page", pageName);
    console.time("render");
    const page = require(`./pages/${pageName}.js`);
    const App = page.getApp(req.body);
    const sheet = new ServerStyleSheet();
    const html = renderToString(sheet.collectStyles(<App />));
    const styleTags = sheet.getStyleTags();
    sheet.seal();
    console.timeEnd("render");
    res.send(styleTags + html);
  } catch (err) {
    console.timeEnd("render");
    console.error("Error rendering page", pageName, err);
    return res.status(500).send("");
  }
});

app.listen(EXPRESS_PORT, () => {
  console.log(`Rendering server is listening on port ${EXPRESS_PORT}`);
});
