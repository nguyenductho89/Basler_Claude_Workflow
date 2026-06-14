# Notion Integration Guide

Hướng dẫn tích hợp Notion MCP để quản lý Product Backlog và Sprint Backlog cho Circle Measurement System.

---

## 1. Cài Đặt

### 1.1 Tạo Notion Integration Token

1. Truy cập: https://www.notion.so/my-integrations
2. Click **"New integration"**
3. Đặt tên: `Circle Measurement MCP`
4. Chọn workspace của bạn
5. Copy **Internal Integration Secret** (bắt đầu bằng `ntn_`)

### 1.2 Cấu Hình Environment Variable

**Windows (PowerShell):**
```powershell
$env:NOTION_TOKEN = "ntn_your_secret_token_here"
```

**Windows (Command Prompt):**
```cmd
set NOTION_TOKEN=ntn_your_secret_token_here
```

**Hoặc thêm vào system environment variables:**
1. Control Panel > System > Advanced system settings
2. Environment Variables
3. New User Variable: `NOTION_TOKEN` = `ntn_your_secret_token_here`

### 1.3 Kích Hoạt MCP Server

Restart Claude Code sau khi cấu hình. MCP server sẽ tự động khởi động.

---

## 2. Cấu Trúc Notion Databases

### 2.1 Product Backlog Database

Tạo database với các properties sau:

| Property | Type | Mô tả |
|----------|------|-------|
| **ID** | Title | ID của User Story (US-01, US-02...) |
| **Title** | Text | Mô tả ngắn gọn |
| **Role** | Select | Operator / Technician / Engineer / Manager / Supervisor |
| **Story** | Text | User Story đầy đủ |
| **Priority** | Select | High / Medium / Low |
| **Status** | Status | Not Started / In Progress / Done |
| **Sprint** | Relation | Link đến Sprint Backlog |
| **Acceptance Criteria** | Multi-select | AC-01.1, AC-01.2... |

**Dữ liệu mẫu từ PRD:**

| ID | Title | Role | Priority | Status |
|----|-------|------|----------|--------|
| US-01 | Live camera view | Operator | High | Done |
| US-02 | Auto circle detection | Operator | High | Done |
| US-03 | Visual measurement display | Operator | High | Done |
| US-04 | OK/NG color indication | Operator | High | Done |
| US-05 | Easy camera connection | Operator | High | Done |
| US-06 | Exposure control | Technician | Medium | Done |
| US-07 | Tolerance configuration | Technician | Medium | Done |
| US-08 | Calibration | Technician | Medium | Done |
| US-09 | Recipe management | Engineer | Medium | Done |
| US-10 | Statistics tracking | Engineer | Low | Done |
| US-11 | Report export | Manager | Low | Done |
| US-12 | Web Dashboard | Supervisor | Medium | Planned |

### 2.2 Sprint Backlog Database

Tạo database với các properties sau:

| Property | Type | Mô tả |
|----------|------|-------|
| **Sprint** | Title | Tên Sprint (Sprint 1, Sprint 2...) |
| **Release** | Select | MVP 1.0 / Release 1.1 / Release 1.2 / Release 2.0 / Release 2.1 |
| **Focus** | Text | Mục tiêu chính của Sprint |
| **Story Points** | Number | Tổng Story Points |
| **Status** | Status | Planned / In Progress / Done |
| **Start Date** | Date | Ngày bắt đầu |
| **End Date** | Date | Ngày kết thúc |
| **Tasks** | Relation | Link đến Sprint Tasks |

**Dữ liệu mẫu:**

| Sprint | Release | Focus | Story Points | Status |
|--------|---------|-------|--------------|--------|
| Sprint 1 | MVP 1.0 | Camera & Live View | 26 | Done |
| Sprint 2 | MVP 1.0 | Detection & Display | 30 | Done |
| Sprint 3 | Release 1.1 | Calibration & Tolerance | 27 | Done |
| Sprint 4 | Release 1.1 | Threading & History | 28 | Done |
| Sprint 5 | Release 1.2 | Recipe & Reporting | 30 | Done |
| Sprint 6 | Release 2.0 | PLC/IO Integration | 35 | Done |
| Sprint 7 | Release 2.0 | Integration & Testing | 34 | Done |
| Sprint 8 | Release 2.0 | Documentation & CI/CD | 15 | Done |
| Sprint 9 | Release 2.1 | Web Dashboard Backend | 30 | Planned |
| Sprint 10 | Release 2.1 | Web Dashboard Frontend | 25 | Planned |

