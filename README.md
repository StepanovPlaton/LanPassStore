## LanPassStore

Приложение состоит из двух сервисов:

- **backend**: Go API и админка (`backend`)
- **frontend**: Angular/Analog клиент (`frontend`)

## Локальный запуск

- **Через Docker Compose**: используйте `docker-compose.yml` и `.env` из корня репозитория.
- **Локально**:
  - backend: `cd backend && go test ./... && go run ./cmd/main.go`
  - frontend: `cd frontend && pnpm install && pnpm dev`

## CI/CD через GitHub Actions и GHCR

При каждом push в ветку `main` автоматически запускаются два workflow:

- `.github/workflows/backend-ci-cd.yml`
- `.github/workflows/frontend-ci-cd.yml`

### Проверки кода

- **Backend**:
  - Запускаются Go-тесты: `go test ./...` в директории `backend`.
- **Frontend**:
  - Устанавливаются зависимости через `pnpm install`.
  - Запускаются тесты: `pnpm test`.

### Сборка и публикация Docker-образов

После успешных проверок выполняется сборка и публикация Docker-образов в GitHub Container Registry (GHCR):

- **Backend образ** публикуется как:
  - `ghcr.io/<OWNER>/<REPO>-backend:latest`
  - `ghcr.io/<OWNER>/<REPO>-backend:<short-sha>`
- **Frontend образ** публикуется как:
  - `ghcr.io/<OWNER>/<REPO>-frontend:latest`
  - `ghcr.io/<OWNER>/<REPO>-frontend:<short-sha>`

`<OWNER>` и `<REPO>` автоматически берутся из контекста GitHub (`github.repository`).

### Пример использования образов

В любом окружении (включая Docker Compose) вы можете использовать опубликованные образы, например:

```yaml
services:
  backend:
    image: ghcr.io/<OWNER>/<REPO>-backend:latest

  frontend:
    image: ghcr.io/<OWNER>/<REPO>-frontend:latest
```

Рекомендуется для продакшена использовать тег с конкретным SHA, например:

```yaml
image: ghcr.io/<OWNER>/<REPO>-backend:abc1234
```

