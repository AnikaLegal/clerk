#
# This Makefile contains commands which are run inside the Docker containers,
# I do not recommend invoking these directly - see Makefile at project root instead.
#
reports-local:
	bash ./scripts/reports/local.sh

reports-prod:
	bash ./scripts/reports/prod.sh

worker-local:
	bash ./scripts/worker/local.sh

worker-prod:
	bash ./scripts/worker/prod.sh

web-local:
	bash ./scripts/web/local.sh

web-prod:
	bash ./scripts/web/prod.sh

lint:
	bash ./scripts/tasks/lint.sh

format:
	bash ./scripts/tasks/format.sh

test:
	bash ./scripts/tasks/test.sh

shell:
	bash ./scripts/tasks/shell.sh
