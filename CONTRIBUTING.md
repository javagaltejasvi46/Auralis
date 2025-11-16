# Contributing to AURALIS

Thank you for your interest in contributing to AURALIS! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Respect differing viewpoints and experiences

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in Issues
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, Python version, etc.)
   - Error logs/screenshots

### Suggesting Features

1. Check if the feature has been suggested
2. Create a new issue with:
   - Clear description of the feature
   - Use cases and benefits
   - Possible implementation approach

### Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/auralis.git
   cd auralis
   ```

2. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the code style guidelines
   - Add tests if applicable
   - Update documentation

4. **Test your changes**
   ```bash
   # Backend tests
   cd backend
   pytest

   # Frontend tests
   cd frontend
   npm test
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   ```

   Use conventional commits:
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation changes
   - `style:` - Code style changes
   - `refactor:` - Code refactoring
   - `test:` - Test changes
   - `chore:` - Build/tooling changes

6. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a Pull Request on GitHub

## Development Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
pip install -r requirements.txt
pip install -r requirements_whisper.txt
pip install -e ".[dev]"  # Install dev dependencies
```

### Frontend

```bash
cd frontend
npm install
```

## Code Style

### Python (Backend)

- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use Black for formatting:
  ```bash
  black backend/
  ```
- Use flake8 for linting:
  ```bash
  flake8 backend/
  ```

### TypeScript (Frontend)

- Follow Airbnb style guide
- Use ESLint and Prettier
- Maximum line length: 100 characters
- Format with Prettier:
  ```bash
  npm run format
  ```

## Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v
pytest tests/ --cov=. --cov-report=html
```

### Frontend Tests

```bash
cd frontend
npm test
npm run test:coverage
```

## Documentation

- Update README.md for major changes
- Add docstrings to Python functions
- Add JSDoc comments to TypeScript functions
- Update INSTALL.md for setup changes
- Update API documentation for endpoint changes

## Project Structure

```
Auralis/
├── backend/
│   ├── main.py              # FastAPI HTTP server
│   ├── transcription_server.py  # WebSocket server
│   ├── models.py            # Database models
│   ├── config.py            # Configuration
│   ├── audio_processor.py   # Audio utilities
│   └── tests/               # Backend tests
├── frontend/
│   ├── App.tsx              # Main app component
│   ├── components/          # React components
│   └── __tests__/           # Frontend tests
├── docs/                    # Additional documentation
└── docker/                  # Docker configurations
```

## Adding New Features

### Adding a New Language

1. Update `LANGUAGE_MAP` in `transcription_server.py`
2. Add language button in `frontend/App.tsx`
3. Test transcription accuracy
4. Update documentation

### Adding a New Translation Language

1. Update translation options in `frontend/App.tsx`
2. Test with deep-translator
3. Update UI to show new language

### Improving Transcription

1. Experiment with different Whisper models
2. Adjust beam_size and other parameters
3. Add preprocessing/postprocessing steps
4. Benchmark accuracy improvements

## Performance Optimization

- Profile code before optimizing
- Use caching where appropriate
- Optimize database queries
- Minimize bundle size (frontend)
- Use lazy loading

## Security

- Never commit sensitive data
- Use environment variables for secrets
- Validate all user inputs
- Sanitize file uploads
- Keep dependencies updated

## Release Process

1. Update version in `setup.py` and `package.json`
2. Update CHANGELOG.md
3. Create release branch
4. Run full test suite
5. Build Docker images
6. Tag release
7. Create GitHub release
8. Deploy to production

## Getting Help

- Check existing documentation
- Search closed issues
- Ask in Discussions
- Join our community chat

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

Thank you for contributing to AURALIS! 🎉
