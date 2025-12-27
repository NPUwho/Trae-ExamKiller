# ExamKiller - 大学考试复习辅助平台

## 🚀 快速启动指南

### 1. 启动后端服务

```bash
cd ExamKiller/backend

# 安装依赖
pip install -r requirements.txt

# 启动服务
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
```

后端服务启动后访问：`http://localhost:8000`

### 2. 启动前端页面

**方式一：直接打开HTML文件**
- 在浏览器中直接打开 `ExamKiller/index.html`

**方式二：使用HTTP服务器（推荐）**
```bash
# 在ExamKiller目录下运行
python -m http.server 8001
```
然后访问：`http://localhost:8001`

### 3. 验证服务状态

打开浏览器控制台（F12），如果看到以下信息说明连接成功：
- 后端API健康检查通过
- 知识图谱加载成功
- 试卷列表正常显示

---

## ✨ 功能使用说明

### 📤 试卷上传与分析
1. 点击导航栏"试卷上传"
2. 填写试卷分类信息（学科、课程、章节）
3. 设置难度系数（1-5级）
4. 点击"选择文件"上传PDF/Word/图片文件
5. 观察上传进度和分析过程
6. 上传完成后自动显示在"已上传试卷"列表

### 🤖 AI智能出题
1. 点击导航栏"AI出题"
2. 选择输入方式：
   - **文本输入**：直接粘贴复习要点
   - **文件导入**：上传.txt或.docx文件
   - **语音输入**：点击麦克风开始录音
3. 点击"提取知识点"让AI分析文本
4. 设置出题参数：
   - 题目数量
   - 难度分布（简单/中等/困难比例）
   - 题型选择
5. 点击"开始生成"生成练习题
6. 查看生成的题目，支持导出

### 📚 知识库管理
1. 点击导航栏"知识库"
2. 查看知识点统计卡片
3. 查看交互式知识图谱
4. 使用筛选器按重要性查看知识点

### 📄 文档导出
1. 点击导航栏"文档导出"
2. 选择排版模板
3. 设置文档标题和包含内容
4. 点击导出按钮生成文档
5. 预览生成的复习资料

---

## 🔧 API接口说明

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/papers` | GET | 获取试卷列表 |
| `/api/papers/upload` | POST | 上传试卷 |
| `/api/papers/{id}` | DELETE | 删除试卷 |
| `/api/knowledge/extract` | POST | 提取知识点 |
| `/api/questions/generate` | POST | 生成题目 |
| `/api/knowledge/graph` | GET | 获取知识图谱 |
| `/api/exports/generate` | POST | 生成文档 |

---

## 🛠️ Qwen API 配置

项目已配置使用通义千问API：

```env
QWEN_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_API_KEY=sk-12835c34b4c744c59f1f24f3acef2b4d
QWEN_MODEL_NAME=qwen-plus
```

如需修改API配置，编辑 `backend/.env` 文件。

---

## 📁 项目结构

```
ExamKiller/
├── index.html              # 前端主页面
├── assets/
│   ├── css/styles.css      # 样式文件
│   └── js/app.js           # 前端逻辑
├── backend/
│   ├── api/
│   │   └── main.py         # FastAPI后端服务
│   ├── services/
│   │   ├── paper_analyzer.py
│   │   └── ai_generator.py
│   ├── requirements.txt    # Python依赖
│   └── .env               # 环境配置
└── docs/
    ├── database_design.md
    └── implementation_guide.md
```

---

## ⚠️ 常见问题

### Q: 点击功能没有反应？
A: 
1. 确保后端服务正在运行（端口8000）
2. 刷新页面后重试
3. 打开浏览器控制台查看错误信息

### Q: API请求失败？
A: 
1. 检查后端服务是否启动
2. 检查API密钥配置是否正确
3. 确认网络连接正常

### Q: 知识点提取失败？
A: 
1. 确保输入内容不为空
2. 检查Qwen API配额
3. 查看后端日志

---

## 📝 更新日志

**v1.0.0** (2024-12-26)
- 初始版本发布
- 集成Qwen API
- 实现核心功能模块
- 响应式UI设计
