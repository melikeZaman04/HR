.PHONY: start stop

start:
	docker compose up --build -d
	@echo "Waiting for db to be healthy..."
	@until [ "$$$$(docker inspect -f '{{.State.Health.Status}}' ai_decision_db 2>/dev/null)" = "healthy" ]; do sleep 2; done
	docker compose exec app alembic upgrade head
	@echo "API docs: http://localhost:8000/docs"

stop:
	docker compose down
