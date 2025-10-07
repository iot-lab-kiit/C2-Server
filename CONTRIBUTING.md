# Contributing to C2 Server Project

Thank you for your interest in contributing to the C2 Server project! This document provides detailed guidelines for contributors.

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Git installed on your system
- Basic understanding of socket programming and networking concepts

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/c2-server.git
   cd c2-server
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install black flake8 pytest  # Development tools
   ```

4. **Test the Setup**
   ```bash
   python c2_server.py  # Test server
   python c2_agent.py   # Test agent (in another terminal)
   ```

## 🌿 Branch Naming Convention

- **Feature**: `feature/description-of-feature`
- **Bug Fix**: `bugfix/issue-number-description`
- **Documentation**: `docs/description-of-changes`
- **Enhancement**: `enhancement/description-of-improvement`
- **Refactor**: `refactor/description-of-refactor`

## 📝 Commit Message Guidelines

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>: <description>

[optional body]

[optional footer(s)]
```

### Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples:
```
feat: add file encryption for secure transfers
fix: resolve connection timeout in multi-client mode
docs: update installation instructions
```

## 🔍 Code Style Guidelines

### Python Style
- Follow [PEP 8](https://pep8.org/) style guidelines
- Use meaningful variable and function names
- Add docstrings for all functions and classes
- Maximum line length: 88 characters
- Use type hints where appropriate

### Code Formatting
```bash
# Format code with black
black .

# Check style with flake8
flake8 .
```

### Example Code Style:
```python
def upload_file(self, src_path: str, dst_path: str) -> bool:
    """
    Upload a file to the connected client.
    
    Args:
        src_path (str): Local source file path
        dst_path (str): Remote destination file path
        
    Returns:
        bool: True if upload successful, False otherwise
    """
    try:
        # Implementation here
        return True
    except Exception as e:
        self.logger.error(f"Upload failed: {e}")
        return False
```

## 🧪 Testing Guidelines

### Writing Tests
- Write tests for new features
- Ensure existing tests pass
- Include both positive and negative test cases
- Mock network connections for unit tests

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_server.py
```

## 📚 Documentation Standards

### Code Documentation
- All public functions must have docstrings
- Include type hints
- Document complex algorithms
- Add inline comments for non-obvious code

### README Updates
- Update feature lists when adding new functionality
- Include usage examples for new features
- Update installation instructions if needed

## 🔒 Security Considerations

### Security Guidelines
- Never commit sensitive information (API keys, passwords)
- Use secure coding practices
- Validate all user inputs
- Implement proper error handling
- Follow principle of least privilege

### Security Review Process
- All security-related changes require thorough review
- Consider potential attack vectors
- Test with various input scenarios
- Document security implications

## 🎯 Areas for Contribution

### High Priority
- **Authentication System**: Implement secure client authentication
- **Encryption**: Add end-to-end encryption for all communications
- **Logging**: Comprehensive logging system with different levels
- **Configuration**: YAML/JSON configuration file support

### Medium Priority
- **GUI Improvements**: Enhanced user interface with better UX
- **Cross-platform**: Better support for different operating systems
- **Performance**: Optimize file transfers and connection handling
- **Error Handling**: More robust error handling and recovery

### Good First Issues
- **Documentation**: Improve code comments and documentation
- **Code Cleanup**: Refactor repetitive code into functions
- **Input Validation**: Add better input validation and sanitization
- **Unit Tests**: Write tests for existing functionality

## 🎃 Hacktoberfest Guidelines

### Valid Contributions
- ✅ Bug fixes with proper testing
- ✅ New features that add value
- ✅ Performance improvements
- ✅ Security enhancements
- ✅ Documentation improvements
- ✅ Code refactoring for better maintainability

### Invalid Contributions
- ❌ Trivial changes (typos, whitespace)
- ❌ Generated content without review
- ❌ Duplicate pull requests
- ❌ Changes that break existing functionality

### Quality Standards
- All PRs must pass CI checks
- Include clear description of changes
- Reference related issues
- Add tests for new functionality
- Update documentation as needed

## 🔄 Pull Request Process

### Before Submitting
1. Ensure your code follows the style guidelines
2. Run tests and ensure they pass
3. Update documentation if necessary
4. Rebase your branch on the latest main

### PR Description Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring
- [ ] Performance improvement

## Testing
- [ ] Tests pass locally
- [ ] Added new tests for functionality
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes
```

### Review Process
1. Automated checks (style, tests)
2. Maintainer review
3. Community feedback (if applicable)
4. Final approval and merge

## 🤝 Community Guidelines

### Communication
- Be respectful and constructive
- Ask questions if unclear about requirements
- Provide helpful feedback on others' contributions
- Use GitHub Discussions for general questions

### Getting Help
- Check existing issues and documentation first
- Use GitHub Issues for bug reports
- Use GitHub Discussions for questions
- Tag maintainers for urgent security issues

## 📋 Issue Templates

When creating issues, please use these templates:

### Bug Report
```markdown
**Bug Description**
Clear description of the bug

**Steps to Reproduce**
1. Step one
2. Step two
3. See error

**Expected Behavior**
What should happen

**Environment**
- OS: [e.g., Windows 10]
- Python version: [e.g., 3.9]
- Project version: [e.g., v1.0]
```

### Feature Request
```markdown
**Feature Description**
Clear description of the feature

**Use Case**
Why is this feature needed?

**Proposed Solution**
How should this be implemented?

**Alternatives**
Other approaches considered
```

## 🏆 Recognition

Contributors will be recognized in:
- Repository README
- Release notes
- GitHub contributors page
- Special mentions for significant contributions

Thank you for contributing to the C2 Server project! 🚀