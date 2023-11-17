#!/bin/bash

if [[ "${1}" == "celery" ]]; then
  celery --app=src.background.app:celery worker -l INFO
elif [[ "${1}" == "flower" ]]; then
  celery --app=src.background.app:celery flower
fi