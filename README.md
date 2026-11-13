<p align="center">
  <a href="https://github.com/mizhexiaoxiao/vue-fastapi-admin">
    <img alt="Vue FastAPI Admin Logo" width="200" src="https://github.com/mizhexiaoxiao/vue-fastapi-admin/blob/main/deploy/sample-picture/logo.svg">
  </a>
</p>

<h1 align="center">vue-fastapi-admin</h1>

[English](./README-en.md) | 简体中文

基于 FastAPI + Vue3 + Naive UI 的现代化前后端分离开发平台，融合了 RBAC 权限管理、动态路由和 JWT 鉴权，助力中小型应用快速搭建，也可用于学习参考。

### 课堂 AI 集成（D，开发中）

- 正式设计与实验要求对照：[docs/AI_INTEGRATION.md](./docs/AI_INTEGRATION.md)。
- 独立模型适配与验证：[ai-service/README.md](./ai-service/README.md)。
- 当前默认课堂设备独立采集；保留以后与学生端同机部署的扩展，设备服务身份与学生登录身份仍分离。
- 普通用户 `/api/v1/emoji` 仅允许手动来源；AI 设备/任务/可靠入库路由尚未上线，不以用户 JWT 冒充服务。

### 特性
- **最流行技术栈**：基于 Python 3.11 和 FastAPI 高性能异步框架，结合 Vue3 和 Vite 等前沿技术进行开发，同时使用高效的 npm 包管理器 pnpm。
- **代码规范**：项目内置丰富的规范插件，确保代码质量和一致性，有效提高团队协作效率。
- **动态路由**：后端动态路由，结合 RBAC（Role-Based Access Control）权限模型，提供精细的菜单路由控制。
- **JWT鉴权**：使用 JSON Web Token（JWT）进行身份验证和授权，增强应用的安全性。
- **细粒度权限控制**：实现按钮和接口级别的权限控制，确保不同用户或角色在界面操作和接口访问时具有不同的权限限制。

