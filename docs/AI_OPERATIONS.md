# D 首版运行与交接手册

日期：2026-11-11。D 与现有 A/B/C 共用用户、课程、课堂、EmojiRecord、
管理端认证和统计，不建立第二套业务数据库。采集节点是独立 outbound Worker。
真实验证范围与未验收项见 `AI_TEST_REPORT.md`，模型来源/局限见 `AI_MODEL_VALIDATION.md`。

**2026-11-13当前接入方案：仅学生网页采集，不保留公共摄像头产品入口。**
学生免安装、服务端部署、匿名/防重复和采样预算见 `AI_BROWSER_CAPTURE.md`。
网页采集API/控件已实现并完成本机短测；管理员统一配置/启停，教师只读所授课堂，
学生仅授权/停止自己的摄像头。管理员没有「我的课堂/我的教室」。首次部署、三端操作与HTTPS
代理步骤统一见 `AI_BROWSER_CAPTURE.md` §8–9。下面的旧节点操作仅作回归/迁移记录。

## 1. 旧节点操作记录（非新版产品入口）

1. 管理员登录现有管理端 →「课堂情绪管理 / AI 采集设备」。
2. 注册设备名称与 `source_alias`，分配现有教师 ID。一设备对应一个输入；
   alias 仅字母、数字、点、下划线、连字符，最多 64 字符，不是摄像头 URL。
3. 签发凭证仅显示一次；保存到节点受限 secret 文件，关闭 modal 后清除。
   设备列表、数据库、审计不保存可回读明文。丢失只能轮换，轮换/撤销会终止原任务。
4. 启动节点，确认在线且模型 profile 已准备。
5. 历史首版曾在教师详情提供控制；当前教师只读，旧任务创建/动作API也仅管理员可写。
   以下选择节点/预检说明是旧 CLI 回归流程，不是当前网页产品页面。
   选择获准设备、profile、采样间隔和表情阈值 →「创建 / 预检」。
6. 等待节点实际获得首帧、状态为预检就绪，在课堂 `[start,end)` 内开始。
   可暂停/恢复/停止；停止任务不可复用，新课堂新建任务。一设备只允许一个活动任务。
7. 原 Emoji 数据、课堂历史、实时看板、统计、CSV 同源展示匿名 AI。
   观测条数不等于学生人数，同一个人可能反复被采样，不替代学生手动反馈。

首版摄像头来自教室采集节点，不是学生浏览器。保留以后节点与学生客户端同机
或本地桥接，但设备 credential、任务/租约与学生 JWT 仍分离，不自动绑定人脸到账号。

## 2. Windows 本地

后端沿用根 README 启动，前端在 `web` 用 pnpm；未配置 AI 时 A/B/C 照常可用。
独立 AI 安装/模型准备见 `ai-service/README.md`。`edge` 不加载 DeepFace/TensorFlow/PyTorch；
`standard` 是固定 DeepFace emotion-only + YuNet + ONNXRuntime CPU。
FER 保留选型评估，不作为未经实测的第三套生产 runtime。

```powershell
Copy-Item ai-service/worker.example.json .local/worker.json
$env:AI_DEVICE_TOKEN_FILE = 'D:\emoji-classroom-final\.local\device.secret'
.\ai-service\.venv\Scripts\python.exe -m emoji_ai.worker --config .local/worker.json
```

编辑配置使 alias 与后台设备一致、profile 与安装环境一致；路径以当前目录为基准，
从仓库根执行。USB 值为摄像头索引，file 是本地视频路径，
RTSP URL（可能含密码）只写节点受限配置，不进入 Git/后台。
设备凭证不通过命令参数、URL、浏览器持久化存储传递。
远程后端强制 HTTPS、证书校验开启；只允许 localhost/127.0.0.1 使用 HTTP。

Ctrl+C / SIGTERM 释放输入与 SQLite。实时输入 latest-frame 覆盖、只保留内存帧；
file 每次采样读下一帧，不按原视频时间重放。EOF 终止，当前协议
`observed=failed, health=eof`，不是分类器失败，不自动循环。
OpenCV 输入阻塞无法可靠停止时进程退出，不在同进程不断开第二个相机。
Windows USB已在2026-11-13本机短测首帧、实际推理/入库和停止释放；
RTSP、阻塞输入及长期运行仍未验收。新版不保留公共摄像头路线。

## 3. 状态与故障

| 状态 | 含义/处理 |
| --- | --- |
| waiting / prechecking | 无任务或等待首帧预检；核对授权 alias、节点连接 |
| ready / running | 已预检或采样中，不代表一定识别到表情 |
| no_frame | 摄像头权限/索引/URL/网络不可用，重连有界退避 |
| no_face | 有画面但无人脸，不写 NEUTRAL |
| model_failed | 缺权重/hash错误/推理异常，重新 doctor，不 fake fallback |
| buffering | 发布失败，租约内短期 outbox 缓冲 |
| degraded | 租约到期/时钟偏差/队列满，停止或降级采集 |
| stopped / credential_revoked | 停止或凭证失效，不自动偷偷恢复 |

heartbeat/常规 ACK 每 5 秒；lease 最长 45 秒且不超过课堂结束。
时钟差超过 30 秒暂停输入，应校准节点时间。desired 是后台命令，
observed 是节点确认，不把点击按钮当成已停止。
节点离线停止后 slot 等 ACK 或安全过期才释放；删除/改时间/换课程教师前停止活动任务。

