# D：AI 集成设计与实验要求对照

日期：2026-11-11。本文是正式设计交付物，不是私人实施计划。

**2026-11-13修订优先于下文旧节点部署设计：仅学生网页摄像头采集，结果强制匿名，
不保留公共摄像头产品入口；管理员统一配置/启停，教师只读所授课堂，学生仅操作本机摄像头。**
管理员是全局管理工作台，不提供「我的课堂/我的教室」。指导书不要求公共摄像头或固定采样次数，
也未指定教师必须拥有AI启停权限；此处采用最小权限实现。
独立Python推理与现有课堂/认证/幂等入库仍保留；浏览器接入已实现并完成本机短测。
新版接入与10秒默认采样预算见 `AI_BROWSER_CAPTURE.md`；下文旧节点事实保留作历史/迁移依据。

**当前状态：D 软件首版闭环已实现。** 设备/授权/课堂任务、租约/fencing、事务 receipt/metadata、
真实视频 Worker、持久 outbox、原 Vue 页面集成、SQL 聚合与有界 CSV 均已落地。
真实文件→独立模型进程→HTTP→数据库→原看板/CSV，以及 Chromium 管理员/教师/学生流程已验证。
详细测试和未完成的现场验收见 `AI_TEST_REPORT.md`，操作/部署见 `AI_OPERATIONS.md`。
USB/RTSP、Linux Compose、课堂准确率、两小时 soak 未计为已验收，不据 smoke 宣称生产现场全通过。

## 1. 实验要求核对

依据仓库根目录 `《表情符号课堂情绪检查器系统》实验指导书.txt` 的 §2.2、§3、§4、§5、§6、§9、§11，以及 `docs/TEAM_MODULES.md` 的 D 分工。

结论：设计匹配必做要求，没有模型库或采集端的硬性冲突。指导书推荐 OpenCV + DeepFace/FER **或轻量模型**，不是必须同时使用两个库；独立 AI 服务是部署边界要求，不要求摄像头由学生浏览器采集。实体可合理扩展；接口示例不要求逐字照搬路径，继续采用 `/api/v1`。

| ID | 实验必做/交付 | 设计与实现位置 | 验收方式 | 当前证据 |
| --- | --- | --- | --- | --- |
| D01 | 摄像头流帧采样 | `StudentCameraCapture` + `emoji_ai.browser_service` | 实际getUserMedia→JPEG→独立模型→释放 | 本机网页硬件短测通过；全班待验收 |
| D02 | 人脸检测和表情分类 | emotion-only standard/edge adapter | 固定预处理/七类分数、真实模型与blank | 两套 CPU 实测；课堂质量待验收 |
| D03 | 至少五类 Emoji 映射 | `emoji_ai.mapping`，复用现有五类枚举 | 五类、别名、unsupported、invalid output 单测 | P1 实现 |
| D04 | 采样频率/置信度可配 | profile + job 不变配置快照 | 边界、节点调度、后端复核 | 已实现与测试 |
| D05 | AI/confidence/session/timestamp 入库 | credential/job 推导，显式 captured_at | 同一 EmojiRecord、真实采样时间 | HTTP闭环与兼容测试通过 |
| D06 | 匿名、不保存人脸图片/视频 | null user、严格元数据、帧仅内存 | DB/outbox/log/一次性 secret | 已实现与测试 |
| D07 | 重试与错误日志 | WAL outbox + publisher + safe events | ACK不确定/重启/TTL/quota/fencing | 自动化故障测试通过；现场断网长测待验收 |
| D08 | 独立服务令牌 | hash-only credential、分配/轮换/revoke | JWT分离、跨教师/设备越权 | 已测试 |
| D09 | REST/统一错误/OpenAPI | FastAPI 控制/数据面、worker不直连DB | 严格 body、chunked限量、安全audit | 已注册并测试 |
| D10 | 原历史/看板/统计/CSV | 原页面嵌AIJobPanel、同一表 | null不计学生、UTC→北京、SQL聚合 | 自动化/真实HTTP/Chromium通过 |
| D11 | 分层与迁移 | controller/service/ORM、additive migration2 | SQLite/MySQL新旧库、并发、Aerich | 已测试；旧手写schema须字段diff |
| D12 | 单元/API/帧→DB/E2E/权限 | backend + ai-service + web/tests | fake/真实模型/硬件分开计 | 软件自动化矩阵通过 |
| D13 | API/部署/用户/测试/贡献文档 | 本文/AI_OPERATIONS/AI_TEST_REPORT/模型报告 | 正式Git提交、可复现命令、未验收矩阵 | 已落地，Linux部署需目标环境验收 |

产品增强：设备管理、课堂任务、租约/fencing、幂等回执、持久 outbox、监控是首版可靠性设计，但不是指导书原文新增的评分项。Compose/CI/MQ/MCP 是选做；不先堆平台，不用这些扩展替代真实视频→数据库闭环。