### 在线预览（原框架参考，非本项目业务演示）
- [http://47.111.145.81:3000](http://47.111.145.81:3000)
- username: admin
- password: 123456

### 登录页

![image](https://github.com/mizhexiaoxiao/vue-fastapi-admin/blob/main/deploy/sample-picture/login.jpg)
### 工作台

![image](https://github.com/mizhexiaoxiao/vue-fastapi-admin/blob/main/deploy/sample-picture/workbench.jpg)

### 用户管理

![image](https://github.com/mizhexiaoxiao/vue-fastapi-admin/blob/main/deploy/sample-picture/user.jpg)
### 角色管理

![image](https://github.com/mizhexiaoxiao/vue-fastapi-admin/blob/main/deploy/sample-picture/role.jpg)

### 菜单管理

![image](https://github.com/mizhexiaoxiao/vue-fastapi-admin/blob/main/deploy/sample-picture/menu.jpg)

### API管理

![image](https://github.com/mizhexiaoxiao/vue-fastapi-admin/blob/main/deploy/sample-picture/api.jpg)

## 本地快速运行（当前项目，Windows PowerShell）

新用户按本节启动即可体验 A/B/C 业务。使用 SQLite，无需安装 MySQL；上方在线预览是原框架参考，不是本项目。

### 1. 准备环境并取得代码

- Python 3.11，安装时启用 PATH / Python Launcher。
- Node.js 20（本项目要求至少 Node 18.8；pnpm 9 要求至少 Node 18.12）。
- Git。终端路径含空格时使用引号。

```powershell
git clone https://github.com/xzhnb666/emoji-classroom-final.git
cd emoji-classroom-final
py -3.11 --version
node --version
npm --version
```

已经下载或克隆项目的用户直接进入自己的仓库根目录，不必重复 clone。B 功能若还在开发分支，先获取包含 B 提交的版本；本地未提交文件不会自动包含在别人克隆的仓库中。

### 2. 安装后端依赖

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

无需激活虚拟环境。Windows 请使用 requirements.txt，避免当前 pyproject.toml 中 uvloop 的平台兼容问题。

### 3. 配置本地数据库

第一次使用时复制配置模板；已有 .env 时只编辑，不能覆盖原有配置：

```powershell
if (!(Test-Path .env)) { Copy-Item .env.example .env }
notepad .env
```

将 .env 中 DB_ENGINE 改成下面一行，其余 MySQL 字段在 SQLite 模式下不使用：

```ini
DB_ENGINE=sqlite
```

建议在本机生成随机密钥，再作为 SECRET_KEY 的值填写到 .env，不要提交该文件：

```powershell
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(48))"
```

.env 由仓库根目录加载，务必从根目录启动后端。SQLite 数据文件是根目录 db.sqlite3。首次启动会创建表、管理员、菜单/API 等数据，可能生成本地迁移文件；无需手工执行 aerich init/migrate/upgrade。已有数据库先备份，不要删除数据库或迁移目录来处理启动错误。B 本阶段没有新增数据模型或数据库结构变更。

### 4. 启动后端（终端一）

```powershell
.\.venv\Scripts\python.exe run.py
```

看到 Application startup complete 后，打开 http://localhost:9999/docs，确认 Swagger 能加载。终端保持运行。如果提示端口占用，先确认是否已有本项目服务，不要同时启动两份后端。

### 5. 安装并启动前端（终端二）

在另一个终端进入同一仓库，然后执行：

```powershell
cd web
npm install --global pnpm@9
pnpm install --frozen-lockfile
pnpm dev
```

仓库有 pnpm-lock.yaml（v9），不要混用 npm install 生成另一份依赖锁。默认打开 http://localhost:3100；若 Vite 提示其他端口，以终端为准。后端 9999 是 API，不是前端网页。

前端所需配置已在 web/.env、web/.env.development 中：VITE_PORT=3100、VITE_USE_PROXY=true、VITE_BASE_API=/api/v1。web/build/constant.js 把 /api/v1 代理到 http://127.0.0.1:9999。如后端换端口，须同步改代理并重启 Vite。若克隆版本缺少前端环境文件，在 web/.env 填入上述配置以及 VITE_PUBLIC_PATH=/、VITE_USE_HASH=false 后重启。

### 6. 首次登录与关闭

全新空库由 init_superuser 创建开发管理员，用户名 admin，初始密码 123456（公开的初始化值，不是部署凭证）。先用它进入管理端并修改密码；已有库不会重置为该值。学生请从公开注册入口注册，不要用管理员作为学生/教师演示账号。

前端和后端终端分别按 Ctrl+C 退出即可，不会删除 SQLite 数据。再次运行时只需执行步骤 4、5 中的启动命令，不必重装依赖。修改后端 .env 后重启后端；修改前端环境或代理后重启前端。

MySQL 用户可参考下方 A 模块数据库说明；本地快速体验无需执行。

### 常见启动问题

| 现象 | 检查方法 |
| --- | --- |
| py / node / pnpm 找不到 | 检查安装和 PATH，重新打开终端；pnpm 安装失败时检查 npm 全局目录权限 |
| Windows 安装 uvloop 失败 | 使用 requirements.txt，不用当前 pyproject.toml 直接安装 |
| 无法连接 MySQL | 快速体验应确认 DB_ENGINE=sqlite；MySQL 模式检查服务、账号、库名、字符集 |
| 登录提示网络错误或代理 ECONNREFUSED | 确认后端已完成启动、9999/docs 能访问、前端代理目标正确 |
| 默认管理员登录失败 | 仅空库自动创建默认账号；确认当前连接的库，不能靠删库重置密码 |
| 注册成功但课堂为空 | 需要管理员给该学生排课，注册不会自动加入课堂 |
| 分配教师后仍无课程 | 角色和课程归属分别配置；创建课程时填写该教师真实用户 ID，退出重登 |
| 403 / 无权限 | 核对账号角色、课程归属与排课，不要给普通测试用户开启超级管理员绕过 |
| 创建课堂日期校验失败 | 使用当前日期选择器，结束晚于开始；接口传 YYYY-MM-DDTHH:mm:ss，不拼接毫秒时间戳 |
| Aerich / 表已存在错误 | 保存完整异常，核对当前 DB_ENGINE、数据库和迁移历史，由 A 处理；不要清库或删除迁移目录 |

### 目录说明

```
├── app                   // 应用程序目录
│   ├── api               // API接口目录
│   │   └── v1            // 版本1的API接口
│   │       ├── apis      // API相关接口
│   │       ├── base      // 基础信息接口
│   │       ├── menus     // 菜单相关接口
│   │       ├── roles     // 角色相关接口
│   │       └── users     // 用户相关接口
│   ├── controllers       // 控制器目录
│   ├── core              // 核心功能模块
│   ├── log               // 日志目录
│   ├── models            // 数据模型目录
│   ├── schemas           // 数据模式/结构定义
│   ├── settings          // 配置设置目录
│   └── utils             // 工具类目录
├── deploy                // 部署相关目录
│   └── sample-picture    // 示例图片目录
└── web                   // 前端网页目录
    ├── build             // 构建脚本和配置目录
    │   ├── config        // 构建配置
    │   ├── plugin        // 构建插件
    │   └── script        // 构建脚本
    ├── public            // 公共资源目录
    │   └── resource      // 公共资源文件
    ├── settings          // 前端项目配置
    └── src               // 源代码目录
        ├── api           // API接口定义
        ├── assets        // 静态资源目录
        │   ├── images    // 图片资源
        │   ├── js        // JavaScript文件
        │   └── svg       // SVG矢量图文件
        ├── components    // 组件目录
        │   ├── common    // 通用组件
        │   ├── icon      // 图标组件
        │   ├── page      // 页面组件
        │   ├── query-bar // 查询栏组件
        │   └── table     // 表格组件
        ├── composables   // 可组合式功能块
        ├── directives    // 指令目录
        ├── layout        // 布局目录
        │   └── components // 布局组件
        ├── router        // 路由目录
        │   ├── guard     // 路由守卫
        │   └── routes    // 路由定义
        ├── store         // 状态管理(pinia)
        │   └── modules   // 状态模块
        ├── styles        // 样式文件目录
        ├── utils         // 工具类目录
        │   ├── auth      // 认证相关工具
        │   ├── common    // 通用工具
        │   ├── http      // 封装axios
        │   └── storage   // 封装localStorage和sessionStorage
        └── views         // 视图/页面目录
            ├── error-page // 错误页面
            ├── login      // 登录页面
            ├── profile    // 个人资料页面
            ├── system     // 系统管理页面
            └── workbench  // 工作台页面
```

## 情绪课堂模块（A）：后端与数据库

本仓库在 vue-fastapi-admin 基础上新增课堂情绪业务。A 模块负责课程、课堂会话、排课和 Emoji 记录的数据模型、Schema、控制器、数据库迁移以及数据归属校验。

### 数据模型

| 表名 | 说明 | 关键约束 |
| --- | --- | --- |
| `course` | 课程，由教师负责 | `(name, teacher_id)` 唯一 |
| `class_session` | 课堂会话，属于某门课程 | `end_time > start_time` |
| `schedule_user` | 课堂排课关系 | `(session_id, user_id)` 唯一 |
| `emoji_record` | 手动或 AI 生成的情绪记录 | `source` 为 `MANUAL`/`AI`，AI 必须带 0~1 的 `confidence`，手动不能带 `confidence` |

`EmojiType` 支持：`HAPPY`、`SAD`、`ANGRY`、`SURPRISED`、`NEUTRAL`。

### API 接口（前缀 `/api/v1`）

除登录外，以下接口都需要登录，鉴权信息放在请求头 `token`（与前端 Axios 拦截器一致）。普通接口使用 `DependAuth`，并在控制器层做教师/学生归属校验。

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/api/v1/courses` | 查询课程列表 |
| POST | `/api/v1/courses` | 创建课程 |
| PUT | `/api/v1/courses/{course_id}` | 更新课程 |
| DELETE | `/api/v1/courses/{course_id}` | 删除课程 |
| GET | `/api/v1/sessions` | 查询课堂会话列表 |
| POST | `/api/v1/sessions` | 创建课堂会话 |
| PUT | `/api/v1/sessions/{session_id}` | 更新课堂会话 |
| DELETE | `/api/v1/sessions/{session_id}` | 删除课堂会话 |
| POST | `/api/v1/sessions/{session_id}/schedule` | 安排用户进入课堂 |
| DELETE | `/api/v1/sessions/{session_id}/schedule/{user_id}` | 取消课堂安排 |
| POST | `/api/v1/emoji` | 提交一条 Emoji 记录 |
| GET | `/api/v1/emoji/history` | 查询 Emoji 历史 |
| GET | `/api/v1/emoji/statistics` | 按类型汇总统计 |

统一响应格式为 `{code, msg, data}`，分页接口额外带 `total`、`page`、`page_size`。

认证接口（公开，不需要 `token`）：`POST /api/v1/base/register`（注册学生）、`POST /api/v1/base/register-teacher`（注册教师）、`POST /api/v1/base/access_token`（登录）。登录后修改密码使用 `POST /api/v1/base/update_password`。注册与修改密码的密码须为 8~128 位，且同时包含字母和数字，服务端会拒绝弱密码。

路由模块已导出并在 `app/api/v1/__init__.py` 注册。以下为当前注册方式示意，无需新用户重复修改：

```python
from .courses import courses_router
from .emoji import emoji_router
from .sessions import sessions_router

v1_router.include_router(courses_router)
v1_router.include_router(sessions_router)
v1_router.include_router(emoji_router)
```

#### 请求/响应示例

创建课程：

```json
POST /api/v1/courses
Content-Type: application/json
token: <登录后的 JWT>

{
  "name": "数据结构",
  "teacher_id": 1,
  "description": "计算机基础课"
}
```

```json
{
  "code": 200,
  "msg": "OK",
  "data": {
    "id": 1,
    "name": "数据结构",
    "teacher_id": 1,
    "description": "计算机基础课",
    "created_at": "2026-11-03 13:00:00",
    "updated_at": "2026-11-03 13:00:00"
  }
}
```

创建课堂会话：

```json
POST /api/v1/sessions
token: <登录后的 JWT>

{
  "course_id": 1,
  "start_time": "2026-11-03T10:00:00",
  "end_time": "2026-11-03T11:00:00",
  "classroom": "A101",
  "class_name": "计科2301"
}
```

```json
{
  "code": 200,
  "msg": "OK",
  "data": {
    "id": 1,
    "course_id": 1,
    "start_time": "2026-11-03 10:00:00",
    "end_time": "2026-11-03 11:00:00",
    "classroom": "A101",
    "class_name": "计科2301",
    "created_at": "2026-11-03 13:00:00",
    "updated_at": "2026-11-03 13:00:00"
  }
}
```

安排学生进入课堂：

```json
POST /api/v1/sessions/1/schedule
token: <登录后的 JWT>

{
  "user_id": 2
}
```

提交手动 Emoji（学生必须已被安排进该课堂）：

```json
POST /api/v1/emoji
token: <登录后的 JWT>

{
  "user_id": 2,
  "session_id": 1,
  "emoji_type": "HAPPY",
  "source": "MANUAL"
}
```

```json
{
  "code": 200,
  "msg": "OK",
  "data": {
    "id": 1,
    "user_id": 2,
    "session_id": 1,
    "emoji_type": "HAPPY",
    "timestamp": "2026-11-03 13:05:00",
    "source": "MANUAL",
    "confidence": null,
    "device_source": null
  }
}
```

提交 AI Emoji 的数据契约（由 `EmojiCreate` 校验：AI 记录必须带 `source=AI` 和 0~1 的 `confidence`，`user_id` 可省略）：

```json
{
  "session_id": 1,
  "emoji_type": "HAPPY",
  "source": "AI",
  "confidence": 0.88,
  "device_source": "camera-01"
}
```

AI 服务的专用入库接口为 `POST /api/v1/ai/emoji-results`（成员 D，使用独立 `AI_SERVICE_TOKEN`），不在 A 模块范围。

查询课堂 Emoji 统计：

```json
GET /api/v1/emoji/statistics?session_id=1
token: <登录后的 JWT>
```

```json
{
  "code": 200,
  "msg": "OK",
  "data": [
    {"emoji_type": "HAPPY", "count": 2, "percentage": 66.67},
    {"emoji_type": "NEUTRAL", "count": 1, "percentage": 33.33}
  ]
}
```

### 数据库初始化与迁移

#### 方式一：MySQL（推荐用于联调/部署）

1. 创建数据库（必须使用 `utf8mb4`，以支持中文和 Emoji）：

```sql
CREATE DATABASE emoji_classroom DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. 执行建表脚本（MySQL 8.0.16 及以上，包含课程/课堂/排课/Emoji 业务表及认证、RBAC 前置表）：

```sh
mysql -u root -p emoji_classroom < database/mysql_schema.sql
```

3. 复制 `.env.example` 为 `.env`，修改数据库连接：

```sh
cp .env.example .env
# 编辑 .env，设置 DB_ENGINE=mysql、MYSQL_HOST、MYSQL_PORT、MYSQL_USER、MYSQL_PASSWORD、MYSQL_DATABASE=emoji_classroom
```

4. 启动后应用会自动执行初始化（`init_db`），并在缺少角色/菜单/API 数据时补齐。

#### 方式二：SQLite（本地快速验证）

在 `.env` 中设置：

```ini
DB_ENGINE=sqlite
```

应用会使用 `db.sqlite3`。启动时 `init_db` 会通过 Aerich 执行 `migrations/` 下的迁移并升级。

#### Aerich 迁移流程（模型变更后）

```sh
# 初始化（仅首次）
aerich init -t app.settings.TORTOISE_ORM

# 生成迁移文件并应用
aerich migrate --name classroom_emotion_models
aerich upgrade
```

注意：`migrations/` 目录中的历史迁移是 SQLite 方言 SQL；如果使用 MySQL，请直接执行 `database/mysql_schema.sql`，或在 MySQL 连接下用 Aerich 重新生成迁移。

### 运行测试

```sh
# 安装测试依赖（已写入 requirements.txt / pyproject.toml）
pip install -r requirements.txt

# 运行 A 模块单元测试和接口测试
pytest
```

测试说明：

- `tests/test_classroom_schemas.py`：A 模块 Schema 单元测试，覆盖课程名称、课堂时间区间、手动/AI Emoji 的置信度约束。
- `tests/test_classroom_api.py`：A 模块接口测试，覆盖课程增删查、课堂会话创建与时间校验、排课、手动 Emoji 提交、来源约束以及教师/学生数据归属校验。
- `tests/test_classroom_admin.py`：C 模块接口测试，覆盖管理端统计、实时看板、CSV 导出（含注入防护）、Emoji 列表、排课列表以及学生越权拦截。

## 情绪课堂模块（B）：学生与教师客户端

基于现有 Vue 3、JavaScript、Naive UI 和 Axios 实现，先按上方“本地快速运行”启动前后端。

| 身份 | 功能 | 页面 |
| --- | --- | --- |
| 未登录 | 学生/教师注册、登录 | /register、/login |
| 学生 | 查看已排课堂、手动提交 Emoji | /student/classroom |
| 学生 | 个人历史、课堂/时间筛选、分页 | /student/history |
| 教师 | 所授课程和课堂列表 | /teacher/classroom |
| 教师 | 课堂历史、筛选、分页、情绪数量与占比 | /teacher/classroom/detail?session_id=实际课堂ID |
| 学生/教师 | 修改密码、只读个人资料 | 头像菜单 → 个人资料 |

### 使用步骤

1. 教师可从登录页公开注册（选择“教师”身份），服务端自动分配 TEACHER 角色；也可以在用户管理由管理员创建教师并分配角色，不要开启超级管理员。
2. 学生从登录页公开注册（选择“学生”身份），填写用户名、邮箱及两次相同密码，服务端自动分配 STUDENT。密码须为 8～128 位，且同时包含字母和数字。
3. 管理员创建课程，授课教师填写该教师的真实用户 ID；创建课堂，填写班级、教室及起止时间。
4. 在课堂排课入口加入学生的真实用户 ID。角色分配不等于排课，用户 ID 可从用户表查看。
5. 学生登录 → 我的课堂 → 选择课堂和 Emoji → 提交 → 查看个人历史。
6. 对应教师登录 → 选择课程 → 打开课堂 → 查看历史和基础统计。两种角色均可从头像菜单修改密码；双角色可切换入口。

情绪为 HAPPY 😀、SAD 😢、ANGRY 😠、SURPRISED 😮、NEUTRAL 😐。手动来源固定 MANUAL，提交中禁止重复点击；结果不确定时先核对历史，再决定是否重试。学生没有匿名提交入口。

业务时间统一北京时间（UTC+8）。筛选修改后点击查询生效，起止时间均包含；历史使用服务端分页，统计覆盖完整筛选范围，不随翻页改变。统计按记录条数计算，默认包含 MANUAL+AI，缺失类型补零。

管理员和教师均不能给教师账号排课（包括双角色及已有授课课程的账号）；排课应选择学生用户 ID。已有排课不会自动删除。

课程和课堂会话删除仅限管理员：教师界面不显示删除按钮，直接调用删除接口也返回 403。

### 测试和限制

仓库根目录执行后端测试（独立 SQLite，不修改业务库）：

```powershell
.\.venv\Scripts\python.exe -m pytest -q --basetemp=.venv/b-local-tests
```

web 目录执行：

```powershell
pnpm run test:auth
node tests/session-date.test.mjs
pnpm run build
```


## 课堂情绪模块（C）：管理端看板与统计

C 模块负责管理端：管理员/教师查看 Emoji 数据、多维统计、实时课堂情绪看板、CSV 导出，以及课堂排课管理页面。

### 后端接口（前缀 `/api/v1`）

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/emoji` | 分页查询 Emoji 记录（管理员看全部，教师看自己的课堂） |
| GET | `/emoji/export` | 导出 Emoji 记录 CSV（含 UTF-8 BOM 与 CSV 注入防护） |
| GET | `/statistics` | 多维统计：按情绪类型、课程、班级、来源、按天/按小时聚合 |
| GET | `/dashboard/realtime?session_id=` | 实时课堂情绪看板 |
| GET | `/sessions/{session_id}/schedule` | 查询课堂已安排的用户列表 |

上述接口均需登录（`token` 请求头）。统计与看板接口仅管理员和教师可访问，学生访问返回 403；教师只能查看自己所授课程的数据。

### 前端管理端页面

菜单「课堂情绪管理」下新增：

| 菜单 | 路径 | 说明 |
| --- | --- | --- |
| 实时看板 | `/classroom/dashboard` | 选择课堂查看实时情绪汇总、分布与时间线，支持自动刷新 |
| 多维统计 | `/classroom/statistics` | 按课程/班级/时间筛选，展示类型/课程/班级/来源分布与趋势 |
| 课程管理 | `/classroom/course` | 课程增删改查 |
| 课堂会话 | `/classroom/session` | 课堂会话增删改查与排课管理 |
| Emoji 数据 | `/classroom/emoji` | Emoji 记录查询与 CSV 导出 |

菜单在应用启动时通过 `init_classroom_menus` 幂等补齐（新老数据库都会自动创建），无需手动插入。

## AI 服务集成（D）

**2026-11-13 产品方案更新：仅学生网页采集，AI结果强制匿名，不保留公共摄像头入口。**
学生电脑只需普通摄像头和浏览器，Python/模型安装在独立服务器上。
网页采集会话、帧入口及学生控件尚待交付；当前已验证的节点控制不能称为免安装网页采集。
接入方案、操作边界、采样次数与防重复规则见 `docs/AI_BROWSER_CAPTURE.md`。
下列节点能力是此前首版实现记录，不是新版学生操作路径。

独立教室采集节点 + 原课堂任务控制 + 同一业务库/看板/统计/CSV。
支持固定 DeepFace emotion-only 标准 CPU profile 和 YuNet + MobileFaceNet 轻量 profile；
不把两套模型塞入业务后端，不以 fake 替代缺失模型。

- 管理员：「课堂情绪管理 / AI采集设备」，注册、分配教师、一次性签发/轮换/撤销凭证。
- 教师：原课堂详情内「AI课堂采集」，创建预检、开始/暂停/停止；原实时看板亦可控制。
- AI 记录默认匿名，仅上传元数据，不保存课堂图片/人脸裁剪；学生手动链路保持独立。
- 单设备单任务、45秒租约、持久 outbox、事件幂等、严格请求限量、版本追溯。
- 统计使用数据库聚合；CSV 流式 keyset，最多100000行，原列/BOM/注入防护保持。

阅读顺序：

1. `docs/AI_BROWSER_CAPTURE.md`：当前学生网页采集方案、匿名规则、采样预算与待实现状态。
2. `docs/AI_INTEGRATION.md`、`ai-service/README.md`：已验证底座、实验对照、服务器模型准备。
3. `docs/AI_OPERATIONS.md`：用户操作、状态、部署/迁移、备份/恢复、容量。
4. `docs/AI_MODEL_VALIDATION.md`、`docs/AI_TEST_REPORT.md`：真实证据与未验收边界。

真实文件视频与 HTTP/数据库/原页面闭环已验；2026-11-13本机USB旧节点首测通过。
学生浏览器采集、Linux部署、课堂质量及两小时稳定性仍待验收，不以节点测试或单图 smoke 代替。
生产先单进程 `python scripts/migrate.py`，API副本 `AUTO_INIT_DB=false`；
本地默认自动迁移仍保留。


