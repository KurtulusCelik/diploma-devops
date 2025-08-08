# Books Catalog API (DevOps Diploma 2025)

A simple Book Catalog REST API built with Django and Django REST Framework. The project is containerized with Docker, deployable via a Helm chart, and automated with GitHub Actions (tests, semantic-release, Docker image build/push, and GitOps-friendly deployment flow).

### Project overview
- **Tech stack**: Python 3.13, Django 5, Django REST Framework
- **Purpose**: Provide a minimal CRUD starting point for a book catalog, suitable for DevOps demos (CI, CD, Helm, K8s, GitOps)
- **Data model**: `Book` with fields `title`, `description`, `author`, `isbn`, `published_date`
- **Environments**:
  - Development: SQLite (no external DB needed)
  - Production: PostgreSQL (env-configured)
- **Container**: `Dockerfile` with `entrypoint.sh` that waits for DB, runs migrations, and serves on port `8000`
- **Helm chart**: `books-catalog-chart` (includes deployment, service, ingress, pre-install/upgrade migration job)
- **CI/CD**: GitHub Actions with pytest, semantic-release, GHCR image publishing, and values bumping for GitOps


### API usage examples
Base URL assumes local dev (`http://localhost:8000`). All endpoints are prefixed with `/api/`.

- **Health**
  - Request:
    ```bash
    curl -s http://localhost:8000/api/
    ```
  - Response:
    ```json
    { "status": "ok" }
    ```

- **Test**
  - Request:
    ```bash
    curl -s http://localhost:8000/api/test/
    ```
  - Response:
    ```json
    { "test": "ok" }
    ```

- **List books**
  - Request:
    ```bash
    curl -s http://localhost:8000/api/books/
    ```
  - Response (example):
    ```json
    [
      {
        "title": "Demo",
        "description": "Description",
        "author": "Author",
        "isbn": "9780135957059",
        "published_date": "2019-09-13"
      }
    ]
    ```

- **Create book**
  - Request:
    ```bash
    curl -s -X POST http://localhost:8000/api/books/ \
      -H 'Content-Type: application/json' \
      -d '{
        "title": "The Pragmatic Programmer",
        "description": "From Journeyman to Master",
        "author": "Andrew Hunt, David Thomas",
        "isbn": "9780201616224",
        "published_date": "1999-10-20"
      }'
    ```
  - Response:
    ```json
    {
      "title": "The Pragmatic Programmer",
      "description": "From Journeyman to Master",
      "author": "Andrew Hunt, David Thomas",
      "isbn": "9780201616224",
      "published_date": "1999-10-20"
    }
    ```

Notes:
- Current implementation returns HTTP 200 on creation.
- Serializer fields: `title`, `description`, `author`, `isbn`, `published_date` (no `id` in response by default).
- `isbn` accepts 10 or 13 digits (dashes/spaces allowed); `published_date` is `YYYY-MM-DD`.

- **Retrieve book**
  - Request:
    ```bash
    curl -s http://localhost:8000/api/books/1/
    ```
  - Response (example):
    ```json
    {
      "title": "Demo",
      "description": "Description",
      "author": "Author",
      "isbn": "9780135957059",
      "published_date": "2019-09-13"
    }
    ```

- **Update book (PUT)**
  - Request:
    ```bash
    curl -s -X PUT http://localhost:8000/api/books/1/ \
      -H 'Content-Type: application/json' \
      -d '{
        "title": "Demo Updated",
        "description": "New Description",
        "author": "Author",
        "isbn": "9780135957059",
        "published_date": "2020-01-01"
      }'
    ```
  - Response: same shape as retrieve

- **Partial update (PATCH)**
  - Request:
    ```bash
    curl -s -X PATCH http://localhost:8000/api/books/1/ \
      -H 'Content-Type: application/json' \
      -d '{ "description": "Only description changed" }'
    ```

- **Delete book**
  - Request:
    ```bash
    curl -i -X DELETE http://localhost:8000/api/books/1/
    ```
  - Response: `204 No Content`


### Local development

#### Option A: Python virtualenv (SQLite dev mode)
Requirements: Python 3.13+

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell
# .venv\\Scripts\\Activate.ps1

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

Visit `http://localhost:8000/api/`.

Run tests:
```bash
pytest -q
```

Environment variables (development defaults are adequate):
- `DEVELOPMENT_MODE` (default: `True`) – when `True`, uses SQLite
- `DATABASE_NAME`, `DATABASE_USER`, `DATABASE_PASSWORD`, `DATABASE_HOST` – used when `DEVELOPMENT_MODE=False`


#### Option B: Docker Compose (PostgreSQL)
Requirements: Docker and Docker Compose

```bash
docker compose up --build
```

This starts:
- `app`: Django API on `:8000`
- `db`: PostgreSQL 17 with a persisted volume

Visit `http://localhost:8000/api/`.


#### Run the image directly
Use SQLite (dev mode) without a database:
```bash
docker run --rm -p 8000:8000 \
  -e DEVELOPMENT_MODE=true \
  ghcr.io/kurtuluscelik/diploma-devops:<tag>
```

Use PostgreSQL (prod mode):
```bash
docker run --rm -p 8000:8000 \
  -e DEVELOPMENT_MODE=false \
  -e DATABASE_NAME=books_db \
  -e DATABASE_USER=books \
  -e DATABASE_PASSWORD=books \
  -e DATABASE_HOST=<postgres-host> \
  ghcr.io/kurtuluscelik/diploma-devops:<tag>
```


### CI/CD pipeline (GitHub Actions)
Workflow: `.github/workflows/test.yml`

