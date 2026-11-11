# 独立课堂 AI 服务：P1 模型适配与验证

**当前可运行的是模型准备、doctor、离线单图片 benchmark 和测试，不是完整课堂采集 worker。** USB/RTSP/file 视频、任务控制、设备认证、outbox/重试和真实 API 入库将在后续实现。设计及实验对照见 `../docs/AI_INTEGRATION.md`。

首版默认摄像头由独立课堂采集节点连接，学生端仍手动反馈；保留以后同机部署/获准本地桥接扩展，学生用户 JWT 与设备凭证不合并，AI 默认匿名。

## 1. 验证环境与依赖隔离

已验证 Windows x86_64、CPython 3.11.15、CPU：

- standard：DeepFace 0.0.104 Emotion-only + YuNet，显式 ONNX Runtime 1.31.1 CPU，不安装 TensorFlow/PyTorch。
- edge：OpenCV 4.11.0.86 YuNet + MobileFaceNet 表情 FP32 ONNX（不是身份 embedding 模型），不需要 DeepFace。
- NumPy 2.2.6。FER 暂仅依赖/接口对照，不是已验证生产 profile。
- `requirements/*-windows-py311.lock` 是含 SHA-256 的**此平台 wheel 锁**（含 pytest），不宣称覆盖 Linux/macOS。Linux 锁/容器待验收。

仓库根目录执行：

```powershell
py -3.11 -m venv ai-service/.venv
# 选一种 profile；不要安装到后端 .venv。
.\ai-service\.venv\Scripts\python.exe -m pip install --require-hashes -r ai-service/requirements/standard-windows-py311.lock
# edge 仅替换上面的锁文件：
# .\ai-service\.venv\Scripts\python.exe -m pip install --require-hashes -r ai-service/requirements/edge-windows-py311.lock
.\ai-service\.venv\Scripts\python.exe -m pip install setuptools==75.8.0 wheel
.\ai-service\.venv\Scripts\python.exe -m pip install --no-deps --no-build-isolation -e ai-service
.\ai-service\.venv\Scripts\python.exe -m pip check
```

也可用于开发快速安装 `pip install -e "./ai-service[standard,test]"`，但正式复现使用平台锁。后端 `requirements.txt` 没有新增推理依赖。

## 2. 显式准备模型与离线检查

权重不进 Git，只有不可变来源/版本/长度/SHA-256 清单 `models/manifest.json` 提交。OpenCV 文件 URL 固定 Git commit，DeepFace release 文件额外以 SHA-256 固定内容。下载过程有限长度、哈希校验、原子替换，不把错误页当模型。

```powershell
.\ai-service\.venv\Scripts\python.exe -m emoji_ai.prepare --profile standard --manifest ai-service/models/manifest.json --model-dir ai-service/models
.\ai-service\.venv\Scripts\python.exe -m emoji_ai.prepare --profile edge --manifest ai-service/models/manifest.json --model-dir ai-service/models
.\ai-service\.venv\Scripts\python.exe -m emoji_ai.cli doctor --profile standard --manifest ai-service/models/manifest.json --model-dir ai-service/models
.\ai-service\.venv\Scripts\python.exe -m emoji_ai.cli doctor --profile edge --manifest ai-service/models/manifest.json --model-dir ai-service/models
```

离线启动前验证文件，缺失/哈希不符明确失败，不静默换模型或切到 fake。一个进程使用一个 profile/检测配置，DeepFace global engine/model cache 不宜跨任务修改。后续 worker 的并发/线程预算须实测。

## 3. Benchmark 与测试

自备已获准本地图片，不将素材或个人路径提交 Git。脚本仅读取图片、输出匿名汇总，不输出图片、坐标、身份、文件路径或原始 logits。

```powershell
.\ai-service\.venv\Scripts\python.exe -m emoji_ai.cli benchmark --profile standard --manifest ai-service/models/manifest.json --model-dir ai-service/models --input "<local-approved-image>" --repeats 30 --threshold 0.7 --detection-threshold 0.85
.\ai-service\.venv\Scripts\python.exe -m emoji_ai.cli benchmark --profile edge --manifest ai-service/models/manifest.json --model-dir ai-service/models --input "<local-approved-image>" --repeats 30 --threshold 0.7 --detection-threshold 0.85
.\ai-service\.venv\Scripts\python.exe -m pytest -q -c ai-service/pyproject.toml ai-service/tests
# 显式启用真实模型检查，否则这两项 skip，不能计为真实能力已通过。
.\ai-service\.venv\Scripts\python.exe -m pytest -q -c ai-service/pyproject.toml ai-service/tests --model-smoke-input "<local-approved-image>" --model-dir ai-service/models
```

脚本可重复指定 `--input`，但当前一次载入所有输入，只适用于小规模 smoke；后续视频/数据集 benchmark 需流式和标注评估。startup_ms 不含 Python 进程启动与顶层依赖 import；warm latency 是检测/对齐/分类/映射，不含网络/DB，不能当采样→入库 SLA。

分数规则：

- DeepFace 返回 emotion percent，转换 `[0,1]`，不二次 softmax；detector score 另存。
- 轻量模型末端为 Gemm/Identity、实测原始输出有负值，不是概率；明确稳定 softmax 后作模型分数，不称已校准概率。
- 七类只映射 happy/sad/angry/surprise(d)/neutral 五类；fear/disgust 的赢家拒识，不重新挑支持类别。
- no-face 返回空观测，不写 NEUTRAL；其他模型异常向上传播；过小人脸/低分有独立原因。
- 当前 0.7/0.85 是验证参数，不是未经质量评估就批准的生产默认。

实测证据、局限和未验收项见 `../docs/AI_MODEL_VALIDATION.md`。
