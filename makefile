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