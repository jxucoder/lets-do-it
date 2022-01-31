#!/bin/bash

gclonecd() {
  git clone "$1" && cd "$(basename "$1" .git)"
}

mkdir tmp_git && cd tmp_git
gclonecd "$1"
git grep -n "TODO" -- '*.py'| 
while read -d $'\n' task
do 
	split=(${task//:/ })
 	file=${split[0]}
 	line=${split[1]}
  	git blame --line-porcelain -L  $line,$line $file
	echo "--blame-end--"
done > ~/work_space/lets-do-it/blame_results.txt
cd ../..