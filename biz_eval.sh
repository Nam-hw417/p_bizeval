#!/bin/bash

ps gx | grep "biz_eval.py" | grep -v grep | awk '{cmd=sprintf("kill %s",$1); system(cmd); system("sleep 5");}'

nohup streamlit run --server.fileWatcherType none --server.port 18882 biz_eval.py > ./biz_eval.log &
echo "App Start ::: BizEval"