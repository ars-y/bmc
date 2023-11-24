define find.functions
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'
endef

help: ## display available commands
	@echo 'The following commands can be used.'
	@echo ''
	$(call find.functions)

setup: ## docker build + up > alembic migrate > create superuser
setup: up migrate csu

up: ## docker compose up
up:
	sudo docker compose up -d --build

migrate:
migrate:
	sudo docker compose exec web_app alembic upgrade head

csu: ## create superuser
csu:
	sudo docker compose exec web_app python __createsuperuser__.py

down: ## docker compose down
down:
	sudo docker compose down -v


clean: ## clean pycache
clean:
	find . | grep -E "(__pycache__|\.pyc|\.pyo$\)" | xargs rm -rf
