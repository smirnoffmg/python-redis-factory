# Release Guide

This document explains how to release new versions of `python-redis-factory` to PyPI using automatic semantic versioning with protected main branch workflow.

## Release Workflow

### Automatic Release Workflow

Since the `main` branch is protected, releases are created automatically from `main` after successful merge requests from `develop`:

1. **Develop on `develop` branch**
   ```bash
   git checkout develop
   git pull origin develop
   # Make your changes
   git add .
   git commit -m "feat: Add new feature"
   git push origin develop
   ```

2. **Create Merge Request**
   - Go to GitHub: `develop` → `main`
   - Ensure all CI checks pass
   - Get required approvals
   - Merge to `main`

3. **Automatic Release Process**
   - GitHub Actions automatically detects the merge
   - Version is automatically bumped (patch increment)
   - Tag is automatically created and pushed
   - Package is automatically published to PyPI
   - GitHub release is automatically created

### Manual Release via GitHub Actions

If you need to trigger a release manually or specify a different version bump:

1. **Go to GitHub Actions**
2. **Select the "Release" workflow**
3. **Click "Run workflow"**
4. **Configure the release**:
   - **Version**: Enter the version (e.g., `0.1.0`)
   - **Release type**: Choose patch/minor/major
5. **Click "Run workflow"**

## Version Management Commands

```bash
# Show current version
python scripts/version.py current

# Bump version (for manual releases)
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
- **Patch**: Bug fixes (0.1.0 → 0.1.1) - **Automatic on MR**
- **Minor**: New features, backward compatible (0.1.0 → 0.2.0) - **Manual**
- **Major**: Breaking changes (0.1.0 → 1.0.0) - **Manual**

## PyPI Publishing

### Production PyPI
- **Trigger**: Automatic on merge to main from develop
- **Repository**: https://pypi.org/project/python-redis-factory/
- **Workflow**: `.github/workflows/release.yml`

## Branch Protection Workflow

### Protected Main Branch
- **Direct pushes to main**: Disabled
- **Required status checks**: Must pass before merging
- **Required reviews**: At least one approval
- **Release workflow**: Triggers on pushes to main

### Develop Branch
- **Direct pushes**: Allowed for development
- **CI workflow**: Runs on pushes and PRs
- **Workflow**: Develop → MR → Main → Auto-Release

### Automatic Release Process
1. **Develop** on `develop` branch
2. **Create MR** from `develop` to `main`
3. **Merge** after approvals and CI passes
4. **Automatic version bump** (patch increment)
5. **Automatic tag creation**
6. **Automatic release** to PyPI

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
5. **MR blocked**: Ensure all CI checks pass and you have required approvals
6. **Auto-version not working**: Check if the commit message contains "Merge pull request"

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