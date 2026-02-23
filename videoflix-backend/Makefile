.PHONY: help build up down restart logs shell migrate makemigrations test clean

help:
	@echo "Videoflix Backend - Available Commands:"
	@echo "  make build          - Build Docker containers"
	@echo "  make up             - Start Docker containers"
	@echo "  make down           - Stop Docker containers"
	@echo "  make restart        - Restart Docker containers"
	@echo "  make logs           - View container logs"
	@echo "  make shell          - Open Django shell"
	@echo "  make migrate        - Run database migrations"
	@echo "  make makemigrations - Create new migrations"
	@echo "  make test           - Run tests"
	@echo "  make clean          - Remove containers and volumes"

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

shell:
	docker-compose exec web python manage.py shell

migrate:
	docker-compose exec web python manage.py migrate

makemigrations:
	docker-compose exec web python manage.py makemigrations

test:
	docker-compose exec web python manage.py test

clean:
	docker-compose down -v
	docker system prune -f
