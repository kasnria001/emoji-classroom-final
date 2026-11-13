# D 首版软件验收报告

日期：2026-11-11；Windows x86_64，Python 3.11.15，SQLite 与临时 MySQL 8.4.10，
Chromium 158（Playwright 1.65.0）。测试数据/凭证/输入视频仅存在临时库或本地忽略目录。
常规自动化使用隔离库；§6明确授权的本机网页短测使用原业务库专用临时课堂，
结束后停止采集并删除测试账号。正式仓库不存 PAT/设备 secret/权重/raw/截图/trace。
§1–5为历史首版证据；当前学生网页产品与三端权限的最终结果以§6为准。

## 1. 已验证范围

| 层 | 验证 | 证据 |
| --- | --- | --- |
| 后端回归 | 原 A/B/C、角色/跨用户、历史分页、五类统计、北京时间、CSV | `tests/` |
| D控制/数据 | 非superuser ADMIN、TEACHER/student、动态RBAC、deviceJWT分离、grant、revoke | `test_d_ai_api.py` |
| 可靠入库 | 同事件并发只有一次效果、冲突、filtered原决定、旧租约补交、fencing | SQLite/API与MySQL5并发 |
| 请求隐私 | JSON/chunked256KiB、额外raw拒绝、不回显/审计secret | `test_d_ai_api.py` |
| Worker | ready首帧、租约内采样、暂停释放/ACK节流、EOF、严格outbox、restart/TTL/quota/ACK不确定 | 独立服务测试 |
| 真实模型 | standard/edge固定权重与分数、30次单图、blank无脸 | `AI_MODEL_VALIDATION.md`，两项显式模型测试 |
| 真实闭环 | 生成获准本地样例视频→真实OpenCV→独立edge Worker进程→HTTP→receipt/EmojiRecord→原看板/CSV | `test_d_worker_http.py` |
| Vue/浏览器 | 管理员注册/一次性secret/关闭清除，教师自己的课堂暂停/异课堂无panel，学生禁止任务路由 | `test_d_browser.py` + `web/tests/ai-browser.py` |
| 聚合与容量 | 1200匿名同时间记录、北京跨午夜day/minute、student=0、97条游标页无重复漏行、导出maxID | `test_d_capacity.py` |
| 迁移/备份 | SQLite真实Aerich新/旧baseline、0→1→2幂等、online snapshot integrity与数据恢复 | `test_d_operations.py` |
| MySQL | 新旧ORM baseline+additive、真实Aerich、并发receipt、SQL聚合、mysqldump→新库恢复 | `test_d_mysql.py`两项（显式BIN启用恢复） |
| 前端 | 认证/学生/教师/AI控制54项，日期3项，Vite production build | 原测试入口+新D用例 |
| 静态 | 新核心Python black/ruff、Git diff/凭证scan | 本地执行 |

集成期间发现并修正：SQLite `strftime`自动将存储`+08:00`转UTC；
Tortoise含JOIN的Count默认按主键分组；Windows sqlite context manager不关闭连接导致
backup rename失败；暂停节点频繁ACK；网络等待不能延长lease；响应异常不能丢outbox。
这些不是仅记录建议，已有代码和回归。

## 2. 重跑

