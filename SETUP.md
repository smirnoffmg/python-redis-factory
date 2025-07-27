# Setup Guide

This guide explains how to set up PyPI publishing and Codecov integration for the python-redis-factory project.

## PyPI Setup

### 1. Create PyPI Account

1. **Go to [PyPI](https://pypi.org/account/register/)**
2. **Create an account** if you don't have one
3. **Verify your email** address

### 2. Generate API Token

1. **Go to [PyPI Account Settings](https://pypi.org/manage/account/)**
2. **Click "Add API token"**
3. **Configure the token**:
   - **Token name**: `python-redis-factory-github-actions`
   - **Scope**: Select "Entire account (all projects)"
4. **Copy the token** (starts with `pypi-`)

### 3. Add Token to GitHub Secrets

1. **Go to your GitHub repository**: `https://github.com/smirnoffmg/python-redis-factory`
2. **Navigate to Settings → Secrets and variables → Actions**
3. **Click "New repository secret"**
4. **Add the secret**:
   - **Name**: `PYPI_API_TOKEN`
   - **Value**: Your PyPI API token (starts with `pypi-`)
5. **Click "Add secret"**

### 4. Test PyPI Publishing

After adding the token, you can test the release process:

```bash
# Bump version and create release
make release-patch
```

This will:
1. Bump the version (e.g., 0.1.0 → 0.1.1)
2. Create a git tag (e.g., v0.1.1)
3. Push to GitHub
4. Trigger GitHub Actions
5. Publish to PyPI automatically

## Codecov Setup

### 1. Connect Repository to Codecov

1. **Go to [Codecov](https://codecov.io/)**
2. **Sign in with GitHub**
3. **Add your repository**: `smirnoffmg/python-redis-factory`
4. **Copy the Codecov token** (if provided)

### 2. Add Codecov Token (if needed)

If Codecov provides a token:

1. **Go to GitHub repository settings**
2. **Navigate to Settings → Secrets and variables → Actions**
3. **Click "New repository secret"**
4. **Add the secret**:
   - **Name**: `CODECOV_TOKEN`
   - **Value**: Your Codecov token
5. **Click "Add secret"**

### 3. Verify Codecov Integration

After setting up:

1. **Run tests with coverage**:
   ```bash
   make test-coverage
   ```

2. **Check Codecov dashboard**: https://codecov.io/gh/smirnoffmg/python-redis-factory

3. **Verify coverage badges** in README.md

## Troubleshooting

### PyPI Issues

**Error: "Invalid API token"**
- Verify the token starts with `pypi-`
- Check that the token has "Entire account" scope
- Ensure the secret name is exactly `PYPI_API_TOKEN`

**Error: "Package already exists"**
- The workflow uses `skip-existing: true`, so this should be handled automatically
- Check if the version number is correct

**Error: "Authentication failed"**
- Verify the token is correctly added to GitHub secrets
- Check that the token hasn't expired

### Codecov Issues

**Error: "No coverage data found"**
- Ensure tests are running with coverage: `uv run pytest --cov=python_redis_factory --cov-report=xml`
- Check that `coverage.xml` is being generated

**Error: "Repository not found"**
- Verify the repository is connected to Codecov
- Check the repository name in Codecov settings

## Verification

### After Setup

1. **Test PyPI publishing**:
   ```bash
   make release-patch
   ```

2. **Check PyPI**: https://pypi.org/project/python-redis-factory/

3. **Check Codecov**: https://codecov.io/gh/smirnoffmg/python-redis-factory

4. **Verify badges** in README.md are working

### Manual Testing

```bash
# Test package installation
pip install python-redis-factory

# Test coverage locally
make test-coverage

# Test build
make build
```

## Security Notes

- **Never commit API tokens** to version control
- **Rotate tokens regularly** (every 6-12 months)
- **Use different tokens** for different environments
- **Monitor token usage** in PyPI and Codecov dashboards 