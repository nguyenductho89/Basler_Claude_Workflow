# CI/CD Guide - Circle Measurement System

## Tổng quan

Hệ thống sử dụng **GitHub Actions** với **self-hosted runner** để tự động hóa quy trình phát triển:
- Lint checking (Ruff)
- Type checking (Mypy)
- Unit & Integration tests (Pytest)
- Code coverage (Codecov)
- Security updates (Dependabot)

## Kiến trúc CI/CD

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   Developer     │      │     GitHub      │      │  Self-hosted    │
│   Push Code     │ ───► │    Actions      │ ───► │    Runner       │
└─────────────────┘      └─────────────────┘      └─────────────────┘
        │                                                 │
        │ Pre-commit hooks                               │
        │ (ruff, mypy)                                   ▼
        │                                        ┌───────────────────┐
        ▼                                        │  lint (parallel)  │
┌─────────────────┐                              │  typecheck        │
│  Local Check    │                              └─────────┬─────────┘
│  Pass? ───────► │                                        │
└─────────────────┘                                        ▼
                                                 ┌───────────────────┐
                                                 │   test + coverage │
                                                 └─────────┬─────────┘
                                                           │
                                                           ▼
                                                 ┌───────────────────┐
                                                 │  Upload Codecov   │
                                                 └───────────────────┘
```

## Badges

[![Build Status](https://github.com/nguyenductho89/Basler_Claude_Workflow/actions/workflows/test.yml/badge.svg)](https://github.com/nguyenductho89/Basler_Claude_Workflow/actions)
[![codecov](https://codecov.io/gh/nguyenductho89/Basler_Claude_Workflow/graph/badge.svg)](https://codecov.io/gh/nguyenductho89/Basler_Claude_Workflow)

---

## 1. Workflow Pipeline

### File: `.github/workflows/test.yml`

```yaml
name: Run Tests

on:
  push:
    branches: ["*"]
  pull_request:
    branches: ["master", "main"]
  workflow_dispatch:

env:
  PYTHON_PATH: C:\Users\Admin\AppData\Local\Programs\Python\Python311\python.exe

jobs:
  lint:
    runs-on: self-hosted
    steps:
      - uses: actions/checkout@v4
      - name: Run Ruff linter
        run: ${{ env.PYTHON_PATH }} -m ruff check src/ tests/
      - name: Run Ruff formatter check
        run: ${{ env.PYTHON_PATH }} -m ruff format src/ tests/ --check

  typecheck:
    runs-on: self-hosted
    steps:
      - uses: actions/checkout@v4
      - name: Run mypy
        run: ${{ env.PYTHON_PATH }} -m mypy src/ --config-file mypy.ini

  test:
    runs-on: self-hosted
    needs: [lint, typecheck]
    steps:
      - uses: actions/checkout@v4
      - name: Install dependencies
        run: ${{ env.PYTHON_PATH }} -m pip install -r requirements.txt
      - name: Run tests with coverage
        run: ${{ env.PYTHON_PATH }} -m pytest tests/ -v --cov=src --cov-report=xml
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        env:
          CODECOV_TOKEN: ${{ secrets.CODECOV_TOKEN }}
```

### Trigger Events
| Event | Mô tả |
|-------|-------|
| `push` | Chạy khi push lên bất kỳ branch nào |
| `pull_request` | Chạy khi tạo/update PR vào master/main |
| `workflow_dispatch` | Chạy thủ công từ GitHub UI |

### Jobs Flow
```
lint ──────┐
           ├──► test ──► Upload Coverage
typecheck ─┘
```

---

## 2. Pre-commit Hooks

### File: `.pre-commit-config.yaml`

Pre-commit hooks chạy tự động trước mỗi commit.

### Cài đặt

```powershell
# Cài đặt pre-commit
pip install pre-commit

# Cài đặt hooks
pre-commit install

# Hoặc chạy script setup
.\scripts\setup-dev.ps1
```

### Hooks được cấu hình

| Hook | Mục đích |
|------|----------|
| `ruff` | Lint Python code với auto-fix |
| `ruff-format` | Format code tự động |
| `mypy` | Type checking |
| `trailing-whitespace` | Xóa khoảng trắng cuối dòng |
| `end-of-file-fixer` | Fix end of file |
| `check-yaml` | Validate YAML syntax |
| `check-json` | Validate JSON syntax |
| `check-merge-conflict` | Phát hiện merge conflict markers |
| `debug-statements` | Cảnh báo print/breakpoint |
| `check-added-large-files` | Cảnh báo file > 1MB |

### Chạy thủ công

```powershell
# Chạy tất cả hooks
pre-commit run --all-files

