# Contributing to RakshaNet

First off, thank you for considering contributing to RakshaNet! It's people like you that make RakshaNet a great tool for disaster management and crisis response.

## Code of Conduct

By participating in this project, you are expected to uphold our Code of Conduct:
- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on what is best for the community
- Show empathy towards other community members

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples** (code snippets, screenshots)
- **Describe the behavior you observed** and what you expected
- **Include your environment details** (OS, Python version, Django version)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear and descriptive title**
- **Provide a detailed description** of the suggested enhancement
- **Explain why this enhancement would be useful**
- **List any similar features** in other applications if applicable

### Pull Requests

1. **Fork the repository** and create your branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following our coding standards:
   - Follow PEP 8 style guide for Python code
   - Add comments for complex logic
   - Update documentation if needed
   - Write descriptive commit messages

3. **Test your changes**:
   ```bash
   python manage.py test
   ```

4. **Ensure your code follows Django best practices**:
   - Use Django ORM properly
   - Follow the DRY principle
   - Implement proper error handling
   - Use Django's built-in security features

5. **Update documentation**:
   - Update README.md if you changed functionality
   - Add docstrings to new functions/classes
   - Update relevant documentation in `docs/` folder

6. **Commit your changes**:
   ```bash
   git commit -m "Add: Brief description of your changes"
   ```
   Use prefixes: `Add:`, `Fix:`, `Update:`, `Remove:`, `Refactor:`

7. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Open a Pull Request** with:
   - Clear title describing the change
   - Detailed description of what changed and why
   - Link to any related issues
   - Screenshots if UI changes are involved

## Development Setup

1. Clone your fork:
   ```bash
   git clone https://github.com/your-username/RakshaNet.git
   cd RakshaNet
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   cd RakshaNet
   pip install -r requirements.txt
   ```

4. Setup database:
   ```bash
   python manage.py migrate
   python manage.py populate_initial_data
   python manage.py createsuperuser
   ```

5. Run development server:
   ```bash
   python manage.py runserver
   ```

## Coding Standards

### Python/Django
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use meaningful variable and function names
- Maximum line length: 100 characters
- Use Django's class-based views when appropriate
- Implement proper model validation
- Use Django forms for data handling

### JavaScript
- Use ES6+ features
- Add comments for complex logic
- Keep functions small and focused
- Use meaningful variable names

### HTML/CSS
- Use semantic HTML5 elements
- Follow Bootstrap 4 conventions
- Keep templates modular and reusable
- Use Django template inheritance properly

### Git Commits
- Use clear, descriptive commit messages
- Prefix commits with type: `Add:`, `Fix:`, `Update:`, `Remove:`, `Refactor:`
- Reference issue numbers when applicable
- Keep commits focused on a single change

## Project Structure

```
RakshaNet/
├── raksha/           # Main crisis management app
│   ├── models.py    # Database models
│   ├── views.py     # General views
│   ├── role_views.py # Role-specific dashboards
│   ├── utils.py     # Utility functions (AI features)
│   ├── forms.py     # Form definitions
│   └── templates/   # HTML templates
├── users/           # User authentication
├── blog/            # Blog functionality
└── django_start/    # Project settings
```

## Areas for Contribution

### High Priority
- [ ] Enhanced AI features for better crisis prediction
- [ ] Mobile app integration
- [ ] Real-time notifications system
- [ ] Advanced analytics dashboard
- [ ] Multi-tenancy support

### Good First Issues
- Documentation improvements
- UI/UX enhancements
- Additional language translations
- Test coverage improvements
- Bug fixes

### Feature Requests
- SMS/WhatsApp integration
- Weather API integration for disaster prediction
- Resource tracking with QR codes
- Mobile-responsive improvements
- Accessibility enhancements

## Testing

- Write tests for new features
- Ensure existing tests pass
- Aim for high test coverage
- Test both success and failure scenarios

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test raksha

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## Documentation

- Document all public functions and classes
- Update README.md for major changes
- Add examples for complex features
- Keep documentation up-to-date

## Questions?

Feel free to:
- Open an issue for discussion
- Join our community discussions
- Reach out to maintainers

## Recognition

Contributors will be recognized in:
- Project README
- Release notes
- Special mentions for significant contributions

Thank you for contributing to RakshaNet! 🛡️