## 2. 架构决策 ADR-D-001：业务耦合，运行隔离

```text
现有 Vue（学生 / 教师 / 管理员） ──原用户 token──► 现有 FastAPI
                                          控制面：设备、任务、运行状态
                                          数据面：服务认证、校验、可靠入库
                                                     │
独立 ai-service ──独立设备 credential / HTTPS───────────┘
摄像头→采样→检测/对齐→表情→过滤/映射→元数据 outbox     │
                                           同一 Tortoise/MySQL
                              User/Course/ClassSession/ScheduleUser/EmojiRecord
                                      + AI device/job/lease/receipt/metadata
```

- 复用 A 的领域实体、B 的认证/教师课堂与个人历史、C 的看板/统计/CSV。不复制用户、课堂、结果库或管理端。
- 推理框架仅装在独立服务；后端不导入 OpenCV/DeepFace，worker 不直连业务数据库。
- 当前摄像头由学生网页读取并上传单帧；独立服务器只推理，不打开摄像头。
  管理员控制课堂策略，教师只读状态，学生手动反馈仍保留。下文旧节点设计仅作历史迁移说明。
- worker 主动 heartbeat/poll；后端不下发任意命令、文件路径或含凭据 URL。输入使用节点配置的 source alias。
- 表情观测不等于已确定的心理状态；匿名 AI 观测数不等于唯一学生数，不做身份识别或个人评分。

### 保留扩展：采集节点与学生端二合一

允许以后将 worker 与学生 PC/终端客户端部署在同一设备，或另行实现获准的浏览器采集桥接。**物理同机不等于身份合并**：

1. 学生用户 token 仅用于原业务；设备 credential/job/lease/outbox 独立，不能用学生 JWT 直接写 AI。
2. 摄像头权限、明确启停、授权撤回、本机资源预算必须有独立交互；浏览器路线还须设计 HTTPS/权限和 bridge 协议。
3. AI 默认 `user_id=None`；不能因为与学生端同机而自动将所有检测人脸绑定当前学生账号。
4. 服务器事件契约、课堂范围和任务控制不变；没有 bridge/capture 的实际验证之前，不宣称已支持学生浏览器摄像头。
5. 首版不为该扩展实现每学生采集、视频上传、身份识别或新客户端。现有部署分离仍是默认路径。

## 3. A/B/C 兼容约束

- 现有枚举仍为 `HAPPY/SAD/ANGRY/SURPRISED/NEUTRAL`、`MANUAL/AI`；`fear/disgust` 拒识计数，不冒充 NEUTRAL。
- 旧历史/列表字段及分页、`/emoji/statistics` 数组、累计 dashboard、CSV 列顺序/BOM/注入防护保留。
- 学生个人历史不包含匿名 AI；教师按当前 course.teacher 归属读取，匿名 AI 不增加 student_count。
- 旧 API 日期沿用无时区北京 wall-clock；新 AI `captured_at` 为带偏移 RFC3339，先归一 UTC，入旧表前转北京时间。
- 普通 `/api/v1/emoji` 不再允许任何用户 JWT 写 AI（包括 admin）；AI 缺 confidence 仍先触发原 schema 的 422。C 的测试数据直接准备匿名记录，不再借教师 token 冒充服务。
- 新模型、lease、payload hash 等内部字段放独立 metadata/receipt，不能塞到旧 `BaseModel.to_dict()` 自动公开字段。
- 按真实容量推进 C 的 SQL 聚合和有界 CSV，不突然把课堂累计统计改成滑窗统计。

## 4. 目标数据模型（未迁移，不是现有表）

| 实体 | 关键字段/关系 | 约束 |
| --- | --- | --- |
| AIDevice | source aliases、enabled、能力、heartbeat；显式教师授权关系 | 设备禁用 fail closed，secret URL 留节点 |
| AICredential | device FK、hash、scopes、expires/revoked/rotation | 高熵独立 secret，仅一次明文显示，不进入 audit |
| AIJob | session FK、device/source、批准 model/config 快照、actor、状态/generation | 当前课程归属 + 设备分配；单相机唯一活动绑定 |
| AILease | job FK、lease UUID、generation、incarnation、有效采集窗、终止原因 | DB 原子领取/续约；旧 worker/旧 generation fencing |
| AIReceipt | event UUID、canonical payload hash、decision、record FK、received_at | unique event、接受/过滤决定持久化，与 record 同事务 |
| AIRecordMetadata | record FK、device/job/model/mapping/config、采样/接收时间、有限质量 | 不存图片/坐标/embedding/身份，显式安全序列化 |