outbox 先存元数据再发布，event UUID 重试不变；不确定 ACK、重启恢复按原 ID 幂等。
最多 5000 条、50MiB payload、TTL 15 分钟；SQLite 主文件约 51MiB 页数上限、
WAL 周期截断，目录总大小不是精确 50MiB。空间不足失败封闭；
过期/永久拒绝只计 dropped，不存 raw/rejected body。401/403 停止；
429/5xx/网络错误退避+jitter。队列不跨 job 改写。

AI 任务页显示 sampled/no_face/filtered/published/queue_size/dropped/inference_ms、
last_ack 与设备 online。无新 ACK 不能据旧 metrics 判断当前正常。
当前没有 Prometheus、MQ 或自动告警平台；这些不冒充已实现。

## 4. 独立 API/Web/MySQL Compose（待 Linux 验收）

`deploy/compose.yml` 拆分 MySQL、单次 migrate、API、Web；Worker 在教室主机独立运行，
不把教室 USB 自动映射到中心服务器。镜像上下文排除 `.local`、凭证、权重/outbox。
本机无 Docker daemon，**未实测镜像构建或 Compose**。

先在 `.local/deploy/` 生成不同强 secret：`mysql_password`、`mysql_root`、
`jwt_key`（≥32字符）、`admin_password`，限制文件读取权限：

```sh
docker compose -f deploy/compose.yml up --build -d
docker compose -f deploy/compose.yml logs migrate api
curl --fail http://localhost:8080/healthz
```

默认只绑定 `127.0.0.1:8080`，MySQL 无宿主机公开端口。跨机器访问在入口终止 TLS，
设置实际 CORS origin；Worker 用 HTTPS `/api/v1`。
`DEBUG=false` 拒绝默认 JWT key/初始管理员密码。
API 使用普通 MySQL 业务用户，root secret 不进入 API。

多副本先单独 `python scripts/migrate.py`，副本 `AUTO_INIT_DB=false`
只检查无待迁移，不写初始化数据。`/healthz` 检查 DB 连接；
本地默认 `AUTO_INIT_DB=true` 保留易启动。不会自动生成新 migration。

Linux edge 镜像使用 `edge-linux-py311.lock`（下载 manylinux wheels 后计算 hash，
只验证发行物，不代表 Linux 运行验收）。挂只读模型、节点 secret/配置，
可写 outbox，UID 10001 需相应权限。USB 另映射 `/dev/video0` 并授予设备组；
RTSP 无 USB 映射。standard Linux 未锁定/验收，不用 Windows lock 冒充通用。

## 5. 升级、备份、恢复

受测升级路线是 Aerich 0→1→2。MySQL ORM baseline：
`database/mysql_orm_bootstrap.sql`；新增表：`ai_mysql_upgrade.sql`。
新旧 ORM 基线保留 MANUAL 数据。早期 `mysql_schema.sql` 是手写参考，
字段/闭包表可能与 ORM 不一致，不能替代受测迁移入口。
已用手写脚本建库者先做字段 diff，不能据 `IF NOT EXISTS` 宣称已补字段。

SQLite 活跃 WAL 库使用 online backup：

```powershell
.\.venv\Scripts\python.exe scripts/backup_sqlite.py --source db.sqlite3 --destination .local/backups/pre-d.sqlite3
```

脚本拒绝覆盖目标、校验 integrity。恢复先停止 API/Worker，
恢复到新路径用 `SQLITE_PATH` 验证数据/迁移/权限，再切换；不在线移动库/WAL。
备份含账户/课堂信息，放受限存储，不提交。

MySQL 用 DBA 受限配置文件，密码不放命令参数：

```sh
mysqldump --defaults-extra-file=/secure/mysql-client.cnf --single-transaction --routines --triggers emoji_classroom > /secure/backups/pre-d.sql
mysql --defaults-extra-file=/secure/mysql-client.cnf emoji_classroom_restore < /secure/backups/pre-d.sql
```

先新库恢复，检查 row counts、FK、MANUAL、receipt、权限、课堂链路，再维护窗口切换。
MySQL DDL 可能隐式提交，不能指望事务回滚整个升级。
SQLite online restore 与临时 MySQL 真 mysqldump→另一个临时库恢复已实测；
正式环境仍需备份存储、RTO/切换和访问权限演练。
回滚优先备份与兼容旧应用，不直接删 AI 表损失追溯。

默认不自动删除 Emoji 业务记录；receipt 30 天有限批次清理：

```sh
python scripts/cleanup_ai_receipts.py --days 30
python scripts/cleanup_ai_receipts.py --days 30 --apply
```

每次最多 500 条，先 dry-run，不早于 1 天，远大于 15 分钟补交窗。
业务记录、历史 job/lease 保留期需项目管理者确定，目前不级联删历史。

## 6. 容量、模型与发布门

采样默认 2 秒，最多 30 脸/帧；批次最多 50，body 最多 256KiB，
每设备约 100 receipts/秒限速。CPU profile 是单 source 单进程，不宣称无限并行。
原统计/分钟时间线改 DB group/count，null user 不参与 distinct student count。
CSV 固定开始时 max ID、500 行 keyset、最多 100000 行，超限收窄筛选；
字段/BOM/注入防护不变，下载期间并发删除不承诺快照一致。

smoke 不代表课堂准确率、后排小脸、遮挡、低光。默认阈值需授权课堂数据校准，
权重/训练数据许可发布前另核查。两小时模型 soak：

```sh
python ai-service/scripts/soak.py --profile edge --manifest ai-service/models/manifest.json --model-dir ai-service/models --input "<approved-local-image>" --duration 7200 --interval 2
```

这只测单输入模型；摄像头、断网、Worker 长测另外现场执行。
未跑满 7200 秒不计两小时通过。MQ/K8s/GPU/量化/身份追踪不在首版。
