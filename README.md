# lets do it
 a TODO dashboard for #TODOs in your repo


1. Go to your git repo (or git clone a repo on which you want to run this tracker)
2. run the blamer script
3. submit the blame_results.txt


```
git grep -n "TODO" -- '*.py'| 
while read -d $'\n' task
do 
	split=(${task//:/ })
 	file=${split[0]}
 	line=${split[1]}
  	git blame --line-porcelain -L  $line,$line $file
	echo "--blame-end--"
done > blame_results.txt
```
