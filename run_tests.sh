#!/usr/bin/env bash

# Run integration tests (postgres, dynamodb)
# Requirements:
# - ENV:           required - environment variable, one of the choices: LOCAL, DEV, FAT
# - S3B:           optional - s3 bucket name available for uploading files
# - LOGSTASH_HOST: optional - environmant variable, host of logstash addr to push logs to
# - LOGSTASH_PORT: optional - environmant variable, port of logstash addr to push logs to
# - $1:            required - name of vendor to run tests for (choices: Mecomo, Zillion, Kirsen)

# check all arguments is ok
set -u

VENDOR=$1
LOGSTASH_HOST=${LOGSTASH_HOST:-''}
LOGSTASH_PORT=${LOGSTASH_PORT:-''}

# internal variable for python tests
export IOT_ENV=$ENV
export S3B_NAME=${S3B:-''}

echo "Starting tests for $VENDOR in env $ENV"

report_file="${VENDOR}_intake_report_$(date +%Y%m%d_%H%M%S).html"
log_file="${VENDOR}_intake_report_$(date +%Y%m%d_%H%M%S).log"
host=${PWD}/tests/IOT_Intake/${VENDOR}
dest=/IOT/tests/IOT_Intake/${VENDOR}

function logstash() {
    # Send specified message to logstash
    # $1 - message to send

    local message="$1"
    echo "LOG: $message"

    if [ -z "$LOGSTASH_PORT" ] || [ -z "$LOGSTASH_PORT" ]; then
        echo "No Logstash specified to push logs to"
        return;
    fi

    echo "Send log to Logstash: $LOGSTASH_HOST:$LOGSTASH_PORT"

    python -c "
import json
import sys

msg = {
    'level_name':'INFO',
    'type':'iot-logs',
    'message': sys.argv[1],
    '@version': '1',
    'thread_name': 'main',
    'service': 'iot-api-integration-tests',
    'level': 'INFO',
    'stage': sys.argv[2],
    'host': sys.argv[3],
    'applicationName': 'iot-api-integration-tests',
    'logger_name': 'iot-api-integration-tests-logger'
}
print(json.dumps(msg))
" "$message" $ENV "kube-`hostname`" | nc $LOGSTASH_HOST $LOGSTASH_PORT
}

logstash "Start integration tests for ${VENDOR}"

mkdir -p ${dest}/Reports

set -o pipefail

pytest -v --tb=short ${dest} --html=${dest}/Reports/${report_file} | tee -a ${dest}/Reports/${log_file}

retcode=$?

if [ $retcode -eq 0 ]; then
  rm -rf ${host}/IntakeRaw
  logstash "Test for ${VENDOR} has succeed"
else
  if [ -z "$S3B" ]; then
    logstash "[ERROR] Test for ${VENDOR} has failed"
  else
    zip_file="${VENDOR}_$(date +%Y%m%d_%H%M%S).zip"
    zip -9 -r --exclude=*.py* ${zip_file} ${dest}
    python /IOT/s3upload.py ${zip_file}
    logstash "[ERROR] Test for ${VENDOR} has failed. The results ${zip_file} saved to S3 bucket $S3B"
  fi
  rm -rf ${dest}/IntakeRaw
  rm -rf ${dest}/__pycache__
fi

exit $retcode
