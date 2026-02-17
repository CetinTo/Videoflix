# Contributing to Videoflix

Thank you for considering contributing to Videoflix!

## Development Setup

1. Fork the repository
2. Clone your fork
3. Create a new branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Run tests
6. Commit your changes
7. Push to your fork
8. Create a Pull Request

## Code Style

- Follow PEP 8 for Python code
- Use meaningful variable names
- Add docstrings to all functions and classes
- Keep functions small and focused

## Commit Messages

Follow conventional commits format:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `chore:` - Maintenance tasks

## Testing

Run tests before submitting PR:

```bash
docker-compose exec web python manage.py test
```

## Pull Request Process

1. Update README.md if needed
2. Update API documentation if API changes
3. Ensure all tests pass
4. Request review from maintainers

## Questions?

Open an issue for questions or discussions.