# Chạy riêng từng hook
pre-commit run ruff
pre-commit run mypy
pre-commit run ruff-format
```

---

## 3. Branch Protection

### Rules cho `master` branch

| Rule | Setting |
|------|---------|
| Require pull request | ✅ Enabled |
| Required approvals | 1 |
| Dismiss stale reviews | ✅ Enabled |
| Require code owner review | ✅ Enabled |
| Required status checks | `lint`, `typecheck`, `test` |
| Require branch up to date | ✅ Enabled |
| Allow force pushes | ❌ Disabled |
| Allow deletions | ❌ Disabled |

### Workflow cho Contributors

```powershell
# 1. Tạo feature branch
git checkout -b feature/my-feature

# 2. Code và commit (pre-commit hooks sẽ chạy)
git add .
git commit -m "Add my feature"

# 3. Push branch
git push -u origin feature/my-feature

# 4. Tạo Pull Request
gh pr create --title "Add my feature" --body "Description"

# 5. Đợi CI pass và approval, sau đó merge
```

---

## 4. CODEOWNERS

### File: `.github/CODEOWNERS`

Tự động request review từ code owners khi có PR thay đổi files.

| Path | Owner |
|------|-------|
| `*` (default) | @nguyenductho89 |
| `/src/domain/` | @nguyenductho89 |
| `/src/services/` | @nguyenductho89 |
| `/src/ui/` | @nguyenductho89 |
| `/tests/` | @nguyenductho89 |
| `/.github/` | @nguyenductho89 |

---

## 5. Issue & PR Templates

### Issue Templates

| Template | Label | Mô tả |
|----------|-------|-------|
| 🐛 Bug Report | `bug` | Báo cáo lỗi |
| ✨ Feature Request | `enhancement` | Đề xuất tính năng |
| 📋 Task | `task` | Công việc cần làm |

### PR Template

PR template tự động được load khi tạo PR mới, bao gồm:
- Description
- Type of Change
- Related Issues
- Changes Made
- Test Plan
- Checklist

---

## 6. Labels

### Priority Labels
| Label | Color | Mô tả |
|-------|-------|-------|
| `priority: critical` | 🔴 | Cần xử lý ngay |
| `priority: high` | 🟠 | Ưu tiên cao |
| `priority: medium` | 🟡 | Ưu tiên trung bình |
| `priority: low` | 🟢 | Ưu tiên thấp |

### Status Labels
| Label | Color | Mô tả |
|-------|-------|-------|
| `status: ready` | 🟢 | Sẵn sàng implement |
| `status: in progress` | 🔵 | Đang xử lý |
| `status: needs review` | 🟡 | Cần review |
| `status: blocked` | 🔴 | Bị block |
| `status: on hold` | ⚪ | Tạm dừng |

### Component Labels
| Label | Mô tả |
|-------|-------|
| `component: camera` | Camera/Basler |
| `component: detection` | Circle detection |
| `component: ui` | User interface |
| `component: io` | PLC/IO |
| `component: calibration` | Calibration |
| `component: recipe` | Recipe management |

### Size Labels
| Label | Estimate |
|-------|----------|
| `size: XS` | < 1 giờ |
| `size: S` | 1-4 giờ |
| `size: M` | 1-2 ngày |
| `size: L` | 3-5 ngày |
| `size: XL` | > 1 tuần |

---

## 7. Dependabot

### File: `.github/dependabot.yml`

Tự động scan và tạo PR để update dependencies.

| Ecosystem | Schedule | Labels |
|-----------|----------|--------|
| pip (Python) | Weekly, Monday 9 AM | `type: security`, `priority: high` |
| github-actions | Weekly, Monday 9 AM | `type: ci/cd`, `priority: medium` |

### Features
- ✅ Vulnerability alerts
- ✅ Automated security fixes
- ✅ Grouped minor/patch updates
- ✅ Auto-assign reviewers

### Xem alerts
```
https://github.com/nguyenductho89/Basler_Claude_Workflow/security/dependabot
```

---

## 8. Self-hosted Runner

### Yêu cầu
- Windows 10/11
- Python 3.11
- Git
- Quyền Administrator

### Cài đặt Runner

```powershell
# Tạo thư mục
mkdir D:\actions-runner
cd D:\actions-runner

