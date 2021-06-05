#!/bin/bash
cd ui
npm install
npm run build
cp -a dist/. ../src/static/vue/dist
