#!/bin/bash

set -e
base="$(cd `dirname $0`; pwd)"
if [ ! -f "$base/python.tar" ];then
    echo "Not python images can't be load"
    exit
fi
if [ ! -f "$base/fateboard.tar" ];then
    echo "Not fateboard images can't be load"
    exit
fi

if [ ! -d "$base/fate/data" ];then
    mkdir -p $base/fate/data
fi
if [ ! -d "$base/fate/log" ];then
    mkdir -p $base/fate/log
fi

docker load < python.tar
docker load < fateboard.tar
docker images
tar xvf data.tar.gz -C $base/fate
nohup docker-compose -f docker_standalone.yml up &
docker ps -a
