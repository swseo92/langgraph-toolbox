# langgraph-toolbox

**Community utilities and patterns for LangGraph development**

**상태**: 초기 개발 중 (Alpha)
**언어**: Python 3.10+
**환경 구성일**: 2025-11-04
**타입**: Open Source Library

---

## ⚠️ 프로젝트 루트 폴더 규칙

**이 `claude.md` 파일이 위치한 폴더가 프로젝트의 루트(root) 디렉토리입니다.**

### 작업 범위 제한
- ✅ 모든 작업은 **이 루트 폴더를 기준**으로 수행됩니다
- ✅ 파일 경로는 **이 루트 폴더 기준 상대 경로** 또는 절대 경로를 사용합니다
- ❌ **상위 폴더(`../`)는 절대 참조하지 않습니다**
- ❌ 프로젝트 외부 파일은 수정하거나 참조하지 않습니다

### Claude Code 작업 가이드라인
```
프로젝트 루트/               ← 이 claude.md가 위치한 폴더
├── claude.md               ← 현재 파일 (프로젝트 루트 마커)
├── src/                    ← ✅ 접근 가능
├── tests/                  ← ✅ 접근 가능
├── pyproject.toml          ← ✅ 접근 가능
└── ...                     ← ✅ 루트 하위 모든 파일 접근 가능

../                         ← ❌ 상위 폴더 접근 금지
../../                      ← ❌ 상위의 상위 폴더 접근 금지
```

**중요**: Claude Code는 이 규칙을 엄격히 준수해야 합니다. 프로젝트 범위를 벗어난 작업은 수행하지 않습니다.

---

## 중요: Commit 시 주의사항

**이 파일은 프로젝트별로 커스터마이징이 필요합니다.**

Commit하기 전에 다음 항목들을 확인하고 수정하세요:

- [ ] **환경 구성일**: 실제 프로젝트 시작일 또는 오늘 날짜로 변경
- [ ] **프로젝트 설명**: 아래 섹션에 프로젝트 목적과 주요 기능 추가
- [ ] **환경변수**: 필요한 환경변수를 `.env.example`에 추가하고 문서화
- [ ] **의존성**: `pyproject.toml`에 실제 의존성 반영
- [ ] **테스트**: 테스트 전략 및 실행 방법 문서화

---

## 프로젝트 설명

> ⚠️ **This is an unofficial, community-maintained project.**
> Not affiliated with or endorsed by LangChain Inc.

`langgraph-toolbox`는 LangGraph 개발을 더 효율적으로 만들기 위한 커뮤니티 주도 유틸리티 라이브러리입니다.

**목적:**
- LangGraph 개발 시 자주 사용하는 패턴들을 재사용 가능한 함수로 제공
- State 관리, Node 패턴, 조건부 라우팅 등의 공통 로직 추상화
- 테스트 및 디버깅을 위한 헬퍼 유틸리티 제공
- 커뮤니티가 함께 만들어가는 오픈소스 라이브러리

**주요 기능 (계획):**
- **State Management**: TypedDict 기반 State 스키마 유틸리티
- **Node Patterns**: Retry, error handling 등의 재사용 가능한 Node 템플릿
- **Conditional Routing**: 동적 라우팅 및 조건부 분기 헬퍼
- **Testing Utilities**: Mock state, test graph builder
- **High-level Abstractions**: 공통 에이전트 워크플로우 패턴

---

## 개발 환경

### 필수 도구
- **Python**: 3.10 이상
- **패키지 매니저**: `uv` (권장) 또는 `pip`
- **가상환경**: 자동 생성 (`.venv/`)
- **Git Worktree**: 병렬 개발을 위한 워크트리 지원
- **의존성**: langgraph>=0.2.0, langchain-core>=0.3.0

### 설치 및 실행

**1. 의존성 설치:**
```bash
# uv 사용 (권장)
uv sync

# 또는 pip 사용
pip install -e .
```

**2. 환경변수 설정:**
```bash
# .env.example을 복사하여 .env 생성
cp .env.example .env

# .env 파일을 편집하여 실제 값 입력
# 필요한 환경변수는 아래 "환경변수 관리" 섹션 참조
```

**3. 개발 서버 실행:**
```bash
# 애플리케이션 실행 (예시)
python src/main.py

# 또는 uvicorn (FastAPI 프로젝트인 경우)
uvicorn src.main:app --reload
```

**4. 테스트 실행:**
```bash
# 전체 테스트
pytest

# 커버리지 포함
pytest --cov=src tests/

# 특정 테스트 파일만
pytest tests/test_example.py
```

---

## ⚠️ 환경변수 관리 (MANDATORY)

**🚨 모든 환경변수는 반드시 `python-dotenv` 라이브러리를 통해 로드해야 합니다.**

### 기본 원칙

1. **절대 하드코딩 금지**
   - ❌ `API_KEY = "sk-abc123..."` (코드에 직접 작성)
   - ✅ `API_KEY = os.getenv("API_KEY")` (환경변수에서 로드)

