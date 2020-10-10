# Helper to upload latest configuration to S3 for local testing.
upload-config:
	aws s3 cp config.yaml s3://movie-vote-bot-bucket/config.yaml


# Create a virtual environment ready for use.
install:
	(\
	python3 -m venv env; \
	source env/bin/activate; \
	pip install -r requirements.txt; \
	)

# Install/upgrade black for formatting Python code
get-format:
	env/bin/pip install -U black

# Run black to format code
format: get-format
	env/bin/black *.py
