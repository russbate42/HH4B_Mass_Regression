## script to move root files from did containers into main folder
# saves did container information just because

FOLDER=$1

DID_DIR="${1}did.CONTAINERS/"
if [ -d "${DID_DIR}" ]; then
	echo ""
else;
	mkdir $DID_DIR
fi

for x in $(ls $FOLDER | grep *.root);
	echo "Working on ${x}"
	mv "${x}/*.root" .
	mv $x $DID_DIR
done
