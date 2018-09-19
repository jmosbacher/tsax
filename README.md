# Time series dashboards for Xenon


## Requirements
 - Docker
 - Docker-compose

## Whip up a server
 - git clone this repo
 - cd to tsax
 - make sure the grafana/data folder is owned by 472 (sudo chown 472:472 ./grafana/data)
 - Set environment variabes with your credentials:
    - export SCUSER='slow control user'
    - export SCPASS='slow control pass'
    - export MONGOPASS='mongodb pass'
 - run the docker images with: 'docker-compose up'
 - Go to http://localhost:3000
 
## Notes
 - You may need to run docker with sudo if you havent added your user to the docker group
 