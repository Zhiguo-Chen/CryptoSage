# 比特币智能监控与决策 Agent 系统 (BTC Smart Agent System)

基于多智能体协作的比特币交易信号分析系统，结合技术分析、新闻情绪和政策动态，通过 OpenAI 和 Gemini 模型协同决策。

## 系统架构

```
数据获取层 → 多Agent分析层 → 决策讨论层 → 通知层
    ↓            ↓              ↓          ↓
  价格/新闻   技术/新闻分析    共识/反思    邮件提醒
```

## 核心特性

- **多智能体协作**: OpenAI GPT-4 + Google Gemini 2.0 并行分析
- **技术+新闻融合**: 结合价格技术指标与新闻情绪分析
- **辩论式决策**: Agent 间多轮讨论达成共识
- **反思学习**: 基于历史准确率动态调整权重
- **人机协作**: 根据置信度自动/人工审核

## 快速开始

### 1. 环境配置

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 填入API密钥
# - OPENAI_API_KEY
# - GOOGLE_API_KEY
# - SENDGRID_API_KEY
# - DATABASE_URL
```

### 2. 使用 Docker 启动

```bash
# 启动所有服务（PostgreSQL + Redis + App）
docker-compose up -d

# 查看日志
docker-compose logs -f app

# 停止服务
docker-compose down
```

### 3. 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 初始化数据库
psql -U btc_user -d btc_agent -f src/database/schema.sql

# 启动应用
python -m src.main
```

## API 接口

- `GET /` - 系统状态
- `GET /health` - 健康检查
- `POST /analyze/manual` - 手动触发分析
- `GET /signals/latest` - 获取最新信号

访问: http://localhost:8000/docs 查看完整 API 文档

## 项目结构

```
.
├── src/
│   ├── agents/              # 智能体层
│   │   ├── base_agent.py
│   │   ├── technical_agents.py    # 技术分析Agent
│   │   ├── news_agents.py         # 新闻分析Agent
│   │   ├── consensus_agents.py    # 共识Agent
│   │   └── decision_agents.py     # 决策/讨论/反思Agent
│   ├── data_collectors/     # 数据采集
│   │   ├── price_collector.py
│   │   └── news_collector.py
│   ├── database/            # 数据库
│   │   ├── models.py
│   │   ├── connection.py
│   │   └── schema.sql
│   ├── workflow/            # LangGraph工作流
│   │   └── graph.py
│   ├── services/            # 服务层
│   │   └── notification_service.py
│   ├── scheduler/           # 定时任务
│   │   └── tasks.py
│   └── main.py              # 主程序
├── config.yaml              # 配置文件
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## 工作流程

1. **数据采集** (每 5 分钟)

   - 从 OKX/Binance 获取价格数据
   - 从 CryptoPanic/CoinDesk 获取新闻

2. **并行分析** (每小时)

   - TechAgent-OpenAI + TechAgent-Gemini → 技术面分析
   - NewsAgent-OpenAI + NewsAgent-Gemini + RAGAgent → 新闻面分析

3. **共识融合**

   - TechConsensusAgent: 加权融合技术分析结果
   - NewsConsensusAgent: 加权融合新闻分析结果

4. **决策讨论**

   - DecisionAgent: 综合技术+新闻生成初步决策
   - DiscussionAgent: 多 Agent 辩论式讨论(3 轮)
   - ReflectionAgent: 基于历史表现反思调整

5. **通知发送**

   - 置信度 ≥ 0.8: 自动发送交易信号
   - 置信度 0.6-0.8: 发送人工审核提醒
   - 置信度 < 0.6: 仅记录不通知

6. **性能评估** (每日)
   - 回测历史信号准确率
   - 更新各 Agent 权重

## 数据库表结构

- `prices`: 价格与成交量数据
- `news`: 新闻摘要与情绪分数
- `signals`: 系统产生的买卖信号
- `feedback`: 历史信号结果与回测反馈
- `models_eval`: 各 Agent 的历史准确率与权重
- `agent_discussions`: Agent 讨论记录

## 配置说明

编辑 `config.yaml` 调整:

- Agent 权重分配
- 置信度阈值
- 讨论轮数
- 数据源选择
- 定时任务频率

## 监控与日志

```bash
# 查看实时日志
docker-compose logs -f app

# 查看数据库
docker-compose exec postgres psql -U btc_user -d btc_agent

# 查看Redis
docker-compose exec redis redis-cli
```

## 扩展开发

### 添加新的 Agent

```python
from src.agents.base_agent import BaseAgent

class MyCustomAgent(BaseAgent):
    def __init__(self):
        super().__init__("MyAgent", "model-name", weight=0.5)

    async def analyze(self, data):
        # 实现分析逻辑
        return self.format_output('BUY', 0.85, 'reasoning')
```

### 添加新的数据源

在 `src/data_collectors/` 中创建新的 collector 类，实现 `collect_all()` 方法。

## 注意事项

- 确保 API 密钥有效且有足够配额
- 生产环境建议使用更强的数据库密码
- 邮件通知需要配置 SendGrid 或其他 SMTP 服务
- 技术指标计算需要安装 TA-Lib 库

## License

MIT License
