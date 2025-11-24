.PHONY: run-dev

run-dev:
	docker compose -f ./docker-compose.dev.yaml down -v
	docker compose -f ./docker-compose.dev.yaml up --build -d
