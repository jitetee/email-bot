# Contributing to Email Bot v3.0

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## 🎯 Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what's best for the community

## 📋 How to Contribute

### 1. Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the behavior
- **Expected vs actual behavior**
- **Screenshots** if applicable
- **Environment details** (OS, Python version, etc.)

**Example:**
```markdown
**Bug**: Campaign fails with large email lists

**Steps to Reproduce:**
1. Add 1000+ emails to email_list.txt
2. Start bulk campaign
3. See error after 100 emails

**Expected:** Campaign completes successfully
**Actual:** Connection timeout error

**Environment:**
- OS: Ubuntu 20.04
- Python: 3.9.7
```

### 2. Suggesting Features

Feature suggestions are welcome! Please provide:

- **Use case** - Why is this feature needed?
- **Proposed solution** - How should it work?
- **Alternatives considered** - Other approaches you've thought about

### 3. Pull Requests

1. **Fork** the repository
2. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Test thoroughly**
5. **Commit** with clear messages:
   ```bash
   git commit -m "feat: add amazing feature"
   ```
6. **Push** to your branch:
   ```bash
   git push origin feature/amazing-feature
   ```
7. **Open a Pull Request**

## 📝 Development Guidelines

### Code Style

- Follow **PEP 8** for Python code
- Use **meaningful variable names**
- Add **docstrings** for functions and classes
- Keep functions **focused and small**

### Testing

Before submitting a PR:

- ✅ Test all affected features
- ✅ Ensure existing tests pass
- ✅ Add tests for new features
- ✅ Update documentation if needed

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting)
- `refactor:` - Code refactoring
- `test:` - Test additions/changes
- `chore:` - Build process or auxiliary tool changes

**Examples:**
```bash
feat: add email scheduling feature
fix: resolve connection timeout issue
docs: update installation instructions
refactor: simplify email validation logic
```

## 🚀 Setting Up Development Environment

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/email-bot.git
cd email-bot
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
nano .env  # Add your credentials
```

## 📂 Project Structure

```
email-bot/
├── email-bot.sh              # Main CLI script
├── install.sh                # Installation script
├── requirements.txt          # Dependencies
├── config.py                 # Configuration
├── email_sender.py           # Core email sending
├── templates/                # Email templates
├── data/                     # Data files
└── logs/                     # Logs
```

## 🔍 Areas for Contribution

### High Priority

- [ ] Email template designs
- [ ] Documentation improvements
- [ ] Bug fixes
- [ ] Performance optimizations
- [ ] Additional SMTP providers support

### Nice to Have

- [ ] More email templates
- [ ] Additional analytics features
- [ ] Integration with more services
- [ ] Translations to other languages
- [ ] Tutorial videos

## ❓ Questions?

Feel free to open an issue for any questions or discussions.

## 🙏 Thank You!

Your contributions make this project better for everyone. We appreciate your time and effort!

---

<div align="center">

**Made with ❤️ by the Email Bot Community**

</div>
