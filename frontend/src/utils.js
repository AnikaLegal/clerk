import React, { useEffect, useRef } from "react";
import { hydrate, render } from "react-dom";

// Skips first update
export const useEffectLazy = (func, vars) => {
  const isFirstUpdate = useRef(true);
  useEffect(() => {
    if (isFirstUpdate.current) {
      isFirstUpdate.current = false;
    } else {
      func();
    }
  }, vars);
};

export const mount = (App) => {
  const root = document.getElementById("app");
  if (root.hasChildNodes()) {
    hydrate(<App />, root);
  } else {
    render(<App />, root);
  }
};

export const debounce = (delay) => {
  let timer = null;
  return (func) => {
    return (...args) => {
      clearTimeout(timer);
      timer = setTimeout(() => func(...args), delay);
    };
  };
};

// Debounce user input, returns a promise
export const debouncePromise = (delay) => {
  let timer = null;
  return (func) => {
    return (...args) =>
      new Promise((resolve) => {
        clearTimeout(timer);
        timer = setTimeout(() => func(...args).then(resolve), delay);
      });
  };
};

// Wait n seconds
export const waitSeconds = (delay) =>
  new Promise((resolve) => setTimeout(() => resolve(), delay * 1000));

export const useOutsideClick = (ref, onClickOutside) => {
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (ref.current && !ref.current.contains(event.target)) {
        onClickOutside();
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [ref]);
};
