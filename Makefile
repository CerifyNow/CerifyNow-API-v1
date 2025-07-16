.PHONY: install migrate seed test run docker-build docker-up docker-down clean setup

# Python and Django commands
install:
	pip install --upgrade pip
	pip install -r requirements.txt

migrate:
	python manage.py makemigrations
	python manage.py migrate

superuser:
	python manage.py create_admin --email=admin@certifynow.uz --password=admin123

seed:
	python manage.py generate_certificates --count=50

test:
	python manage.py test --verbosity=2

run:
	python manage.py runserver 0.0.0.0:8000

collectstatic:
	python manage.py collectstatic --noinput --clear

shell:
	python manage.py shell_plus

# Docker commands
docker-build:
	docker-compose build --no-cache

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down -v

docker-logs:
	docker-compose logs -f

docker-restart:
	docker-compose restart

docker-clean:
	docker-compose down -v --rmi all --remove-orphans
	docker system prune -f

# Development setup
setup: install migrate superuser seed
	@echo "✅ Development environment setup complete!"
	@echo "🚀 Run 'make run' to start the server"
	@echo "📚 API docs: http://localhost:8000/api/docs/"
	@echo "👤 Admin: admin@certifynow.uz / admin123"

# Production setup
prod-setup: install collectstatic migrate
	@echo "✅ Production environment setup complete!"

# Database operations
db-reset:
	python manage.py flush --noinput
	python manage.py migrate
	python manage.py create_admin --email=admin@certifynow.uz --password=admin123

db-backup:
	python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission > backup.json

db-restore:
	python manage.py loaddata backup.json

# Code quality
lint:
	flake8 .
	black --check .
	isort --check-only .

format:
	black .
	isort .

# Testing
test-coverage:
	coverage run --source='.' manage.py test
	coverage report
	coverage html

# Clean up
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name "*.log" -delete

# API documentation
docs:
	python manage.py spectacular --color --file schema.yml
	@echo "📄 API schema generated at schema.yml"

# Security check
security:
	python manage.py check --deploy
	safety check

# Performance monitoring
monitor:
	python manage.py runserver_plus --print-sql

# Celery commands
celery-worker:
	celery -A certifynow worker -l info

celery-beat:
	celery -A certifynow beat -l info

celery-flower:
	celery -A certifynow flower

# Help
help:
	@echo "Available commands:"
	@echo "  setup          - Complete development setup"
	@echo "  run            - Run development server"
	@echo "  test           - Run tests"
	@echo "  docker-up      - Start with Docker"
	@echo "  clean          - Clean temporary files"
	@echo "  docs           - Generate API documentation"
	@echo "  help           - Show this help"
