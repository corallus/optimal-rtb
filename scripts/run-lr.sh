#!/usr/bin/env bash
advs="1458 2259 2261 2821 2997 3358 3386 3427 3476"
folder=/data/vincent/make-ipinyou-data
for adv in $advs; do
    echo $adv
    python ../utilities/lryzx.py $folder/$adv/train.yzx.txt $folder/$adv/test.yzx.txt
done
