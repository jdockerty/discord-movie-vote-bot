ECR_LOGIN = aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin 268906218954.dkr.ecr.eu-west-2.amazonaws.com

# Helper to upload latest configuration to S3 for local testing.
upload:
	aws s3 cp config.yaml s3://movie-vote-bot-bucket/config.yaml


# Create a virtual environment ready for use.
install:
	(\
	python3 -m venv env; \
	source env/bin/activate; \
	pip install -r requirements.txt; \
	)

docker-prod:
	${ECR_LOGIN}
	docker build -t discord-movie-bot:prod-latest --build-arg environment=production -f .docker/bot.yml .
	docker tag discord-movie-bot:prod-latest 268906218954.dkr.ecr.eu-west-2.amazonaws.com/discord-movie-bot:prod-latest
	docker push 268906218954.dkr.ecr.eu-west-2.amazonaws.com/discord-movie-bot:prod-latest

docker-testing:
	${ECR_LOGIN}
	docker build -t discord-movie-bot:testing-latest --build-arg environment=testing -f .docker/bot.yml .
	docker tag discord-movie-bot:testing-latest 268906218954.dkr.ecr.eu-west-2.amazonaws.com/discord-movie-bot:testing-latest
	docker push 268906218954.dkr.ecr.eu-west-2.amazonaws.com/discord-movie-bot:testing-latest

# Install/upgrade formatting tools for Python code.
get-format:
	env/bin/pip install -U black
	env/bin/pip install -U isort
	env/bin/pip install -U autoflake

# Run formatting tools.
format: get-format
	env/bin/black *.py
	env/bin/isort *.py
	env/bin/autoflake --remove-unused-variables --in-place *.py