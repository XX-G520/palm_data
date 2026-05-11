# Palm Data — NL2SQL 智能问数系统

基于 **LangGraph** 构建的 Text-to-SQL Agent，支持用户以自然语言查询数据库，自动生成并执行 SQL。

## 项目架构

```
palm_data/
├── app/
│   ├── agent/               # AI Agent 核心模块（LangGraph 工作流）
│   │   ├── nodes/           # 12 个工作流节点
│   │   ├── state.py         # Agent 状态定义
│   │   ├── context.py       # Agent 上下文/工具定义
│   │   ├── graph.py         # 工作流编排
│   │   └── llm.py           # LLM 客户端
│   ├── api/                 # FastAPI Web 接口
│   │   ├── routers/         # API 路由
│   │   ├── schemas/         # 请求/响应 Schema
│   │   ├── dependencies.py  # 依赖注入
│   │   └── lifespan.py      # 应用生命周期
│   ├── services/            # 业务服务层
│   │   ├── query_service.py           # 查询服务
│   │   └── meta__knowledge_service.py # 元知识构建服务
│   ├── repositories/        # 数据访问层（Repository 模式）
│   │   ├── mysql/           # MySQL 数据访问
│   │   ├── qdrant/          # Qdrant 向量检索引擎
│   │   └── es/              # Elasticsearch 全文检索引擎
│   ├── models/              # SQLAlchemy ORM 模型
│   ├── entities/            # 领域实体（dataclass）
│   ├── client/              # 外部服务客户端管理
│   ├── conf/                # 配置管理
│   ├── core/                # 核心工具（日志等）
│   ├── prompt/              # Prompt 加载器
│   └── scripts/             # 脚本工具
├── conf/                    # 配置文件（YAML）
│   ├── app_config.yaml      # 应用配置
│   └── meta_config.yaml     # 元数据配置（表/字段/指标定义）
├── docker/                  # Docker 部署文件
│   ├── docker-compose.yaml  # 容器编排
│   ├── mysql/               # MySQL 初始化 SQL
│   └── elasticsearch/       # ES Dockerfile
├── prompts/                 # LLM Prompt 模板
├── pyproject.toml           # 项目依赖
└── main.py                  # 应用入口
```

## 核心流程

```
用户提问："统计华北地区销售总额"
        │
        ▼
  extract_keywords    ←── 关键词提取（jieba + LLM扩展）
        │
   ┌────┼────┐
   ▼    ▼    ▼
recall  recall  recall
column  value   metric        ←── 三路并行召回
   │     │      │
   └────┼──────┘
        ▼
merge_retrieved_info         ←── 合并检索结果
        │
   ┌────┴────┐
   ▼         ▼
filter_table  filter_metric  ←── LLM 筛选相关表/指标
   │         │
   └────┬────┘
        ▼
 add_extra_context            ←── 补充维度外键关联
        │
        ▼
   generate_sql               ←── LLM 生成 SQL
        │
        ▼
   validate_sql               ←── 校验 SQL 语法
    │         │
  正确      错误
    │         │
    │    correct_sql           ←── LLM 修正 SQL
    │         │
    └────┬────┘
         ▼
      run_sql                 ←── 执行 SQL 返回结果
```

## 技术选型

| 组件            | 技术                 | 用途                  |
| ------------- | ------------------ | ------------------- |
| **工作流引擎**     | LangGraph          | Agent 节点编排、状态管理     |
| **Web 框架**    | FastAPI            | REST API + SSE 流式响应 |
| **LLM**       | OpenAI 兼容接口        | SQL 生成、关键词扩展、信息筛选   |
| **向量检索**      | Qdrant             | 字段(Column)的语义检索     |
| **全文检索**      | Elasticsearch + IK | 字段取值(Value)的精确匹配    |
| **元数据存储**     | MySQL              | 表/字段/指标元数据          |
| **数据仓库**      | MySQL (DW)         | 实际业务数据查询            |
| **Embedding** | HuggingFace TEI    | 文本向量化               |
| **中文分词**      | jieba              | 查询关键词提取             |
| **配置管理**      | OmegaConf          | YAML 配置加载与校验        |

## 快速开始

### 环境要求

- Python >= 3.12
- Docker & Docker Compose
- uv（Python 包管理器）

### 1. 克隆项目

```bash
git clone <仓库地址>
cd palm_data
```

### 2. 启动基础设施

```bash
cd docker
docker compose up -d
```

启动后会自动创建以下服务：

