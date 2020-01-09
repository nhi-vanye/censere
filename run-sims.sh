#! /bin/sh

for i in $(seq 10)
do

	s=$(random 0 999999)

	for a in  "randrange:32,46" "randrange:28,42" "triangle:28,34,42" "triangle:28,32,38" "triangle:22,30,34" "half:25,5" "half:22,6"
	do

		docker run -it -d -v /home/core/data:/data  registry.gitlab.com/mars-society-uk/science/mars-censere/mars-censere  \
			--limit=sols\
			--limit-count=66800\
			--settlers-per-initial-ship=randint:160,160\
			--ships-per-mission=randint:0,0\
			--first-child-delay=randint:300,600\
			--sols-between-siblings=triangle:300,500,800\
			--random-seed=$s\
			--database=/data/$s-$a.db\
			--astronaut-age-range=$a
			--notes="$a" 
	done
done
