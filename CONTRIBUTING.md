# Contributing to ArtifactLens

## Branch Protection

The `main` branch is protected. Direct pushes are not allowed.

All changes must go through a pull request:

1. **Create a feature branch** from `main`
   ```bash
   git checkout main
   git pull
   git checkout -b your-branch-name
   ```

2. **Make your changes**, commit, and push
   ```bash
   git add .
   git commit -m "Describe your change"
   git push origin your-branch-name
   ```

3. **Open a Pull Request** on GitHub against `main`

4. **Wait for CI** — the pipeline must pass (syntax check + build)

5. **Request review** — a project maintainer must approve before merging

## CI Pipeline

Every push and PR triggers the CI workflow which:
- Runs syntax checks on all Python source files
- Validates that all modules import correctly
- Builds the executable via PyInstaller
- Uploads the build artifact

PRs cannot be merged until CI passes.

## Development Setup

```bash
# Clone the repo
git clone https://github.com/william051200/azure-artifacts-search.git
cd azure-artifacts-search

# Create a virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Running the App

```bash
python -m search_artifact_app
```

## Building the Executable

```bash
scripts\build.bat
```

The output will be at `dist\ArtifactLens\ArtifactLens.exe`.