2. **`.env` 파일은 Git에 커밋하지 않음**
   - ❌ `.env` 파일 커밋 (보안 위험!)
   - ✅ `.env.example` 템플릿만 커밋

3. **`load_dotenv()` 사용 필수**
   - 모든 Python 스크립트는 환경변수 사용 전에 `load_dotenv()` 호출

### 사용 방법

**1. 의존성 추가 (이미 포함되어 있음):**
```toml
# pyproject.toml
[project]
dependencies = [
    "python-dotenv>=1.0.0",
    # ... 기타 의존성
]
```

**2. 코드에서 환경변수 로드:**

```python
# src/main.py 또는 모든 entry point 파일의 최상단
import os
from dotenv import load_dotenv

# .env 파일에서 환경변수 로드 (프로젝트 루트의 .env)
load_dotenv()

# 이제 환경변수 사용 가능
DATABASE_URL = os.getenv("DATABASE_URL")
API_KEY = os.getenv("API_KEY")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# 필수 환경변수 검증
if not DATABASE_URL:
    raise ValueError("DATABASE_URL 환경변수가 설정되지 않았습니다.")
```

**3. `.env` 파일 예시:**
```bash
# .env (Git에 커밋하지 않음!)
DATABASE_URL=postgresql://user:password@localhost:5432/mydb
API_KEY=sk-abc123xyz789
DEBUG=True
LOG_LEVEL=INFO
```

**4. `.env.example` 템플릿 작성:**
```bash
# .env.example (Git에 커밋함)
# 이 파일을 복사하여 .env를 생성하고 실제 값을 입력하세요

# 데이터베이스 연결 정보
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# API 키
API_KEY=your_api_key_here

# 디버그 모드 (True/False)
DEBUG=False

# 로그 레벨 (DEBUG/INFO/WARNING/ERROR)
LOG_LEVEL=INFO
```

### 환경변수 체크리스트

프로젝트에서 사용하는 모든 환경변수를 여기에 문서화하세요:

| 환경변수 | 필수 | 기본값 | 설명 |
|----------|------|--------|------|
| `DATABASE_URL` | ✅ | - | PostgreSQL 연결 문자열 |
| `API_KEY` | ✅ | - | 외부 API 인증 키 |
| `DEBUG` | ❌ | `False` | 디버그 모드 활성화 |
| `LOG_LEVEL` | ❌ | `INFO` | 로그 레벨 (DEBUG/INFO/WARNING/ERROR) |
| `SECRET_KEY` | ✅ | - | 세션/JWT 서명 키 |

### 배포 환경별 설정

**개발 환경 (`.env`):**
```bash
DEBUG=True
LOG_LEVEL=DEBUG
DATABASE_URL=postgresql://localhost:5432/mydb_dev
```

**프로덕션 환경:**
```bash
# 환경변수는 시스템 레벨에서 설정 (Docker, K8s secrets, etc.)
# .env 파일 사용 안 함!
export DEBUG=False
export LOG_LEVEL=WARNING
export DATABASE_URL=postgresql://prod-db:5432/mydb_prod
```

### 보안 주의사항

- ⚠️ **절대 `.env` 파일을 Git에 커밋하지 마세요**
- ⚠️ **민감 정보는 로그에 출력하지 마세요**
- ⚠️ **환경변수 값을 코드 리뷰에 포함하지 마세요**
- ✅ **`.gitignore`에 `.env`가 포함되어 있는지 확인**

---

## 개발 규칙

### 코드 스타일
- **PEP 8** 준수
- **타입 힌트** 사용 권장 (Python 3.10+ 타입 문법)
- **Formatter**: `black` (line length 100)
- **Linter**: `ruff` (Flake8 + isort 대체)

**포매팅 실행:**
```bash
# 코드 포매팅
black src/ tests/

# Lint 검사 및 자동 수정
ruff check --fix src/ tests/

# 타입 체킹
mypy src/
```

### 임시 파일 관리
**🚨 모든 임시/테스트/실험 파일은 반드시 `tmp/` 폴더에만 생성합니다.**

- ✅ **DO**: `tmp/test-feature.py`, `tmp/experiment/`
- ❌ **NEVER**: `test-feature.py`, `experiment/` (루트에 직접 생성 금지)

**이유:** 보안 리스크, Git 오염, 관리 불가 방지

### 테스트 작성
- **최소 80% 커버리지** 유지
- **모든 공개 함수**에 대한 단위 테스트 작성
- **통합 테스트**로 주요 워크플로우 검증
- **테스트 파일 명명**: `test_{module_name}.py`

### Commit 규칙
```
type(scope): description

Types:
- feat: 새 기능
- fix: 버그 수정
- docs: 문서 업데이트
- refactor: 리팩토링
- test: 테스트 추가/수정
- chore: 빌드/설정 변경

Examples:
- feat(auth): add OAuth2 login
- fix(api): handle null values in response
- docs(readme): update installation guide
```

---

## 디렉토리 구조

