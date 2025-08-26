#!/bin/bash

GPT_HOME_DIR="$HOME/gpt/py-gpt/"
GPT_RUN_DIR="$GPT_HOME_DIR/run"
GPT_LOG_DIR="$GPT_RUN_DIR/log"
mkdir -p $GPT_RUN_DIR
mkdir -p $GPT_LOG_DIR

export PATH=$HOME/.local/bin:$PATH

if [ ! -e "log" ]; then
    ln -s "${GPT_LOG_DIR}" log
    if [ "$?" != 0 ]; then
        echo "ln -s log dir error!"
        exit 2
        echo "ln log dir success"
    fi
fi

SUPERVISOR_PATH="supervisord"
SUPERVISOR_CTRL_PATH="supervisorctl"

action=$1


start_prd()
{
    export GPT_ENV="PRD"
    start
}

start_dev()
{
    export GPT_ENV="DEV"
    start
}

start_test()
{
    export GPT_ENV="TEST"
    start
}

function start() {
  echo "start"
  $SUPERVISOR_PATH -c "config/supervisord/supervisord.conf"
  check
}

function check() {
  $SUPERVISOR_CTRL_PATH -c "config/supervisord/supervisord.conf" status
  return $?
}

function stop() {
  check

  $SUPERVISOR_CTRL_PATH -c "config/supervisord/supervisord.conf" shutdown
  RESULT=$?
  if [ "RESULT" != "0" ];then
      PIDFILE="${GPT_RUN_DIR}/supervisord.pid"
      if [ -f "$PIDFILE" ];then
          cat $PIDFILE | xargs -I{} kill -9 {}
      fi
      if [ -f "$PIDFILE" ];then
          rm -f $PIDFILE
      fi
  fi
  ps -ef | grep "python" | grep -v "grep" | awk '{print $2}' | xargs -I {} kill -9 {}

  echo "stop success"
}

function check_start() {
  check
  RET="$?"
  if [ "$RET" != "0" ];then
    start
  fi
}

output_usage()
{
    echo
    echo "#[USAGE] >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
    echo "start.sh dev"
    echo "start.sh test"
    echo "start.sh prd"
    echo "start.sh stop"
    echo "#[USAGE] <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
}

case $action in
  "prd")
      start_prd
      ;;
  "dev")
      start_dev
      ;;
  "test")
      start_test
      ;;
  check)
    check
    ;;
  stop)
    stop
    ;;
  check_start)
    check_start
    ;;
  *)
    output_usage
    ;;
esac