### 2.3 Sprint Tasks Database

| Property | Type | Mô tả |
|----------|------|-------|
| **Task ID** | Title | ID của task (S1-01, S2-01...) |
| **Description** | Text | Mô tả task |
| **Sprint** | Relation | Link đến Sprint |
| **Priority** | Select | High / Medium / Low |
| **Story Points** | Number | Điểm effort |
| **Status** | Status | To Do / In Progress / Done |
| **Assignee** | Person | Người thực hiện |

---

## 3. Chia Sẻ Databases Với Integration

**QUAN TRỌNG:** Sau khi tạo databases, bạn cần chia sẻ với Integration:

1. Mở mỗi database trong Notion
2. Click **"..."** (menu) > **"Connections"**
3. Tìm và chọn **"Circle Measurement MCP"**
4. Lặp lại cho tất cả databases

---

## 4. Sử Dụng MCP Trong Claude Code

Sau khi cấu hình xong, Claude Code có thể:

### 4.1 Đọc Backlogs

```
"Hiển thị tất cả User Stories trong Product Backlog"
"Lấy Sprint 9 và các tasks"
"Tìm các tasks có Priority = High"
```

### 4.2 Cập Nhật Status

```
"Cập nhật US-12 sang status In Progress"
"Đánh dấu Sprint 9 là hoàn thành"
"Thêm task mới vào Sprint 10"
```

### 4.3 Tạo Mới

```
"Tạo User Story mới cho feature X"
"Thêm Sprint 11 với focus Y"
"Tạo task mới trong Sprint hiện tại"
```

---

## 5. Template Notion

### 5.1 Product Backlog Template

```
### [US-XX] Title

**Role:** [Operator/Technician/Engineer/Manager/Supervisor]

**As a** [role], **I want** [feature] **so that** [benefit].

**Priority:** [High/Medium/Low]

**Acceptance Criteria:**
- [ ] AC-XX.1: Given..., When..., Then...
- [ ] AC-XX.2: Given..., When..., Then...

**Sprint:** [Sprint X]
**Status:** [Not Started/In Progress/Done]
```

### 5.2 Sprint Task Template

```
### [SX-XX] Task Description

**Sprint:** Sprint X
**Priority:** [High/Medium/Low]
**Story Points:** X

**Description:**
[Chi tiết task cần làm]

**Acceptance Criteria:**
- [ ] Tiêu chí 1
- [ ] Tiêu chí 2

**Status:** [To Do/In Progress/Done]
```

---

## 6. Troubleshooting

### Lỗi thường gặp

| Lỗi | Nguyên nhân | Giải pháp |
|-----|-------------|-----------|
| `NOTION_TOKEN not found` | Chưa set env variable | Set NOTION_TOKEN |
| `Page not found` | Database chưa share với integration | Share database |
| `Unauthorized` | Token không hợp lệ | Tạo token mới |
| `Rate limited` | Quá nhiều requests | Chờ và thử lại |

### Kiểm Tra Kết Nối

Trong Claude Code, chạy:
```
/mcp
```

Để xem status của Notion MCP server.

---

## 7. Best Practices

1. **Sync định kỳ**: Cập nhật status sau mỗi task hoàn thành
2. **Naming convention**: Tuân thủ format ID (US-XX, SX-XX)
3. **Relations**: Luôn link tasks với Sprint và User Stories
4. **Story Points**: Estimate trước khi bắt đầu Sprint
5. **Burndown**: Theo dõi progress qua Status changes

---

**Version:** 1.0
**Created:** 2025-12-28
**Author:** Development Team
