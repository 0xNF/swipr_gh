#!/usr/bin/env bash
export PATH=/home/science/anaconda3/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games
. /home/science/anaconda3/etc/profile.d/conda.sh
conda activate fastai-cpu
source ~/swipr/swiprvars.sh
python ./swiprsscriptserver.py > ./sss_logs.txt