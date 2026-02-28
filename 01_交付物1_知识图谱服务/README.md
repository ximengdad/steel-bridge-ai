# 钢箱梁知识图谱服务（简化版）

基于JSON-LD文件存储的知识图谱服务，无需Neo4j。

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 初始化数据
```bash
python init_data.py
```

这会创建 `data/kg_steel_bridge.jsonld` 示例数据文件。

### 3. 启动服务
```bash
python main.py
```

服务启动在 http://localhost:8000

### 4. 查看API文档
打开 http://localhost:8000/docs 查看自动生成的Swagger文档。

## 核心API

### 健康检查
```bash
curl http://localhost:8000/health
```

### 查询实体
```bash
curl "http://localhost:8000/kg/query?type=Beam&project_id=PRJ-20260115-001"
```

### 导出知识图谱（关键功能！）

```bash
# 导出全部数据（JSON-LD格式）
curl http://localhost:8000/kg/export

# 导出指定项目
curl "http://localhost:8000/kg/export?project_id=PRJ-20260115-001"

# 导出CSV格式
curl "http://localhost:8000/kg/export?format=csv"
```

## 数据格式

知识图谱采用JSON-LD格式（语义网标准），可直接被大模型读取。

## 与交付物2集成

交付物2通过调用 `/kg/export` 接口获取知识图谱数据，加载到大模型上下文。

示例：
```python
import requests

# 从交付物1导出知识图谱
response = requests.get("http://localhost:8000/kg/export")
kg_data = response.json()

# 在大模型中使用
prompt = f"基于以下知识：{kg_data}\n回答问题：..."
```

## 替换为你的数据

将你的数据转换为JSON-LD格式，替换 `data/kg_steel_bridge.jsonld` 即可。
