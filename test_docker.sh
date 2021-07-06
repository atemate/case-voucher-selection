#!/bin/bash
TIMEOUT=${TIMEOUT:-5m}
DELAY=${DELAY:-5s}

timeout ${TIMEOUT} bash -c "until curl -q --fail http://0.0.0.0:8080/ping; do date; sleep ${DELAY}; done"