- **Triggers**: On PRs to `main` and on pushes to `main`.
- **Jobs**:
  - `test`: Installs dependencies and runs `pytest`.
  - `runmigrations`: Runs `python manage.py migrate` to verify migrations.
  - `migrations-check`: Runs `python manage.py makemigrations --check` to ensure no unstaged model changes.
  - `semantic-release` (needs: test, runmigrations, migrations-check): Uses conventional commits to decide if a new version should be released, creates a GitHub Release, and outputs `new_release_version`.
  - `build-docker-image` (needs: semantic-release): If a new release is published, builds and pushes the Docker image to GHCR `ghcr.io/kurtuluscelik/diploma-devops` tagged with the new semver.
  - `deploy-application` (needs: semantic-release, build-docker-image): Updates `envs/prod/values.yaml` to bump `image.tag` to the newly released version and commits the change on `main` (GitOps trigger).

- **Registries and permissions**:
  - Uses `GITHUB_TOKEN` for `semantic-release` and GHCR login.
  - Pushes to `ghcr.io/kurtuluscelik/diploma-devops` with semver tags.

- **Semantic-release**:
  - Follows Conventional Commits (feat, fix, chore, etc.).
  - Automates CHANGELOG and versioning.

This flow is GitOps-friendly: changing `envs/prod/values.yaml` can be used by an Argo CD `Application` to reconcile the cluster to the new image.


### Kubernetes and Helm

#### Prerequisites
- A Kubernetes cluster and `kubectl`
- Helm v3
- Access to GHCR image `ghcr.io/kurtuluscelik/diploma-devops`
- An ingress controller if you want `/api` accessible externally

#### Image pull secret (if your cluster requires it)
Create a Docker registry secret and reference it as `ghcr-token` (matches chart values):
```bash
kubectl create secret docker-registry ghcr-token \
  --docker-server=ghcr.io \
  --docker-username=<gh-username> \
  --docker-password=<gh-personal-access-token> \
  --namespace default
```

Update namespace and secret name in `books-catalog-chart/values.yaml` if needed.

#### Database options
You have two main options for PostgreSQL:

- Option 1: Install a PostgreSQL Helm chart (recommended). For example, Bitnami:
  ```bash
  helm repo add bitnami https://charts.bitnami.com/bitnami
  helm repo update
  helm install books-database bitnami/postgresql \
    --set auth.username=books \
    --set auth.password=<db-password> \
    --set auth.database=books
  ```
  Then create a Secret that the app expects for the password:
  ```bash
  kubectl create secret generic books-database-postgresql \
    --from-literal=password=<db-password>
  ```
  Note: The chart defaults reference a headless hostname for a StatefulSet pod. You can also use the regular service DNS name and override `DATABASE_HOST` accordingly.

- Option 2: Use the raw manifests in `k8s_yamls/postgres/` to spin up a minimal PostgreSQL (dev/demo only). Ensure the Secret name and key match what the app expects, or override the Helm values.

#### Configure values
Key Helm values (see `books-catalog-chart/values.yaml`):
- `image.repository`: container registry (default: `ghcr.io/kurtuluscelik/diploma-devops`)
- `image.tag`: image tag; in production, `envs/prod/values.yaml` is updated by CI
- `imagePullSecrets`: list including `ghcr-token` if required
- `environmentVariables`: populated as a ConfigMap and consumed by the app
  - Typically set:
    - `DATABASE_NAME`: `books`
    - `DATABASE_USER`: `books`
    - `DATABASE_HOST`: e.g. `books-database-postgresql.default.svc.cluster.local`
    - `DEVELOPMENT_MODE`: `"false"`
- `loadSecretFrom`: name of a Secret with a `password` key (database password)

Example override file (prod): `envs/prod/values.yaml` (auto-bumped by CI):
```yaml
image:
  tag: 1.2.3
```

#### Install/upgrade the release
From the repo root:
```bash
# Install (or upgrade) the API with production values
target_tag=<tag> # e.g., 1.2.3
helm upgrade --install books-api ./books-catalog-chart \
  --values envs/prod/values.yaml \
  --set image.tag=${target_tag}
```

The chart includes a pre-install/upgrade Job that runs `python manage.py migrate` with the same image and environment.

#### Accessing the service
- The chart exposes a `ClusterIP` Service on port `80`, targeting the container `8000`.
- An Ingress is created for path prefix `/api`.
- For quick local testing without an ingress controller:
  ```bash
  kubectl port-forward svc/books-api 8000:80
  curl -s http://localhost:8000/api/
  ```
  Replace `books-api` with the actual release name if different.


### Repository layout
- `api/`: DRF views, serializers, URLs, tests
- `bookcatalog/`: Django project settings and root URLs
- `books-catalog-chart/`: Helm chart (deployment, service, ingress, env config, migration job)
- `k8s_yamls/`: Assorted raw manifests (nginx demo, NodePort, PVCs, PostgreSQL example, Argo CD values)
- `.github/workflows/test.yml`: CI/CD workflow
- `envs/prod/values.yaml`: Production overrides (image tag bumped by CI)
- `Dockerfile`, `docker-compose.yml`, `entrypoint.sh`: Container build and runtime


### Environment variables (summary)
- `DEVELOPMENT_MODE` (bool-like): `true` uses SQLite, `false` uses PostgreSQL
- `DATABASE_NAME`: Postgres database name
- `DATABASE_USER`: Postgres user
- `DATABASE_PASSWORD`: Postgres password
- `DATABASE_HOST`: Postgres hostname (service DNS)