课堂改时间/换教师/删除、设备撤销与任务联动；活动删除应明确拒绝或有序停止，不能级联后让节点继续上报。新/旧 MySQL 和 SQLite 都必须测试；不能只凭 SQLite 测试宣称生产迁移完成。

## 5. 目标 API v1（设计）

| API | 身份 | 责任 |
| --- | --- | --- |
| `/api/v1/ai/devices`、credential actions | 原用户 token + ADMIN RBAC | 注册、分配、签发/轮换/撤销、状态；无 secret 回读 |
| `/api/v1/ai/jobs`、preflight/actions/status | 原用户 token + TEACHER/ADMIN + 当前课堂归属 | 选设备/profile，预检、启停、运行状态 |
| `/api/v1/ai/worker/heartbeat`、poll/lease | 独立设备 credential | outbound 领取/确认、能力、租约续期 |
| `POST /api/v1/ai/emoji-results` | 独立设备 credential + job/lease 范围 | 单事件可靠入库，统一 Success/Fail |
| `POST /api/v1/ai/emoji-results/batch` | 同上 | 最多 50 事件、256 KiB 请求初值、逐事件回执 |

控制面使用既有 `DependAuth`/`DependPermission`，还要做数据归属；数据面不得将设备凭证伪装成用户 JWT。旧库 API/menu/role 需增量幂等补齐，不覆盖已有自定义授权。新动态路由权限匹配必须测试，不能只测 superuser。

事件示例（`app/schemas/ai.py` 已实现）：

```json
{
  "contract_version": 1,
  "event_id": "7dd9ab8d-6f1c-467a-922f-f19f7a87514a",
  "job_id": 23,
  "generation": 4,
  "lease_id": "e573b86d-1d5b-44f0-915b-38d58c1cb5a9",
  "captured_at": "2026-11-11T08:40:00.123Z",
  "emoji_type": "HAPPY",
  "confidence": 0.91,
  "model_version": "deepface-emotion-0.0.104-onnx",
  "config_revision": 3,
  "mapping_version": "five-emotions-v1",
  "quality": {"detection_confidence": 0.96}
}
```

- session/device/source/user 由 credential + job 推导；额外 raw、session override、identity 字段拒绝。
- strict positive integer/UUID v4、finite confidence `[0,1]`；bool/string/NaN/Inf 不强转。model/config/mapping 必须与批准快照一致。
- 时间须落在课堂 `[start,end)` **且** job/lease 有效采集窗；future skew 30 秒、补交 15 分钟为待实测初值。
- 停止前已授权事件可以有界补交，但撤销/强制终止 fail closed；duplicate 也先检查当前授权。
- event/hash 稳定重试；accepted、filtered 保存原决定；同 ID 不同 payload 返回 conflict，不覆盖记录。at-least-once delivery + exactly-once effect，不承诺网络 exactly-once。
- batch HTTP 200 不代表所有事件成功；accepted/duplicate/filtered/conflict/rejected 按项处理。
- 读取完整 JSON 前限制 body bytes，audit/validation 错误不能回显素材或 secret；schema alone 不等于字节限制或安全日志已经完成。

## 6. 正式验收顺序

后端阶段实施补充：一个 AIDevice 代表一个固定 source alias，用 unique active_slot 保证同时一个非终止任务；heartbeat 5 秒、租约 45 秒。控制先更新 desired/generation、关闭旧采集窗，停止/暂停前结果仍可按历史租约 15 分钟内补交；credential revoke/设备禁用关闭所有授权。停止节点 ACK 或租约安全过期后才释放设备。ADMIN 非 superuser、TEACHER、跨教师、用户 JWT/device token 分离和 chunked 超限已测试。

MySQL 首次实测发现缺 `cryptography` 无法执行默认 caching_sha2_password 认证，已添加兼容现有 CFFI 的 45.0.7。迁移 0/1 保留原 SQLite SQL，仅补 MySQL 分支（此前 MySQL 自动迁移不可运行），新迁移 2 添加 AI 表；ORM-compatible MySQL bootstrap 与升级 SQL 正式提交。部署只单 migration 进程，备份后升级，不删除现有库。

1. P1：兼容契约、元数据/时间/分数边界、真实模型可安装可推理证据。
2. P2/P3：设备/任务/权限/租约，事务 receipt/metadata 入库与 MySQL 迁移。
3. P4：真实 capture、durable outbox、断网/重启恢复，模拟帧→真实 API→同一表。
4. P5：原课堂 UI、统计/CSV 规模测试、浏览器权限/E2E。
5. P6：部署支持矩阵、备份/恢复、soak、操作手册/模型局限/测试报告。

目标采样 2 秒、采样到入库 p95 ≤5 秒、10 秒页面刷新下可见 ≤15 秒、2 小时 soak、重复业务效果为 0 均为**待验证目标**。P1 单图片 smoke 不代表课堂质量、多人脸容量或最终 D 验收。