| 服务            | 端口   | 说明          |
| ------------- | ---- | ----------- |
| MySQL         | 3306 | 元数据库 + 数据仓库 |
| Elasticsearch | 9200 | 全文检索        |
| Kibana        | 5601 | ES 管理界面     |
| Qdrant        | 6333 | 向量数据库       |
| Embedding     | 8081 | 文本嵌入模型服务    |

### 3. 安装 Python 依赖

```bash
uv sync
```

### 4. 配置文件

编辑 `conf/app_config.yaml` 配置各服务的连接信息：

```yaml
db_meta:          # 元数据库
  host: localhost
  port: 3306
  user: atguigu
  password: Atguigu.123
  database: meta

db_dw:            # 数据仓库
  host: localhost
  port: 3306
  user: atguigu
  password: Atguigu.123
  database: dw

llm:              # 大模型配置
  model_name: gpt-4
  api_key: <你的 API Key>
  base_url: <API 地址>
```

### 5. 配置元数据

编辑 `conf/meta_config.yaml` 定义数据库中的表和字段信息（参考已有示例）。

### 6. 构建元知识库

将 `meta_config.yaml` 中定义的表、字段、指标信息同步到向量数据库和 ES：

```bash
python -m app.scripts.build_meta_knowledge -c conf/meta_config.yaml
```

### 7. 启动服务

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 8. 测试 API

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "统计各地区销售总额"}'
```

## 召回策略

| 数据类型     | 引擎            | 方式      | 示例                      |
| -------- | ------------- | ------- | ----------------------- |
| **字段名**  | Qdrant        | 向量语义相似度 | "销售额" ≈ "sales\_amount" |
| **字段取值** | Elasticsearch | 关键词精确匹配 | "北京" → "北京"、"北京市"       |
| **指标名**  | Qdrant        | 向量语义相似度 | "GMV" ≈ "成交总额"          |

**为什么字段用向量检索、取值用关键词检索？**

- 字段名有**描述语义**（如"订单金额"也可能被称为"销售额"、"revenue"），向量检索能理解同义词
- 取值需要**精确匹配**（如"北京"不能错配成"南京"），关键词检索更可靠

## ID 设计原则

项目采用 **语义 ID** 设计，ID 本身携带业务信息：

| 实体 | 格式               | 示例                          |
| -- | ---------------- | --------------------------- |
| 表  | `{表名}`           | `fact_order`                |
| 字段 | `{表名}.{字段名}`     | `fact_order.order_amount`   |
| 取值 | `{表名}.{字段名}.{值}` | `dim_region.region_name.华东` |
| 指标 | `{指标名}`          | `GMV`                       |

这种设计适合 NL2SQL 场景，因为生成 SQL 时必须明确"哪个表的哪个字段"。

## API 文档

启动服务后访问：`http://localhost:8000/docs` (Swagger UI)

### POST /api/query

**请求：**

```json
{
  "query": "2024年华东地区销售额最高的商品是什么？"
}
```

**响应：** SSE 流式事件，包含：

```json
{"type": "progress", "step": "抽取关键词", "status": "running"}
{"type": "progress", "step": "抽取关键词", "status": "success"}
{"type": "progress", "step": "召回字段", "status": "running"}
...
{"type": "result", "data": [...]}
```

## 架构分层

```
┌─────────────────────────┐
│       API Layer         │  ← FastAPI 路由 + 依赖注入
├─────────────────────────┤
│     Service Layer       │  ← 业务逻辑编排
├─────────────────────────┤
│    Agent Layer          │  ← LangGraph 工作流
├─────────────────────────┤
│   Repository Layer      │  ← 数据访问（MySQL/Qdrant/ES）
├─────────────────────────┤
│      Client Layer       │  ← 外部服务连接管理
├─────────────────────────┤
│    Infrastructure       │  ← MySQL/Qdrant/ES/Embedding
└─────────────────────────┘
```

## 项目特点

- **Agent 模式**：基于 LangGraph 的 12 节点工作流，支持条件路由和自动纠错
- **混合检索**：向量检索 + 全文检索，覆盖语义理解和精确匹配两种场景
- **流式响应**：SSE (Server-Sent Events) 实时推送处理进度
- **分层架构**：API → Service → Agent → Repository，职责清晰
- **依赖注入**：FastAPI `Depends` 实现解耦，方便测试
- **语义 ID**：ID 设计携带业务语义，天然适合 NL2SQL 场景
- **自动纠错**：SQL 校验失败后自动调用 LLM 修正

## License

内部项目，仅供学习与研究使用。
