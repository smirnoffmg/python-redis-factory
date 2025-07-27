# Release Guide

This document explains how to release new versions of `python-redis-factory` to PyPI using automatic semantic versioning.

## Release Workflow

### Automatic Releases (Recommended)

1. **Bump version using the version script**
   ```bash
   # For patch release (bug fixes)
   python scripts/version.py bump patch
   
   # For minor release (new features, backward compatible)
   python scripts/version.py bump minor
   
   # For major release (breaking changes)
   python scripts/version.py bump major
   ```

2. **Update CHANGELOG.md**
   - Add new version section
   - Document changes, features, and bug fixes

3. **Create and push tag (automated)**
   ```bash
   python scripts/version.py tag
   ```
   
   This command will:
   - Commit the version change
   - Create a git tag
   - Push to main branch
   - Push the tag

4. **GitHub Actions will automatically:**
   - Run all tests
   - Run linting and type checking
   - Build the package
   - Publish to PyPI
   - Create a GitHub release with assets

### Manual Releases

If you need to trigger a release manually:

1. **Go to GitHub Actions**
2. **Select the "Release" workflow**
3. **Click "Run workflow"**
4. **Enter the version tag** (e.g., `v0.1.1`)
5. **Click "Run workflow"**

### Version Management Commands

```bash
# Show current version
python scripts/version.py current

# Bump version
python scripts/version.py bump patch    # 0.1.0 -> 0.1.1
python scripts/version.py bump minor    # 0.1.0 -> 0.2.0
python scripts/version.py bump major    # 0.1.0 -> 1.0.0

# Set specific version
python scripts/version.py set 1.2.3

# Create and push tag (commits version change and creates tag)
python scripts/version.py tag
```

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR.MINOR.PATCH** (e.g., `1.0.0`)
- **Patch**: Bug fixes (0.1.0 → 0.1.1)
- **Minor**: New features, backward compatible (0.1.0 → 0.2.0)
- **Major**: Breaking changes (0.1.0 → 1.0.0)

## PyPI Publishing

### Production PyPI
- **Trigger**: Tags matching `v*` (e.g., `v0.1.0`, `v1.0.0`)
- **Repository**: https://pypi.org/project/python-redis-factory/
- **Workflow**: `.github/workflows/release.yml`

## Verification

After a release:

1. **Check PyPI**: https://pypi.org/project/python-redis-factory/
2. **Test installation**:
   ```bash
   pip install python-redis-factory==0.1.1
   ```
3. **Check GitHub release**: https://github.com/smirnoffmg/python-redis-factory/releases

## Troubleshooting

### Common Issues

1. **Build fails**: Check GitHub Actions logs for test/lint failures
2. **PyPI upload fails**: Verify API token is correct and has proper permissions
3. **Version already exists**: Use `skip-existing: true` in workflow (already configured)
4. **Tag already exists**: The version script will warn you if the tag already exists

### Manual PyPI Upload (if needed)

```bash
# Build package
uv build

# Upload to Production PyPI
uv run twine upload dist/*
```

## Security

- API tokens are stored as GitHub repository secrets
- Use different tokens for different environments
- Rotate tokens regularly 