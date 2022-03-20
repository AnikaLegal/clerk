import React from "react";
import { Transition } from "react-transition-group";

const DURATION = 300;

const defaultStyle = {
  transition: `opacity ${DURATION}ms ease-in-out`,
  opacity: 0,
};

const transitionStyles = {
  entering: { opacity: 1 },
  entered: { opacity: 1 },
  exiting: { opacity: 0 },
  exited: { opacity: 0 },
};

export const FadeTransition = ({ in: inProp, children }) => (
  <Transition in={inProp} timeout={DURATION}>
    {(state) => (
      <div
        style={{
          ...defaultStyle,
          ...transitionStyles[state],
        }}
      >
        {children}
      </div>
    )}
  </Transition>
);
