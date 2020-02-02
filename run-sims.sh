#! /bin/sh
#
#
# Run some sample simulations with a variety of parameters to get
# a feel for how the parameters may affect the results.
#

prefix=$(date +"%Y%m%d%H%M")

image="registry.gitlab.com/mars-society-uk/science/mars-censere/mars-censere"

echo "" > run-sims.log

for s in $(jot -r 10 0 999999)
do

    # While having settlers where half are under 25years (half:20,5),
    # the average age of the US Marines is 25
    for a in  "randrange:32,46" "randrange:28,42" "triangle:28,34,42" "triangle:28,32,38" "triangle:22,30,34" "half:25,5" "half:20,5"
    do

        for r in 0.25 0.75 0.90 0.95
        do

        for g in 3 4 5 6
        do
            c=$(docker run -it -d -v /home/core/data:/data  $image  \
            --fraction-relationships-having-children=$r\
            --common-ancestor=$g\
            --limit=sols\
            --limit-count=66800\
            --settlers-per-initial-ship=randint:160,160\
            --ships-per-mission=randint:0,0\
            --first-child-delay=randint:300,600\
            --sols-between-siblings=triangle:300,500,800\
            --random-seed=$s\
            --database=/data/$prefix-160-0-$s-$r-$a-gen-$g.db\
            --astronaut-age-range=$a\
            --notes="$a; relfrac:$r gen:$g")

            echo "$c $prefix-160-0-$s-$r-$a" >> run-sims.log
        done	
        done
    done
done

while read -r container_id desc
do

    echo "Waiting for $container_id to exit"
    docker wait $container_id
    echo "Saving logs for $container_id to $desc.log"
    docker logs $container_id > $desc.log

    echo "Removing $container_id"
    docker rm $container_id

done < run-sims.log

