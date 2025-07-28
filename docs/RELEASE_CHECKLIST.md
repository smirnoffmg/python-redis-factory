# Release Checklist

A quick checklist for making new releases of `python-redis-factory`.

## Pre-Release Checklist

- [ ] **All tests pass**: `make test-parallel`
- [ ] **Linting passes**: `make lint`
- [ ] **Type checking passes**: `make type-check`
- [ ] **Documentation updated**: README.md, docstrings
- [ ] **No breaking changes** (unless intentional major release)
- [ ] **Dependencies are up to date**: `uv sync`

## Release Process

### Option 1: Automated Release (Recommended)

```bash
# 1. Ensure you're on main branch
git checkout main
git pull origin main

# 2. Run full quality checks
make ci

# 3. Choose release type and execute
make release-patch  # Bug fixes (0.1.0 -> 0.1.1)
make release-minor  # New features (0.1.0 -> 0.2.0)
make release-major  # Breaking changes (0.1.0 -> 1.0.0)

# 4. GitHub Actions automatically handles the rest!
```

### Option 2: Manual Release via GitHub Actions

1. Go to GitHub Actions → Release workflow
2. Click "Run workflow"
3. Enter version and choose release type
4. Click "Run workflow"

### Option 3: Manual Release (Local)

```bash
# 1. Run quality checks
make ci

# 2. Bump version
python scripts/version.py bump minor  # or patch, major

# 3. Create tag and push
python scripts/version.py tag

# 4. Build and upload (if needed)
make build
uv run twine upload dist/*
```

## Post-Release Verification

- [ ] **Check PyPI**: https://pypi.org/project/python-redis-factory/
- [ ] **Test installation**: `pip install python-redis-factory==<new-version>`
- [ ] **Check GitHub release**: https://github.com/smirnoffmg/python-redis-factory/releases
- [ ] **Verify package works**:
  ```python
  from python_redis_factory import get_redis_client
  client = get_redis_client("redis://localhost:6379")
  ```

## Version Management

### Current Version
```bash
make version  # Shows current version
```

### Version Location
- **Source**: `src/python_redis_factory/__init__.py` (line 17)
- **Current**: `0.1.0`

### Version Commands
```bash
python scripts/version.py current              # Show version
python scripts/version.py current --version-only  # Show version only
python scripts/version.py bump patch           # 0.1.0 -> 0.1.1
python scripts/version.py bump minor           # 0.1.0 -> 0.2.0
python scripts/version.py bump major           # 0.1.0 -> 1.0.0
python scripts/version.py set 0.2.0            # Set specific version
python scripts/version.py tag                  # Create git tag
```

## Troubleshooting

### Common Issues

**Build fails**: Check GitHub Actions logs for test/lint failures

**PyPI upload fails**: Verify `PYPI_API_TOKEN` secret is set

**Version already exists**: Workflow uses `skip-existing: true`

**Tag already exists**: Version script will warn you

**Git identity error**: Workflow now configures git automatically

### Emergency Manual Release
```bash
make ci
python scripts/version.py bump patch
python scripts/version.py tag
make build
uv run twine upload dist/*
```

## Quick Reference

| Command              | Description            |
| -------------------- | ---------------------- |
| `make version`       | Show current version   |
| `make release-patch` | Release patch version  |
| `make release-minor` | Release minor version  |
| `make release-major` | Release major version  |
| `make ci`            | Run all quality checks |
| `make build`         | Build package          |

## Links

- **PyPI**: https://pypi.org/project/python-redis-factory/
- **GitHub Releases**: https://github.com/smirnoffmg/python-redis-factory/releases
- **Detailed Guide**: [RELEASE.md](RELEASE.md) 