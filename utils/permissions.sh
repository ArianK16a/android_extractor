all_files=$(sudo find $1 -type f)
for i in $all_files
do
    sudo chmod 0777 $i
done
