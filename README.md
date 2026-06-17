# CodePulse AI — GitHub Repository Quality Analyzer

A production-ready microservices application that analyzes GitHub repositories and provides quality metrics including README, testing, structure scores, and GitHub metadata enrichment.

## Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   React UI  │────▶│  Repository Svc  │────▶│  Analysis Svc    │
│   (Vite)    │     │  (Spring Boot)   │     │  (Python Flask)  │
│   :3000     │     │  :8080           │     │  :5000           │
└─────────────┘     └────────┬─────────┘     └──────────────────┘
                             │                        │
                     ┌───────▼───────┐         git clone (depth=1)
                     │    MySQL      │                │
                     │    :3306      │         ┌──────▼──────┐
                     └───────────────┘         │  GitHub     │
                                               │  Repos      │
                                               └─────────────┘
```

## Features

- **Repository Submission** — Submit any public GitHub repo URL for analysis
- **Async Analysis** — Non-blocking background processing with status polling
- **Quality Scores** — README (0-100), Testing (0-100), Structure (0-100)
- **Structure Scoring** — 6-criteria evaluation: README, LICENSE, .gitignore, tests, CI/CD, dependency files
- **GitHub Metadata** — Stars, forks, issues, default branch, last commit date
- **Language Detection** — Automatic programming language breakdown
- **Code Metrics** — Total files and lines of code
- **Future-Ready** — `ai_recommendations` table designed for Phase 4 LLM integration

## Tech Stack

| Service | Technology | Port |
|---------|-----------|------|
| Frontend | React + Vite | 3000 |
| Backend API | Java 17 + Spring Boot 3.2 | 8080 |
| Analysis Engine | Python 3.11 + Flask | 5000 |
| Database | MySQL 8.0 | 3306 |
| HTTP Client | WebClient (Spring WebFlux) | — |

## Quick Start (Local Development)

### Prerequisites

- Java 17+
- Python 3.9+
- Node.js 18+
- MySQL 8.0 (or Docker)
- Git

### 1. Start MySQL

```bash
# Using Docker
docker run -d --name codepulse-mysql \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=codepulse \
  -p 3306:3306 \
  mysql:8.0
```

### 2. Start Analysis Service (Python)

```bash
cd analysis-service
pip install -r requirements.txt
python app.py
# Running on http://localhost:5000
```

### 3. Start Repository Service (Spring Boot)

```bash
cd repository-service
mvn spring-boot:run
# Running on http://localhost:8080
```

### 4. Start Frontend (React)

```bash
cd frontend
npm install
npm run dev
# Running on http://localhost:5173
```

### Docker Compose (All Services)

```bash
docker-compose up --build
```

## API Reference

### Submit Repository

```bash
POST /api/repositories
Content-Type: application/json

{
  "repoUrl": "https://github.com/owner/repo"
}

# Response: 201 Created
{
  "id": 1,
  "repoName": "repo",
  "owner": "owner",
  "status": "PENDING",
  "message": "Repository submitted successfully. Analysis in progress."
}
```

### Poll Status

```bash
GET /api/repositories/{id}/status

# Response
{
  "id": 1,
  "repoName": "repo",
  "status": "ANALYZING"  // PENDING | ANALYZING | COMPLETED | FAILED
}
```

### Get Report

```bash
GET /api/repositories/{id}/report

# Response (when status = COMPLETED)
{
  "repoName": "repo",
  "owner": "owner",
  "readmeScore": 100,
  "testingScore": 100,
  "structureScore": 84,
  "overallScore": 94.67,
  "totalFiles": 150,
  "totalLines": 12000,
  "languages": { "Python": 80, "JavaScript": 30 },
  "stars": 5000,
  "forks": 800,
  "openIssues": 120,
  "defaultBranch": "main",
  "lastCommitDate": "2024-01-15T10:30:00",
  "description": "A micro web framework"
}
```

### List Repositories

```bash
GET /api/repositories

# Response
[
  { "id": 1, "repoName": "repo", "owner": "owner", "status": "COMPLETED" }
]
```

## Database Schema

- `repositories` — Submitted repos with status tracking
- `reports` — Analysis scores and metrics (FK → repositories)
- `github_metadata` — Stars, forks, issues from GitHub API (FK → repositories)
- `ai_recommendations` — Future AI/LLM recommendations (FK → reports, Phase 4)

## Scoring

| Category | Score | Criteria |
|----------|-------|----------|
| README | 0 or 100 | README file present |
| Testing | 0 or 100 | Test directories or test files found |
| Structure | 0–100 | 6 checks × ~17pts each: README, LICENSE, .gitignore, tests, CI/CD, dependency file |
| Overall | Average | (readme + testing + structure) / 3 |

## Future Phases

- **Phase 2**: Cyclomatic complexity, code smell detection, dependency analysis
- **Phase 3**: Security vulnerability scanning, secret/API key detection
- **Phase 4**: AI-generated repository review and recommendations (LLM integration)

## License

MIT
