run-dev:
	uvicorn main:app --reload

build:
	docker build -t fluxovia-api .

run-api:
	docker run -p 8000:8000 fluxovia-api

run-compose:
	docker compose up
