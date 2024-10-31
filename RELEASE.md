# Releasing a new version of `bedrock-gi`

## 1. Update the Version Number

Follow [Semantic Versioning](https://semver.org/) (e.g., `1.0.0`, `1.1.0`, `1.1.1`):

- **Major** version: For incompatible API changes.
- **Minor** version: For new features that are backward-compatible.
- **Patch** version: For backward-compatible bug fixes.

Update the version number in:

- [`pyproject.toml`](pyproject.toml)
- [`/src/bedrock/__init__.py`](/src/bedrock/__init__.py)

## 2. Update the Changelog

Update `CHANGELOG.md` with details about the new release. Include any new features, bug fixes, or breaking changes.

## 3. Run Tests

Ensure that all tests pass by running your test suite.

To automate this, it's possible to set up a CI (Continuous Integration) pipeline to confirm everything works in multiple environments, e.g. with `GitHub Actions`.

## 4. Commit the Changes

Commit the files that contain the updated version number and `CHANGELOG.md`:

```bash
git add .
git commit -m "Release version X.Y.Z"
```

## 5. Prepare for Merge

Open a pull request (PR) from `dev` to `main`.

## 6. Merge `dev` into `main`

Once everything is ready, and the PR is approved, merge `dev` into `main`. This officially brings all the changes in `dev` into the release-ready `main` branch.

## 7. Tag the Release

Create a Git tag for the new version:

```bash
git checkout main
git tag X.Y.Z
git push origin X.Y.Z
```

## 8. Build the Distribution

Create source and wheel distributions:

```bash
uv build
```

## 9. Upload to PyPI

Upload the new version to PyPI (Python Package Index):

```bash
uvx twine upload dist/*
```

> ⚠️ **Attention:**
>
> You might have to delete previous distributions of the Python package in `dist/*`
>
> Ensure you have the correct credentials for PyPI in your environment. These should be in `~/.pypirc`

## 10. Verify the Release

Check that the new version is available on PyPI:  
<https://pypi.org/project/bedrock-gi/>

Install the new Python package version in a clean environment to verify it works:

```bash
mkdir check-bedrock-gi-release
uv init
uv add bedrock-gi
```

## 11. Create a GitHub Release

Create a new release based on the tag.
