

# create temp dir for the migration files
# that have the variable subsitution applied to them
FLYWAYMIGRATION_FILES_DIR=../../server/flyway/sql
TMP_FLYWAY_DIR=junk
FAM_USER=fam
FAM_PASSWORD=fam

rm -rf junk

if [ ! -d junk ]
then
    echo 'making junk dir';
    mkdir junk;
fi
for FILE in $FLYWAYMIGRATION_FILES_DIR/*;
    do
        echo $FILE;
        justFile=$( basename $FILE )
        file2Create=$TMP_FLYWAY_DIR/$justFile
        echo "$file2Create"

        echo '------------'
        cat $FILE | sed 's/${api_db_username}/'"$FAM_USER"'/g' | \
            sed 's/${api_db_password}/'"$FAM_PASSWORD"'/g' > $file2Create
    done

flyway -user=$POSTGRES_USER \
    -password=$POSTGRES_PASSWORD \
    -url=jdbc:postgresql://localhost:5432/postgres \
    -locations=filesystem:$TMP_FLYWAY_DIR \
    migrate

rm -rf junk