# Tải runner
$version = "2.321.0"
Invoke-WebRequest -Uri "https://github.com/actions/runner/releases/download/v$version/actions-runner-win-x64-$version.zip" -OutFile actions-runner.zip

# Giải nén
Expand-Archive -Path actions-runner.zip -DestinationPath .

# Lấy token
$token = gh api repos/nguyenductho89/Basler_Claude_Workflow/actions/runners/registration-token -X POST --jq '.token'

# Cấu hình
.\config.cmd --url https://github.com/nguyenductho89/Basler_Claude_Workflow --token $token --name "windows-runner" --labels "self-hosted,Windows,X64" --unattended
```

### Auto-start với Task Scheduler

```powershell
# Chạy với quyền Administrator
.\setup-runner.ps1
```

### Quản lý Runner

```powershell
# Khởi động
Start-ScheduledTask -TaskName "GitHub Actions Runner - Basler"

# Dừng
Stop-ScheduledTask -TaskName "GitHub Actions Runner - Basler"

# Kiểm tra trạng thái
Get-Process -Name "Runner.Listener"

# Xem trên GitHub
gh api repos/nguyenductho89/Basler_Claude_Workflow/actions/runners --jq '.runners[]'
```

### Logs

```
D:\actions-runner\_diag\        # Runner diagnostic logs
D:\actions-runner\_work\_temp\  # Job logs
```

---

## 9. Lint & Type Check Configuration

### Ruff Configuration (`ruff.toml`)

```toml
target-version = "py311"
line-length = 120

[lint]
select = ["E", "F", "W"]
ignore = ["E501", "E402", "E712", "E722", "F401", "F403", "F541", "F841"]
```

### Mypy Configuration (`mypy.ini`)

```ini
[mypy]
python_version = 3.11
files = src/
ignore_missing_imports = True
strict = False
show_error_codes = True

[mypy-src.ui.*]
ignore_errors = True

[mypy-src.services.camera_service]
ignore_errors = True
```

---

## 10. Troubleshooting

### Runner offline

```powershell
# Kiểm tra process
Get-Process -Name "Runner.Listener" -ErrorAction SilentlyContinue

# Khởi động lại
cd D:\actions-runner
.\run.cmd
```

### Pre-commit hooks fail

```powershell
# Xem lỗi chi tiết
pre-commit run --all-files -v

# Fix tự động với ruff
ruff check src/ --fix
ruff format src/
```

### Tests fail

```powershell
# Chạy tests locally
pytest tests/ -v --tb=long

# Chạy test cụ thể
pytest tests/unit/services/test_detector_service.py -v
```

### Dependency issues

```powershell
# Xóa cache và cài lại
pip cache purge
pip install -r requirements.txt --force-reinstall
```

---

## 11. Quick Reference

### Commands

```powershell
# Lint
ruff check src/ tests/
ruff check src/ --fix

# Format
ruff format src/ tests/

# Type check
mypy src/ --config-file mypy.ini

# Test
pytest tests/ -v
pytest tests/ --cov=src --cov-report=html

# Pre-commit
pre-commit run --all-files
```

### Links

| Resource | URL |
|----------|-----|
| Repository | https://github.com/nguyenductho89/Basler_Claude_Workflow |
| Actions | https://github.com/nguyenductho89/Basler_Claude_Workflow/actions |
| Coverage | https://codecov.io/gh/nguyenductho89/Basler_Claude_Workflow |
| Security | https://github.com/nguyenductho89/Basler_Claude_Workflow/security |
| Issues | https://github.com/nguyenductho89/Basler_Claude_Workflow/issues |

### GitHub Actions Docs
- [Workflow syntax](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
- [Self-hosted runners](https://docs.github.com/en/actions/hosting-your-own-runners)
- [Branch protection](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches)
- [CODEOWNERS](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)
- [Dependabot](https://docs.github.com/en/code-security/dependabot)
