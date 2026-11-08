<p align="center">
  <a href="https://github.com/mizhexiaoxiao/vue-fastapi-admin">
    <img alt="Vue FastAPI Admin Logo" width="200" src="https://github.com/mizhexiaoxiao/vue-fastapi-admin/blob/main/deploy/sample-picture/logo.svg">
  </a>
</p>

<h1 align="center">vue-fastapi-admin</h1>

[English](./README-en.md) | 简体中文

基于 FastAPI + Vue3 + Naive UI 的现代化前后端分离开发平台，融合了 RBAC 权限管理、动态路由和 JWT 鉴权，助力中小型应用快速搭建，也可用于学习参考。

### 特性
- **最流行技术栈**：基于 Python 3.11 和 FastAPI 高性能异步框架，结合 Vue3 和 Vite 等前沿技术进行开发，同时使用高效的 npm 包管理器 pnpm。
- **代码规范**：项目内置丰富的规范插件，确保代码质量和一致性，有效提高团队协作效率。
- **动态路由**：后端动态路由，结合 RBAC（Role-Based Access Control）权限模型，提供精细的菜单路由控制。
- **JWT鉴权**：使用 JSON Web Token（JWT）进行身份验证和授权，增强应用的安全性。
- **细粒度权限控制**：实现按钮和接口级别的权限控制，确保不同用户或角色在界面操作和接口访问时具有不同的权限限制。

### 在线预览
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

### 快速开始
#### 方法一：dockerhub拉取镜像

```sh
docker pull mizhexiaoxiao/vue-fastapi-admin:latest 
docker run -d --restart=always --name=vue-fastapi-admin -p 9999:80 mizhexiaoxiao/vue-fastapi-admin
```

#### 方法二：dockerfile构建镜像
##### docker安装(版本17.05+)

```sh
yum install -y docker-ce
systemctl start docker
```

##### 构建镜像

```sh
git clone https://github.com/mizhexiaoxiao/vue-fastapi-admin.git
cd vue-fastapi-admin
docker build --no-cache . -t vue-fastapi-admin
```

##### 启动容器

```sh
docker run -d --restart=always --name=vue-fastapi-admin -p 9999:80 vue-fastapi-admin
```

##### 访问

http://localhost:9999

username：admin

password：123456

### 本地启动
#### 后端
启动项目需要以下环境：
- Python 3.11

#### 方法一（推荐）：使用 uv 安装依赖
1. 安装 uv
```sh
pip install uv
```

2. 创建并激活虚拟环境
```sh
uv venv
source .venv/bin/activate  # Linux/Mac
# 或
.\.venv\Scripts\activate  # Windows
```

3. 安装依赖
```sh
uv add pyproject.toml
```

4. 启动服务
```sh
python run.py
```

#### 方法二：使用 Pip 安装依赖
1. 创建虚拟环境
```sh
python3 -m venv venv
```

2. 激活虚拟环境
```sh
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows
```

3. 安装依赖
```sh
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

4. 启动服务
```sh
python run.py
```

服务现在应该正在运行，访问 http://localhost:9999/docs 查看API文档

#### 前端
启动项目需要以下环境：
- node v18.8.0+

1. 进入前端目录
```sh
cd web
```

2. 安装依赖(建议使用pnpm: https://pnpm.io/zh/installation)
```sh
npm i -g pnpm # 已安装可忽略
pnpm i # 或者 npm i
```

3. 启动
```sh
pnpm dev
```

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

路由模块已在 `app/api/v1/courses/__init__.py`、`app/api/v1/sessions/__init__.py`、`app/api/v1/emoji/__init__.py` 中导出（自带前缀和 tags）。合并时在 `app/api/v1/__init__.py` 中注册即可：

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


