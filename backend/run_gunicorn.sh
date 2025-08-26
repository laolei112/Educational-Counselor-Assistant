#!/bin/bash


# 普通提示
notify()
{
    COLOR='\E[1;32m' #32:绿 31:红
    RES='\E[0m'
    echo -e "${COLOR}"$1" ${RES}"
}

# 失败提示
error_notify(){
    COLOR='\E[1;31m' #32:绿 31:红
    RES='\E[0m'
    echo -e "${COLOR}"$1" ${RES}"
}

# 成功提示
success_notify()
{
    COLOR='\E[1;32m' #32:绿 31:红
    RES='\E[0m'
    echo -e "${COLOR}"$1" ${RES}"
}

# 输出错误提示
output_usage()
{
    echo
    echo "#[USAGE] >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
    echo "start.sh dev"
    echo "start.sh prd"
    echo "start.sh stop"
    echo "#[USAGE] <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
}

CMD=$1

run_gunicorn()
{
    echo "GPT_ENV:  $GPT_ENV"

    if [ -d "backend/static_cdn" ]; then
        rm -rf "backend/static_cdn"
    fi
    mkdir -p backend/static_cdn
    mkdir -p backend/dist/static

    if [ -e $HOME/.bashrc ]; then
        source $HOME/.bashrc
    fi
    if [ -z "$PYTHONPATH" ]; then
        export PYTHONPATH="python3"
    fi
    if [ -z "$GUNICORNPATH" ]; then
        export GUNICORNPATH="gunicorn"
    fi

    $PYTHONPATH --version
    $PYTHONPATH manage.py migrate
    $PYTHONPATH manage.py collectstatic
    $GUNICORNPATH backend.wsgi:application -t 900 -c config/gunicorn/backend.py --capture-output --access-logfile log/backend_access.log
    echo $?
}

run_gunicorn
