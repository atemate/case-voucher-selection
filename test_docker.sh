#!/bin/bash
TIMEOUT=${TIMEOUT:-2m}

timeout ${TIMEOUT} bash -c "until curl --fail http://0.0.0.0:8080/ping; do date; sleep 1; done"
