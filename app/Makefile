#
# This Makefile contains commands which are run inside the Docker containers,
# I do not recommend invoking these directly - see Makefile at project root instead.
#
# Allows us to run several commands in one bash shelll
.ONESHELL:

worker-local:
	./scripts/worker/local.sh

worker-prod:
	./scripts/worker/prod.sh

web-local:
	./scripts/web/local.sh

web-prod:
	./scripts/web/prod.sh

lint:
	./scripts/tasks/lint.sh

format:
	./scripts/tasks/format.sh

test:
	./scripts/tasks/test.sh

