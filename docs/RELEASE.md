# Release Guide

This document explains how to release new versions of `python-redis-factory` to PyPI. The project uses a **manual release workflow** from the main branch.

## Quick Release Commands

```bash
# Show current version
make version

# Release commands (bump version + create tag + trigger deployment)
make release-patch  # 0.1.0 -> 0.1.1 (bug fixes)
make release-minor  # 0.1.0 -> 0.2.0 (new features)
make release-major  # 0.1.0 -> 1.0.0 (breaking changes)
```

## Release Workflow

### Manual Release via GitHub Actions (Recommended)

The project uses GitHub Actions for manual releases. This provides full control over when and how releases are made:

1. **Go to GitHub Actions** in your repository
2. **Select the "Release" workflow**
3. **Click "Run workflow"**
4. **Configure the release**:
   - **Version**: Enter the target version (e.g., `0.2.0`) or leave as `0.1.0` to auto-bump
   - **Release type**: Choose `patch`, `minor`, or `major` (used when version is `0.1.0`)
5. **Click "Run workflow"**

The workflow will:
- ✅ Run quality checks (tests, linting, type checking)
- ✅ Bump version automatically
- ✅ Create git tag
- ✅ Build package
- ✅ Publish to PyPI
- ✅ Create GitHub release

**Note**: If you enter a specific version (not `0.1.0`), it will set that exact version. If you leave it as `0.1.0`, it will bump the current version based on the release type.

### Manual Release (Local)

For complete manual control:

```bash
# 1. Run quality checks
make ci

# 2. Bump version manually
python scripts/version.py bump minor  # or patch, major

# 3. Create tag and push
python scripts/version.py tag

# 4. Build package
make build

# 5. Upload to PyPI (if needed)
uv run pip install twine
uv run twine upload dist/*
```

## Version Management

### Current Version Location

The version is managed in a single location:
- **Source**: `src/python_redis_factory/__init__.py` (line 17)
- **Current version**: `0.1.0`

### Version Commands

```bash
# Show current version
python scripts/version.py current
# or
make version

# Show version only (for scripts)
python scripts/version.py current --version-only

# Bump version types
python scripts/version.py bump patch    # 0.1.0 -> 0.1.1
python scripts/version.py bump minor    # 0.1.0 -> 0.2.0  
python scripts/version.py bump major    # 0.1.0 -> 1.0.0
python scripts/version.py bump prerelease  # 0.1.0 -> 0.1.0-alpha.1

# Set specific version
python scripts/version.py set 0.2.0

# Create git tag for current version
python scripts/version.py tag
```

### Semantic Versioning

Follow [Semantic Versioning](https://semver.org/) (MAJOR.MINOR.PATCH):

- **Patch** (0.1.0 → 0.1.1): Bug fixes, documentation updates
- **Minor** (0.1.0 → 0.2.0): New features, backward compatible
- **Major** (0.1.0 → 1.0.0): Breaking changes

## Pre-Release Checklist

Before making a release, ensure:

- [ ] **All tests pass**: `make test-parallel`
- [ ] **Linting passes**: `make lint`
- [ ] **Type checking passes**: `make type-check`
- [ ] **Documentation is updated**: README.md, docstrings
- [ ] **Changelog is updated** (if applicable)
- [ ] **No breaking changes** (unless intentional major release)

## Release Process Step-by-Step

### Step 1: Prepare for Release

```bash
# Ensure you're on main branch
git checkout main
git pull origin main

# Run full quality checks
make ci
```

### Step 2: Trigger Manual Release

**Option A: GitHub Actions (Recommended)**
1. Go to GitHub Actions → Release workflow
2. Click "Run workflow"
3. Choose version and release type
4. Click "Run workflow"

**Option B: Local Commands**
```bash
# For bug fixes and minor updates
make release-patch

# For new features
make release-minor

# For breaking changes
make release-major
```

### Step 3: Verify Release

After the release process completes:

1. **Check PyPI**: https://pypi.org/project/python-redis-factory/
2. **Test installation**:
   ```bash
   pip install python-redis-factory==<new-version>
   ```
3. **Check GitHub release**: https://github.com/smirnoffmg/python-redis-factory/releases
4. **Verify package works**:
   ```python
   from python_redis_factory import get_redis_client
   # Test basic functionality
   ```

## GitHub Actions Workflow

The `.github/workflows/release.yml` workflow:

1. **Triggers on**: Manual workflow dispatch only
2. **Runs on**: Ubuntu latest
3. **Steps**:
   - Setup Python 3.12 and uv
   - Install dependencies
   - Run tests with coverage
   - Upload coverage to Codecov
   - Run linting and type checking
   - Build package
   - Bump version and create tag
   - Publish to PyPI
   - Create GitHub release

## PyPI Publishing

### Production PyPI
- **URL**: https://pypi.org/project/python-redis-factory/
- **Authentication**: GitHub Actions uses `PYPI_API_TOKEN` secret
- **Workflow**: Automatic via GitHub Actions

### Package Information
- **Package name**: `python-redis-factory`
- **Build system**: `hatchling`
- **Python versions**: 3.12+
- **Dependencies**: `redis>=6.2.0`

## Troubleshooting

### Common Issues

**1. Build fails**
```bash
# Check GitHub Actions logs
# Common causes: test failures, linting errors, type issues
```

**2. PyPI upload fails**
- Verify `PYPI_API_TOKEN` secret is set in GitHub repository
- Check token has proper permissions (upload to PyPI)
- Ensure package name is available

**3. Version already exists**
- The workflow uses `skip-existing: true` to handle this
- For manual uploads, use `--skip-existing` flag

**4. Tag already exists**
```bash
# The version script will warn you
python scripts/version.py tag
# Error: Tag v0.1.0 already exists
```

**5. Git identity error in CI**
```
Author identity unknown
*** Please tell me who you are.
```
- **Solution**: The workflow now configures git identity automatically
- **If it still fails**: Check that the workflow has `contents: write` permissions

**6. Tests fail locally but pass in CI**
```bash
# Ensure you're using the same Python version
python --version  # Should be 3.12+
# Check uv.lock is up to date
uv sync
```

### Manual Recovery

If automated release fails:

```bash
# 1. Check what went wrong in GitHub Actions
# 2. Fix the issue
# 3. Push the fix to main
# 4. Or trigger manual workflow dispatch

# For emergency manual release:
make ci
python scripts/version.py bump patch
python scripts/version.py tag
make build
uv run twine upload dist/*
```

## Security Considerations

- **API tokens**: Stored as GitHub repository secrets
- **Token rotation**: Rotate PyPI tokens regularly
- **Branch protection**: Main branch is protected
- **Required reviews**: PRs require approval before merge

## Best Practices

1. **Always run tests** before releasing
2. **Use semantic versioning** consistently
3. **Update documentation** with new features
4. **Test the released package** after publication
5. **Monitor PyPI download statistics**
6. **Keep dependencies updated**

## Support

- **Issues**: Create GitHub issues for bugs and feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Contributing**: See CONTRIBUTING.md for development guidelines 