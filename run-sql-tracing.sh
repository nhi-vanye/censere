#! /bin/sh
#

uniq=$(date +%s)

echo ""
echo "Saving SQL Trace report to sql-trace-$uniq.txt ..."
echo ""

echo python3 -m apsw.trace  --reports=summary,popular,aggregate,individual  -- ${VIRTUAL_ENV}/mars-censere $* > sql-trace-$uniq.txt
echo "" >> sql-trace-$uniq.txt

python3 -m apsw.trace -o sql-trace-$uniq.tmp  --reports=summary,popular,aggregate,individual  -- ${VIRTUAL_ENV}/bin/mars-censere $*

cat sql-trace-$uniq.tmp >> sql-trace-$uniq.txt

rm -f sql-trace-$uniq.tmp

