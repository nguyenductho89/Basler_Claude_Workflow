# CI/CD Guide - Circle Measurement System

## Tổng quan

Hệ thống sử dụng **GitHub Actions** với **self-hosted runner** để tự động chạy test mỗi khi có code mới được push lên repository.

## Kiến trúc CI/CD

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   Developer     │      │     GitHub      │      │  Self-hosted    │
│   Push Code     │ ───► │    Actions      │ ───► │    Runner       │
└─────────────────┘      └─────────────────┘      └─────────────────┘
                                                          │
                                                          ▼
                                                  ┌─────────────────┐
                                                  │   Run Tests     │
                                                  │   & Coverage    │
                                                  └─────────────────┘
```

## Workflow

### Trigger
- **Push**: Chạy test trên tất cả branches
- **Pull Request**: Chạy test khi có PR vào `master` hoặc `main`

### Các bước thực thi
1. Checkout code
2. Cài đặt dependencies (`pip install -r requirements.txt`)
3. Chạy tests (`pytest tests/ -v`)
4. Tạo báo cáo coverage

## Cài đặt Self-hosted Runner

### Yêu cầu
- Windows 10/11
- Python 3.10+
- Git
- Quyền Administrator (để cài đặt auto-start)

### Bước 1: Tải và cấu hình Runner

```powershell
# Tạo thư mục runner
mkdir D:\actions-runner
cd D:\actions-runner

# Tải runner (thay version nếu cần)
Invoke-WebRequest -Uri https://github.com/actions/runner/releases/download/v2.321.0/actions-runner-win-x64-2.321.0.zip -OutFile actions-runner.zip

# Giải nén
Expand-Archive -Path actions-runner.zip -DestinationPath .

# Lấy token từ GitHub (cần gh cli đã đăng nhập)
$token = gh api repos/OWNER/REPO/actions/runners/registration-token -X POST --jq '.token'

# Cấu hình runner
.\config.cmd --url https://github.com/OWNER/REPO --token $token --name "windows-runner" --labels "self-hosted,Windows,X64" --unattended
```

### Bước 2: Cài đặt Auto-start

Chạy script với quyền Administrator:

```powershell
# Mở PowerShell as Administrator
cd D:\actions-runner
.\setup-runner.ps1
```

### Bước 3: Kiểm tra trạng thái

```powershell
# Kiểm tra process runner
Get-Process -Name "Runner.Listener"

# Kiểm tra trạng thái trên GitHub
gh api repos/OWNER/REPO/actions/runners --jq '.runners[]'
```

## Quản lý Runner

### Khởi động/Dừng Runner

```powershell
# Khởi động
Start-ScheduledTask -TaskName "GitHub Actions Runner - Basler"

# Dừng
Stop-ScheduledTask -TaskName "GitHub Actions Runner - Basler"

# Hoặc dừng process trực tiếp
Stop-Process -Name "Runner.Listener" -Force
```

### Gỡ cài đặt Runner

```powershell
cd D:\actions-runner
.\setup-runner.ps1 -Uninstall

# Xóa runner khỏi GitHub
.\config.cmd remove --token <TOKEN>
```

### Xem logs

Logs được lưu tại:
- `D:\actions-runner\_diag\` - Runner diagnostic logs
- `D:\actions-runner\_work\_temp\` - Job logs

## Workflow File

File: `.github/workflows/test.yml`

```yaml
name: Run Tests

on:
  push:
    branches: ["*"]
  pull_request:
    branches: ["master", "main"]

jobs:
  test:
    runs-on: self-hosted

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run tests
        run: |
          pytest tests/ -v --tb=short

      - name: Run tests with coverage
        run: |
          pytest tests/ --cov=src --cov-report=term-missing
```

## Xử lý sự cố

### Runner offline

1. Kiểm tra process đang chạy:
   ```powershell
   Get-Process -Name "Runner.Listener" -ErrorAction SilentlyContinue
   ```

2. Nếu không có, khởi động lại:
   ```powershell
   cd D:\actions-runner
   .\run.cmd
   ```

3. Kiểm tra network connectivity đến GitHub

### Tests fail

1. Xem logs trên GitHub Actions tab
2. Chạy tests locally để debug:
   ```bash
   pytest tests/ -v --tb=long
   ```

### Dependency issues

1. Xóa cache và cài lại:
   ```bash
   pip cache purge
   pip install -r requirements.txt --force-reinstall
   ```

## Thêm Runner mới

Nếu cần thêm runner trên máy khác:

1. Vào repo → Settings → Actions → Runners → New self-hosted runner
2. Làm theo hướng dẫn trên GitHub
3. Thêm labels phù hợp (ví dụ: `gpu`, `high-memory`)

## Best Practices

1. **Không commit secrets** - Dùng GitHub Secrets cho API keys, passwords
2. **Giữ runner cập nhật** - Update runner khi có version mới
3. **Monitor disk space** - Dọn dẹp `_work` folder định kỳ
4. **Backup config** - Lưu `.runner` và `.credentials` files

## Links

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Self-hosted runners](https://docs.github.com/en/actions/hosting-your-own-runners)
- [Workflow syntax](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
