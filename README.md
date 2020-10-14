## Overview

Simple Discord bot for counting the number of votes in a given list of movies for the movie night on Discord.

## Install

Dependencies can be installed into a virtual environment, with pip, using the commands

```
python3 -m venv <virtual_env_name>
pip install -r requirements.txt
```

or using the convenience provided in the `makefile` with 
    
    make install
    source env/bin/activate

## Usage

Requires an API key from Discord Developer Portal for usage inside of the `os.getenv['API_KEY']` and a channel ID for the appropriate channel messages are to be placed into, this is retrieved via `os.getenv['CHANNEL_ID']` as part of running the client.

Within the designated channel the commands are:

* `!newvote movie 1, movie 2, movie 3, ...` starts a new vote, only those with the role of 'Admin' can begin a vote.
* `!vote X Y Z` allows people to vote after a new vote has begun, the values correspond to the numerical value within list that is presented by the bot. Votes are weighted in order: the first vote is worth 3 points, the second is worth 2, and the last vote is worth 1.
* `!changevote X Y Z` someone can change their vote if it has already been cast, reusing `!vote` would stop them duplicating the vote.
* `!endvote` will end the vote casting and write the movie with the highest number of points into the channel.

## Deployment

**TODO: Update with some sort of blue/green etc.**

At present, this is deployed using AWS Fargate, executing a single service for the container. Logs are pushed into CloudWatch for simplicity.

## Testing

Using GitLab CI for testing, this is activated via repository mirroring to GitLab and using a `.gitlab-ci.yml` file.

The stages for this pipeline are:
* **test:** run the `bot_test.py` file which runs another tester bot account that sends various messages into an isolated test channel, verifying the responses from the movie bot. 
* **build-image:** this will build the latest image for the application, using the Dockerfile within `.docker/bot.yml`, and push it into AWS Elastic Container Registry (ECR). This occurs only on the master branch and uses the docker-in-docker service from GitLab.