最终执行：常规后端109 passed，真实视频HTTP与Chromium各1 passed，
共111个后端用例（分批执行；之前未新增生产设置时全量110 passed）；
独立AI 40 passed（含两个真实模型，不是skip）；MySQL 2 passed（包含真实dump/restore）；
前端54+日期3 passed；Vite build通过。原依赖弃用提示及已有Unocss/路由拆包提示仍在，
不把这些提示误写成测试失败。

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests --ignore=tests/test_d_mysql.py
.\ai-service\.venv\Scripts\python.exe -m pytest -q -c ai-service/pyproject.toml ai-service/tests --model-smoke-input "<approved-local-image>" --model-dir ai-service/models
cd web
pnpm test:auth
node tests/session-date.test.mjs
pnpm build
```

真实HTTP闭环需显式 `AI_TEST_SMOKE_IMAGE`；Chromium需隔离安装 Playwright、
`AI_TEST_BROWSER_PYTHON` 与浏览器安装目录，已启动web（默认localhost:3100）；
MySQL需显式 `AI_TEST_MYSQL_PASSWORD` 与临时127.0.0.1:3307。
不配置这些时相应项 skip，不计为真实能力通过。AI推理依赖与业务后端/浏览器工具分环境。
详细机器测试计数以最终追加执行结果为准，不能把所有 skipped 合算 passed。

真实闭环测试 threshold=0 为确定可发布验证参数，不是生产建议；
样例无课堂标注，不计算macro-F1、不宣称“识别准确率”。
publisher单测注入断网/ACK不确定；实际教室断网/阻塞USB未在本机硬件演练。

## 3. 支持/未验收矩阵

| 项目 | 实现状态 | 本次验收 |
| --- | --- | --- |
| Windows CPU edge/standard | 固定profile/hash/runtime | 真推理通过 |
| file VideoCapture+Worker+HTTP | 已实现 | 真闭环通过 |
| Windows USB（历史节点） | 已实现，非新版产品入口 | 2026-11-13本机短测通过，见下文 |
| RTSP（历史节点） | 旧输入适配实现 | 未验收；新版不保留公共摄像头路线 |
| 学生网页采集 | 控件/短期授权/时槽/独立服务已实现 | 2026-11-13本机真实getUserMedia短测通过，见§6；全班待验收 |
| Linux edge | downloaded wheel hash lock、Dockerfile | 无Linux/Docker运行，待验收 |
| API/Web/MySQL Compose | 分服务、单migrate、secrets、health | 未构建/启动，不计通过 |
| SQLite online backup/restore | 脚本与安全目标检查 | 真恢复通过 |
| MySQL dump/restore | 运维流程与临时库真实恢复 | 本机恢复通过，正式RTO/切换待演练 |
| 2小时/24小时soak | 有真实计时脚本 | 未跑满，不计通过 |
| 课堂macro-F1/小脸/低光/多流容量 | 测评方法/门槛已定义 | 无授权标注集/现场，不计通过 |
| 采样→入库p95≤5秒/页面≤15秒 | 目标 | 未作容量SLA结论 |
| 权重/训练数据发布许可 | 来源/库许可已记 | 权重/数据条件需发布前复核 |
| FER/GPU/MQ/K8s/量化 | 评估/后续 | 不作为首版虚假能力 |

软件闭环与实验主要代码要求已落地；“正式课堂生产验收”仍需矩阵中目标环境/数据条件。
未验收不是吞掉错误或假返回成功；节点缺模型/输入明确fail closed，UI呈现真实状态。

计时脚本另跑10.016秒，20次真实edge推理成功，仅验证脚本能运行；
不计为两小时soak或容量SLA。生产secret加载/默认拒绝专项新增1项通过。

## 4. D 贡献及共享文件影响

D：独立推理适配/准备/基准、capture/worker、凭证/任务/租约、幂等匿名入库、
严格schema/body/audit、权限/菜单增量、AI UI、SQL聚合/流式CSV、部署/备份/测试文档。
共享A：课堂/课程变更事务guard防活动job竞态；新增additive表，不重建业务模型。
共享B：JWT不能冒充AI，教师详情嵌panel，学生MANUAL/历史保持。
共享C：原管理端新增设备/任务与看板panel、聚合/导出优化，返回列/形状/北京口径保持。
私有实施规划只在 `.local`，由 `.git/info/exclude` 排除；正式文档/源码/测试提交。
Git身份 `kasnria001 <kasnria001@users.noreply.github.com>`，按阶段提交到feature分支，不改main。

## 5. 2026-11-13本机USB首测（旧节点链路）

使用这台Windows电脑的摄像头索引0，OpenCV实际后端DSHOW、分辨率640×480。
先做8秒有界输入检查，获取155份最新帧样本后释放；没有保存照片/录像。

随后通过原API注册专用设备、创建独立测试课堂，真实edge模型→服务认证HTTP→
同一EmojiRecord→原看板，采样间隔2秒、表情阈值0.70、检测阈值0.85。
2026-11-13 10:52:57至10:55:18（北京时间），67次推理采样：
58条成功发布、9次过滤、0次无脸、待补交0、丢弃0。
测试本机预览仅处理内存帧，设备凭证只存进程内存；结束后确认stopped、活动slot释放、
摄像头释放，撤销测试设备凭证。本次使用业务库中的专门测试课堂，不混入原课堂。

原计划测试最长15分钟，实际提前停止约2分21秒，**不计15分钟持续采集通过**。
未专门完成离开镜头、多脸、断网、低光、全班并发或课堂准确率验收。
结果中有通过阈值的分类不代表该分类经人工标注核验正确。

本次证据说明普通电脑摄像头能走旧Python节点真实闭环，
**不说明学生浏览器getUserMedia→独立AI服务的新路线已经实现**。
用户随后确定新版只保留学生网页采集，强制匿名；接入与采样规范见`AI_BROWSER_CAPTURE.md`。

本轮同时修复静态学生/教师子路由缺少显示标题，以及已缓存标签不更新的问题；
内部`TeacherClassroomHome`保留作路由标识，不显示在中文菜单/页面标题/标签上。
前端认证/业务测试56 passed、日期测试3 passed、Vite构建通过；空子路由不再重复显示面包屑。
隔离Chromium通过`web/tests/navigation-labels.py`使用测试HTTP验证真实教师页面
中文菜单/页面标题/旧标签更新，无重复标签；
该浏览器检查不访问摄像头，不计为学生网页采集通过。

## 6. 2026-11-13学生网页采集交付与验收

产品入口已替换为原学生课堂页的「摄像头匿名反馈（可选）」、
教师课堂详情/原看板的只读「课堂匿名采集状态」。
管理员“AI服务身份”管理独立服务器凭证，“课堂采集管理”面向全部课堂配置/启停，
没有“我的课堂/我的教室”或学生入口。历史CLI管理写API也限管理员，避免权限绕行。
不再提供公共摄像头产品操作入口；历史CLI代码保留作回归工具。
详细部署、身份注册、普通电脑操作、HTTPS/代理、采样和故障处理见
`AI_BROWSER_CAPTURE.md` §3–9。

### 本轮代码与自动化结果

- 常规后端全量：**118 passed，4 skipped**。跳过的分别是显式Chromium、
  MySQL两项、旧真实文件Worker；以下另跑的通过项不与常规计数混淆。
- 新浏览器后端授权/排课/60秒TTL/主动停止清身份/重开配额/票据/单人门/
  匿名入库与原看板闭环、ADMIN+RBAC、教师只读：8项，包含在118中。
  另补普通非superuser ADMIN全局课程/课堂/排课/删除回归。
- 独立AI完整测试，显式已有获准本地素材及两套固定模型：**47 passed，0 skipped**。
  其中新单帧服务7项，覆盖JPEG尺寸解码前限制、单人检查先于质量过滤、
  无脸/多人/低分不写记录、只出匿名元数据、严格来源/格式/尺寸/授权。
- 临时MySQL8.4.10真实新旧库升级、MANUAL保留、并发receipt、SQL聚合、
  四步Aerich迁移、mysqldump恢复：**2 passed**。实例测试后正常SHUTDOWN。
- 真实Chromium管理员全局工作台、无“我的课堂”、
  服务身份注册/一次性secret/关闭清除、管理员选全局课堂停止、
  教师所属课堂只读/异课堂隔离/无管理菜单、学生不能进入管理任务页：**1 passed**。
- 前端认证/原业务：**57 passed**；新增camera与日期：**8 passed**；
  最终Vite生产构建通过。新增核心Python ruff通过。
- 当前业务SQLite先执行online backup并验证完整性，再执行增量migration3；
  原课堂/手动记录未重建。运行配置/备份/权重/测试报告原始JSON留在忽略目录。

最终合并执行（含最新权限、标签清理、匿名CSV与格式化代码）：
后端显式启用Chromium和真实文件Worker后 **120 passed，2 skipped**，
两个跳过项仅为MySQL，在独立临时实例另跑 **2 passed**（含真实dump/restore）。
因此后端122项均有通过证据；不把常规118、显式120和MySQL2重复相加。
独立AI重新执行 **47 passed**；前端重新执行57+5+3项并完成Vite生产构建。
MySQL测试实例已正常关闭，业务API与网页AI服务健康检查ready。

### 实际学生页面：模拟流与真实硬件分开记录

1. 模拟MediaStream，不假装是硬件：
   使用实际Vue控件、原登录/排课API、实际二进制HTTP、独立edge真模型。
   最新权限收紧后的复测3次采样均no_face；AI记录0，看板AI0。
   停止后全部track ended；没有pageerror；持久化存储没有bcc/aic凭证。
2. 本机真实摄像头：
   Chromium使用原生 `getUserMedia`，约35秒有界采集；
   **间隔10秒、表情阈值0.70、检测阈值0.85**，没有为通过而降低阈值。
   3次HTTP采样：**2 accepted、1 no_face**。
   同一原业务库专门测试课堂产生2条 `user_id=None / source=AI` 记录，
   原看板 `ai_count=2`；停止后活动采集会话0、全部track ended，
   没有pageerror，浏览器存储不含服务或采集凭证。
   临时测试账号在结束后删除，测试课堂停止；没有保存照片、录像、截图或trace。

真实短测证明普通电脑网页摄像头可贯通，不是完整课程/多学生容量/准确率验收。
真实多人、低光、跨摄像头重复、50端并发、2小时soak、Linux/Compose/TLS、
课堂标注macro-F1和SLA仍未计通过。多人门有自动化验证，不能替代真实多人现场测试。
匿名统计是观测条数，不是学生人数或逐学生等权结果。

可靠性边界：学生页一请求在途，过载/断网跳过错过帧、不持久缓存原图；
AI只将已通过单人门的严格v1元数据写outbox，TTL60秒并有界重试。
最终入库要求采集授权仍有效，停止后未入库结果拒绝；
claimed但未完成的事件不重复推理，以跳过该槽换取fail-closed，不保证每次采样都产生记录。

权限依据：指导书§2.1–2.2区分全局管理员与所授课堂教师，§6只要求参数可配，
未指定教师必须拥有AI启停权或学生必须开相机。管理员控制、教师只读、
学生仅本机授权/释放是项目的最小权限实现。测试同时覆盖误授教师配置API仍403、
ADMIN移除动态RBAC配置授权后403，以及旧教师AI写授权的幂等撤销。

HTTP超限回归以真实socket只发送超限Content-Length、不发送正文，验证读取/推理前413，
避免Windows客户端持续上传大正文而服务提前关闭连接触发TCP reset的测试竞态。