```
프로젝트 루트/
├── src/                    # 소스 코드
│   ├── __init__.py
│   ├── main.py             # Entry point
│   ├── config.py           # 환경변수 로드 및 설정
│   └── ...                 # 모듈들
├── tests/                  # 테스트 코드
│   ├── __init__.py
│   ├── conftest.py         # Pytest fixtures
│   ├── test_main.py
│   └── ...
├── docs/                   # 문서
├── notebooks/              # Jupyter 노트북 (선택)
├── .claude/                # Claude Code 설정
│   ├── scripts/            # Hook 스크립트
│   └── settings.json       # 로컬 설정
├── .env                    # 환경변수 (Git 무시)
├── .env.example            # 환경변수 템플릿
├── .gitignore
├── pyproject.toml          # 프로젝트 설정 및 의존성
├── pytest.ini              # Pytest 설정
├── README.md               # 프로젝트 개요
└── claude.md               # 이 파일
```

---

## 의존성 관리

### 주요 라이브러리
- **python-dotenv**: 환경변수 로드 (필수)
- **pytest**: 테스트 프레임워크
- **pytest-cov**: 커버리지 측정
- **black**: 코드 포매터
- **ruff**: Fast linter
- **mypy**: 정적 타입 검사

### 의존성 추가
```bash
# 런타임 의존성 추가
uv add <package-name>

# 개발 의존성 추가
uv add --dev <package-name>

# 의존성 동기화
uv sync
```

---

## Git Worktree 기반 병렬 개발

이 프로젝트는 **Git Worktree**를 활용한 병렬 개발을 지원합니다.

### Worktree란?

Git Worktree는 하나의 저장소에서 여러 브랜치를 동시에 작업할 수 있게 해주는 기능입니다.

**장점:**
- 여러 기능을 동시에 개발 가능 (브랜치 전환 없이)
- 각 워크트리는 독립적인 작업 디렉토리
- 테스트와 개발을 병렬로 진행 가능

### Worktree 생성

**새 기능 개발 시:**
```bash
# 슬래시 커맨드 사용 (추천)
claude
/worktree-create feature/state-helpers

# 또는 직접 git 명령어
git worktree add ../langgraph-toolbox-state-helpers -b feature/state-helpers
```

**생성 후 구조:**
```
PycharmProjects/project/
├── langgraph-toolbox/              # Main worktree (main branch)
└── langgraph-toolbox-state-helpers/  # Feature worktree
```

### Worktree에서 작업

```bash
# Feature worktree로 이동
cd ../langgraph-toolbox-state-helpers

# 개발 및 테스트
uv sync
pytest

# 커밋 및 푸시
git add .
git commit -m "feat: add state helpers"
git push origin feature/state-helpers
```

### Worktree 병합 및 정리

```bash
# Main worktree로 돌아가기
cd ../langgraph-toolbox

# 슬래시 커맨드로 병합 (추천)
/merge feature/state-helpers

# Worktree 정리
/worktree-cleanup feature/state-helpers
```

### 사용 가능한 Worktree 커맨드

Claude Code에서 다음 명령어들을 사용할 수 있습니다:

- `/worktree-create <branch-name>` - 새 워크트리 생성
- `/worktree-list` - 현재 워크트리 목록 확인
- `/worktree-cleanup <branch-name>` - 워크트리 삭제 및 정리
- `/merge <source-branch>` - 브랜치 병합 (자동 conflict 해결)

### Worktree 모범 사례

1. **기능별로 분리**: 각 기능은 별도의 worktree에서 개발
2. **명확한 브랜치명**: `feature/`, `fix/`, `refactor/` 등의 prefix 사용
3. **정기적인 정리**: 완료된 worktree는 즉시 제거
4. **독립적인 가상환경**: 각 worktree는 독립적인 `.venv/` 사용

---

## 문제 해결

### 환경변수가 로드되지 않을 때
```python
# 1. .env 파일 위치 확인
import os
from pathlib import Path

print("현재 작업 디렉토리:", os.getcwd())
print(".env 파일 존재:", Path(".env").exists())

# 2. 명시적 경로 지정
from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

# 3. 환경변수 확인
print("DATABASE_URL:", os.getenv("DATABASE_URL"))
```

### 가상환경 문제
```bash
# 가상환경 재생성
rm -rf .venv
uv sync
```

### 테스트 실패
```bash
# 상세 로그 출력
pytest -v -s

# 특정 테스트만 실행
pytest tests/test_main.py::test_function_name
```

---

## 메모
<!-- 프로젝트 관련 중요 메모를 여기에 추가하세요 -->

-
-
-

---

## 참고 자료

**LangGraph 관련:**
- [LangGraph Official Docs](https://python.langchain.com/docs/langgraph)
- [LangGraph GitHub](https://github.com/langchain-ai/langgraph)
- [LangChain Documentation](https://python.langchain.com/)

**Python 개발:**
- [Python Docs](https://docs.python.org/3/)
- [uv Documentation](https://docs.astral.sh/uv/)
- [python-dotenv Documentation](https://github.com/theskumar/python-dotenv)
- [Pytest Documentation](https://docs.pytest.org/)

**Git Worktree:**
- [Git Worktree Documentation](https://git-scm.com/docs/git-worktree)

---

**마지막 업데이트**: 2025-11-04
