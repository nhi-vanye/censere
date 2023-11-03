#! /bin/sh
#
#
# Run some sample simulations with a variety of parameters to get
# a feel for how the parameters may affect the results.
#

prefix=$(date +"%Y%m%d%H%M")

image="${1:-mars-censere:latest}"

echo "" > run-sims.log

    # While having settlers where half are under 25years (half:20,5),
    # the average age of the US Marines is 25
    for a in  "randrange:32,46" "randrange:28,42" "triangle:28,34,42" "triangle:28,32,38" "triangle:22,30,34" "half:25,5" "half:20,5"
    do

        for r in 0.25 0.75 0.90 0.95
        do

            c=$(docker run -it -d -v $(pwd)/sims:/data --name $prefix-$r-$a $image generator \
            --fraction-relationships-having-children=$r \
            --database-dir=/data/ \
            --astronaut-age-range=$a \
            --parameters=/data/single-ship.params
            )

            sleep 5

            echo "$c $prefix-$r-$a" >> run-sims.log
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

