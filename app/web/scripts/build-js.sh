#!/usr/bin/env bash

set -o errexit

mkdir -p /dist/web/scripts /dist/web/styles
cp ./node_modules/htmx.org/dist/htmx.min.js /dist/web/scripts/
cp ./node_modules/embla-carousel/embla-carousel.umd.js /dist/web/scripts/
cp ./node_modules/embla-carousel-autoplay/embla-carousel-autoplay.umd.js /dist/web/scripts/
cp ./node_modules/glightbox/dist/js/glightbox.min.js /dist/web/scripts/
cp ./node_modules/glightbox/dist/css/glightbox.min.css /dist/web/styles/
