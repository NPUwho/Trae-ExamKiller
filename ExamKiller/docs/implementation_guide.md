# ExamKiller - 项目实施指南

## 一、项目概述

### 1.1 项目背景与目标

ExamKiller是一款基于人工智能技术的综合性学习辅助工具，旨在为大学生提供智能化的考试复习解决方案。平台通过集成先进的OCR文字识别、自然语言处理、知识图谱构建和智能出题等AI能力，帮助学生更高效地备考。本项目的核心目标是利用人工智能技术改变传统的复习模式，实现从被动刷题到主动理解、从盲目复习到精准定位的转变。

平台采用微服务架构设计，支持弹性扩展和高并发访问。前端采用现代化的响应式设计，适配PC端、平板和手机等多种终端设备。后端基于Python和FastAPI构建，充分利用AI模型的强大能力，同时保证接口的高性能和稳定性。整体技术栈经过精心选型，既考虑了开发效率，也兼顾了系统性能和可维护性。

### 1.2 核心功能模块

平台包含四大核心功能模块，每个模块都经过精心设计以满足用户的实际需求。试卷上传与分析模块支持多格式文件的上传和处理，包括PDF、Word文档以及各类图片格式，通过集成OCR技术实现试卷内容的自动识别和结构化存储。AI出题系统基于Transformer架构和学科知识图谱，能够根据用户输入的复习要点智能生成高质量的模拟试题，并支持自定义难度分布和题型设置。知识库管理模块帮助用户构建和管理个人知识网络，通过可视化方式展示知识点之间的关联关系。文档导出模块则提供多格式文档生成能力，支持Markdown、Word和PDF等常见格式的导出，并提供多种专业排版模板。

### 1.3 技术架构总览

平台采用分层微服务架构，将系统划分为接入层、网关层、服务层和数据层四个主要层次。接入层负责处理来自不同终端设备的请求，包括Web应用、移动端和第三方集成。网关层承担认证授权、流量控制和请求路由等职责。服务层包含多个独立部署的微服务，分别负责用户管理、试卷处理、OCR识别、AI出题、文档导出等核心业务。数据层则由PostgreSQL主库、Redis缓存、Elasticsearch搜索引擎和MinIO对象存储组成，提供稳定可靠的数据持久化能力。

整体架构遵循高可用、高性能、易扩展的设计原则。各服务之间通过gRPC进行高效的内部通信，对外则暴露RESTful API接口。容器化部署方案使用Docker和Kubernetes，实现服务的自动化部署、弹性伸缩和故障自愈。

## 二、开发环境配置

### 2.1 硬件要求

开发环境的硬件配置直接影响开发效率和系统性能。对于前端开发，推荐配置为8核以上CPU、16GB以上内存和256GB以上的SSD存储空间。对于后端开发和AI模型相关工作，建议使用16核以上CPU、32GB以上内存和500GB以上的SSD存储空间。如果需要运行完整的AI模型进行本地测试，显卡配置也很重要，NVIDIA RTX 3060或更高规格的显卡可以显著加速模型推理。开发过程中需要同时运行多个服务，充足的内存和CPU资源可以避免资源竞争导致的性能瓶颈。

测试环境和生产环境的硬件配置要求更高。测试环境应尽量模拟生产环境的配置，以便发现潜在的性能问题。生产环境的硬件配置需要根据预期用户规模和并发访问量进行详细规划，通常建议使用多节点集群部署以保证系统的高可用性。

### 2.2 操作系统与基础软件

项目推荐运行在Ubuntu 22.04 LTS或CentOS 8以上版本的Linux操作系统上。这些系统具有良好的软件包管理支持和丰富的文档资源，能够简化开发和部署过程。macOS系统也可以用于开发，但需要注意某些Linux专有的特性在macOS上可能需要额外配置。Windows系统推荐使用WSL2（Windows Subsystem for Linux 2）来运行开发环境，以获得接近原生Linux的开发体验。

基础软件安装清单包括：Docker Engine 24.0及以上版本用于容器化部署；Docker Compose 2.20及以上版本用于本地编排测试；Git 2.40及以上版本用于版本控制；Python 3.11或更高版本用于后端开发；Node.js 18 LTS及以上版本用于前端构建；PostgreSQL 15客户端工具用于数据库操作。安装这些软件时，建议使用官方APT或YUM源，以获取最新稳定版本。

### 2.3 Python环境配置

后端开发基于Python 3.11版本，推荐使用pyenv进行Python版本管理。pyenv允许在同一系统上安装和切换多个Python版本，避免全局安装带来的版本冲突。安装pyenv后，执行以下命令安装并配置Python 3.11：

```bash
# 安装Python 3.11
pyenv install 3.11.0

# 设置全局Python版本
pyenv global 3.11.0

# 创建项目虚拟环境
pyenv virtualenv 3.11.0 ai-exam-platform

# 激活虚拟环境
pyenv activate ai-exam-platform

# 升级pip
pip install --upgrade pip
```

项目依赖通过requirements.txt文件管理，主要依赖包括：FastAPI 0.109.0用于构建高性能API服务；Uvicorn 0.27.0作为ASGI服务器；SQLAlchemy 2.0.25用于数据库操作；Pydantic 2.5.3用于数据验证；python-jose 3.3.0用于JWT令牌处理；passlib 1.7.4用于密码加密；python-multipart 0.0.6用于文件上传处理。安装依赖时建议使用国内镜像源以提高下载速度：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2.4 前端开发环境

前端项目基于React 18和TypeScript构建，使用Vite 5作为构建工具。Node.js推荐使用nvm（Node Version Manager）进行版本管理。首先安装并配置Node.js环境：

```bash
# 安装nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash

# 安装Node.js 18 LTS
nvm install 18
nvm use 18
nvm alias default 18

# 验证安装
node --version
npm --version
```

前端项目初始化步骤如下：

```bash
# 进入项目前端目录
cd AIExamPlatform/frontend

# 安装依赖
npm install

# 安装UI组件库和工具库
npm install antd@5.12.8 @ant-design/icons@5.2.6 tailwindcss postcss autoprefixer

# 初始化TailwindCSS
npx tailwindcss init -p
```

前端项目结构采用标准的React项目布局：src目录包含源代码，components目录存放可复用组件，pages目录存放页面组件，services目录存放API调用逻辑，utils目录存放工具函数，hooks目录存放自定义Hook，styles目录存放全局样式。

### 2.5 数据库环境配置

开发环境使用PostgreSQL 15作为主数据库。安装PostgreSQL后，需要创建数据库和用户：

```bash
# 安装PostgreSQL
sudo apt install postgresql-15 postgresql-15-contrib

# 启动服务
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 切换到postgres用户
sudo -i -u postgres

# 进入PostgreSQL命令行
psql

# 创建数据库
CREATE DATABASE ai_exam_platform;

# 创建数据库用户
CREATE USER exam_user WITH ENCRYPTED PASSWORD 'your_password';

# 授予权限
GRANT ALL PRIVILEGES ON DATABASE ai_exam_platform TO exam_user;

# 连接到数据库并授予Schema权限
\c ai_exam_platform
GRANT ALL ON SCHEMA public TO exam_user;
```

Redis缓存的安装和配置相对简单：

```bash
# 安装Redis
sudo apt install redis-server

# 启动服务
sudo systemctl start redis
sudo systemctl enable redis

# 测试连接
redis-cli ping
```

Elasticsearch用于全文检索功能，安装时需要注意Java环境的配置：

```bash
# 安装Elasticsearch 8
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-8.11.0-amd64.deb
sudo dpkg -i elasticsearch-8.11.0-amd64.deb

# 配置网络
sudo tee /etc/elasticsearch/elasticsearch.yml > /dev/null <<EOF
cluster.name: ai-exam-cluster
node.name: node-1
network.host: 127.0.0.1
http.port: 9200
discovery.type: single-node
xpack.security.enabled: false
EOF

# 启动服务
sudo systemctl start elasticsearch
sudo systemctl enable elasticsearch
```

### 2.6 AI模型环境配置

AI功能是本平台的核心竞争力，需要配置相应的模型运行环境。首先安装深度学习框架：

```bash
# 安装PyTorch（CUDA版本，需要NVIDIA驱动支持）
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 安装Transformers用于预训练模型
pip install transformers==4.36.2

# 安装PaddleOCR用于中文OCR
pip install paddlepaddle-gpu==2.6.0.post118 -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install paddleocr==2.7.0.3

# 安装其他AI相关库
pip install sentence-transformers==2.2.2 langchain==0.1.5
```

模型文件较大，首次使用时需要从HuggingFace等平台下载。建议配置国内镜像源加速下载：

```python
# 在代码中配置镜像
from transformers import AutoModel, AutoTokenizer

model_name = "hfl/chinese-bert-wwm-ext"
tokenizer = AutoTokenizer.from_pretrained(model_name, mirror='tfsimple')
model = AutoModel.from_pretrained(model_name, mirror='tfsimple')
```

## 三、项目部署

### 3.1 Docker容器化部署

项目采用Docker容器化部署，所有服务都打包为独立的Docker镜像。首先创建Dockerfile：

```dockerfile
# 后端Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY backend/ ./backend/

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```dockerfile
# 前端Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: exam-postgres
    environment:
      POSTGRES_DB: ai_exam_platform
      POSTGRES_USER: exam_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U exam_user -d ai_exam_platform"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: exam-redis
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  elasticsearch:
    image: elasticsearch:8.11.0
    container_name: exam-elasticsearch
    environment:
      - discovery.type=single-node
      - ES_JAVA_OPTS=-Xms512m -Xmx512m
    volumes:
      - es_data:/usr/share/elasticsearch/data
    ports:
      - "9200:9200"
      - "9300:9300"
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:9200/_cluster/health || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 5

  minio:
    image: minio/minio:latest
    container_name: exam-minio
    command: server /data --console-address ":9001"
    volumes:
      - minio_data:/data
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      MINIO_ROOT_USER: ${MINIO_ROOT_USER}
      MINIO_ROOT_PASSWORD: ${MINIO_ROOT_PASSWORD}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 20s
      retries: 3

  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    container_name: exam-backend
    environment:
      - DATABASE_URL=postgresql+asyncpg://exam_user:${DB_PASSWORD}@postgres:5432/ai_exam_platform
      - REDIS_URL=redis://redis:6379/0
      - ELASTICSEARCH_URL=http://elasticsearch:9200
      - MINIO_ENDPOINT=minio:9000
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    ports:
      - "8000:8000"
    volumes:
      - ./uploads:/app/uploads

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: exam-frontend
    depends_on:
      - backend
    ports:
      - "80:80"

volumes:
  postgres_data:
  redis_data:
  es_data:
  minio_data:
```

部署步骤：

```bash
# 1. 克隆代码仓库
git clone https://github.com/your-org/ai-exam-platform.git
cd ai-exam-platform

# 2. 配置环境变量
cp .env.example .env
# 编辑.env文件，填入实际的配置值

# 3. 构建并启动服务
docker-compose up -d --build

# 4. 查看服务状态
docker-compose ps

# 5. 查看日志
docker-compose logs -f
```

### 3.2 Kubernetes生产部署

生产环境推荐使用Kubernetes进行容器编排。首先创建命名空间和配置：

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ai-exam-platform
  labels:
    app: ai-exam-platform
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: exam-config
  namespace: ai-exam-platform
data:
  DATABASE_URL: "postgresql+asyncpg://exam_user:password@postgres-service:5432/ai_exam_platform"
  REDIS_URL: "redis://redis-service:6379/0"
  ELASTICSEARCH_URL: "http://elasticsearch-service:9200"
  MINIO_ENDPOINT: "minio-service:9000"
---
apiVersion: v1
kind: Secret
metadata:
  name: exam-secrets
  namespace: ai-exam-platform
type: Opaque
stringData:
  SECRET_KEY: "your-production-secret-key-at-least-32-chars"
  DB_PASSWORD: "your-secure-database-password"
```

数据库StatefulSet配置：

```yaml
# postgres-statefulset.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: ai-exam-platform
spec:
  serviceName: postgres-service
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        envFrom:
        - secretRef:
            name: exam-secrets
        - configMapRef:
            name: exam-config
        volumeMounts:
        - name: postgres-data
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          exec:
            command: ["pg_isready", "-U", "exam_user"]
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command: ["pg_isready", "-U", "exam_user"]
          initialDelaySeconds: 5
          periodSeconds: 5
  volumeClaimTemplates:
  - metadata:
      name: postgres-data
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: ssd
      resources:
        requests:
          storage: 50Gi
```

后端服务Deployment配置：

```yaml
# backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: ai-exam-platform
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: exam-platform/backend:latest
        envFrom:
        - secretRef:
            name: exam-secrets
        - configMapRef:
            name: exam-config
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /api/health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchLabels:
                  app: backend
              topologyKey: kubernetes.io/hostname
```

水平自动伸缩配置：

```yaml
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
  namespace: ai-exam-platform
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100
        periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
```

Ingress配置：

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: exam-ingress
  namespace: ai-exam-platform
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/proxy-body-size: "100m"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "300"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "300"
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - api.exam-platform.com
    secretName: exam-tls
  rules:
  - host: api.exam-platform.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 8000
```

### 3.3 CI/CD流水线配置

使用GitLab CI进行持续集成和持续部署：

```yaml
# .gitlab-ci.yml
stages:
  - lint
  - test
  - build
  - deploy

variables:
  DOCKER_DRIVER: overlay2
  DOCKER_TLS_CERTDIR: ""
  FRONTEND_DIR: frontend
  BACKEND_DIR: backend

flake8:
  stage: lint
  image: python:3.11
  script:
    - pip install flake8
    - cd backend && flake8 --max-line-length=120 .

eslint:
  stage: lint
  image: node:18
  script:
    - cd $FRONTEND_DIR && npm ci && npm run lint

pytest:
  stage: test
  image: python:3.11
  services:
    - postgres:15-alpine
    - redis:7-alpine
  variables:
    POSTGRES_DB: test_db
    POSTGRES_USER: test_user
    POSTGRES_PASSWORD: test_pass
  script:
    - pip install -r backend/requirements.txt
    - cd backend && pytest --cov=. --cov-report=xml

build-backend:
  stage: build
  image: docker:24.0
  services:
    - docker:24.0-dind
  script:
    - docker build -t $CI_REGISTRY_IMAGE/backend:$CI_COMMIT_SHA ./backend
    - docker push $CI_REGISTRY_IMAGE/backend:$CI_COMMIT_SHA
  only:
    - main
    - develop

build-frontend:
  stage: build
  image: node:18
  script:
    - cd $FRONTEND_DIR && npm ci && npm run build
    - docker build -t $CI_REGISTRY_IMAGE/frontend:$CI_COMMIT_SHA ./frontend
    - docker push $CI_REGISTRY_IMAGE/frontend:$CI_COMMIT_SHA
  only:
    - main
    - develop

deploy-staging:
  stage: deploy
  image: bitnami/kubectl:latest
  script:
    - kubectl config use-context staging
    - kubectl set image deployment/backend backend=$CI_REGISTRY_IMAGE/backend:$CI_COMMIT_SHA -n ai-exam-platform
    - kubectl set image deployment/frontend frontend=$CI_REGISTRY_IMAGE/frontend:$CI_COMMIT_SHA -n ai-exam-platform
  only:
    - develop
  environment:
    name: staging
    url: https://staging.exam-platform.com

deploy-production:
  stage: deploy
  image: bitnami/kubectl:latest
  script:
    - kubectl config use-context production
    - kubectl set image deployment/backend backend=$CI_REGISTRY_IMAGE/backend:$CI_COMMIT_SHA -n ai-exam-platform
    - kubectl set image deployment/frontend frontend=$CI_REGISTRY_IMAGE/frontend:$CI_COMMIT_SHA -n ai-exam-platform
  only:
    - main
  environment:
    name: production
    url: https://exam-platform.com
  when: manual
```

## 四、API接口文档

### 4.1 认证模块

用户认证模块提供用户注册、登录和Token刷新等功能。JWT令牌采用RS256算法签名，令牌有效期为7天，支持刷新机制延长会话时间。

**用户注册接口**

请求路径为POST /api/v1/auth/register，请求体包含email、name和password三个必填字段。email字段需要进行格式验证，密码要求至少8个字符且包含字母和数字。注册成功后返回access_token和user信息。email字段具有唯一性约束，已注册邮箱无法重复注册。

**用户登录接口**

请求路径为POST /api/v1/auth/login，请求体包含email和password两个字段。登录验证用户凭据的准确性，验证通过后生成JWT令牌返回给客户端。登录失败会返回401状态码和具体的错误信息。登录接口有频率限制，连续失败5次后将触发账户锁定机制。

**获取用户信息**

请求路径为GET /api/v1/users/profile，需要在请求头中携带Bearer Token。该接口返回当前登录用户的详细信息，包括用户ID、邮箱、昵称、角色、注册时间等。Token验证失败会返回401错误，需要重新登录获取有效令牌。

### 4.2 试卷管理模块

试卷管理模块提供试卷上传、查询、删除和分析等功能。试卷文件支持PDF、Word和图片格式，单个文件大小限制为50MB。

**上传试卷**

请求路径为POST /api/v1/papers/upload，采用multipart/form-data格式提交。请求参数包括：file（试卷文件）、title（试卷标题）、subject（学科类别）、course（课程名称）、chapter（章节范围，可选）、difficulty（难度系数，1-5）、exam_date（考试日期，可选）。上传成功后返回试卷的完整信息，包括自动生成的试卷ID和初始分析状态。上传过程采用分片上传机制，支持断点续传。

**获取试卷列表**

请求路径为GET /api/v1/papers，支持分页和筛选参数。分页参数包括page（页码，从1开始）和page_size（每页数量，默认20）。筛选参数包括subject（学科）、course（课程）、difficulty（难度）和analysis_status（分析状态）。返回结果包含试卷列表和分页信息，每条记录包含试卷的基本元数据。

**获取试卷详情**

请求路径为GET /api/v1/papers/{paper_id}，返回指定试卷的完整信息，包括分析结果、题目列表等。试卷属于用户私有资源，只能访问自己上传的试卷。返回的数据中包含analysis_result字段，存储OCR识别和结构化分析的结果。

**分析试卷**

请求路径为POST /api/v1/papers/{paper_id}/analyze，触发试卷的AI分析流程。分析过程包括OCR文字识别、版式分析、题目提取和知识点标注。分析是异步执行的，接口立即返回但分析结果需要通过轮询或WebSocket推送获取。分析完成后，试卷的analysis_status变为completed，同时更新question_count和knowledge_points字段。

**删除试卷**

请求路径为DELETE /api/v1/papers/{paper_id}，删除指定的试卷及其关联的题目和文件。删除操作不可逆，系统会同时清理存储在对象存储中的文件。批量删除可以通过在请求体中传递多个paper_id实现。

### 4.3 AI出题模块

AI出题模块根据用户输入的复习要点生成高质量的模拟试题，支持自定义难度分布和题型设置。

**生成题目**

请求路径为POST /api/v1/questions/generate，请求体包含review_input（复习内容）和settings（生成设置）两个对象。review_input包含text（文本内容）和source_type（来源类型）。settings包含question_count（题目数量）、easy_ratio（简单题比例）、medium_ratio（中难题比例）、hard_ratio（困难题比例）和question_types（题型列表）。生成过程首先对输入文本进行知识点提取，然后结合知识图谱和出题策略生成符合要求的题目。返回结果包含题目列表、总数和预计用时。

**获取题目详情**

请求路径为GET /api/v1/questions/{question_id}，返回指定题目的完整信息，包括题目内容、类型、难度、答案、解析等。AI生成的题目还会返回生成参数，包括使用的知识点和生成策略。

**获取知识图谱**

请求路径为GET /api/v1/knowledge/graph，返回指定学科或课程的知识图谱数据。图谱采用节点和边的形式组织，节点代表知识点，边代表知识点之间的关系。节点信息包括id、name、importance（重要性级别）和位置信息。边信息包括source和target表示关联的两个节点。

**提取知识点**

请求路径为POST /api/v1/knowledge/extract，对输入的文本进行知识点提取。返回提取到的知识点列表，每个知识点包含名称、重要性级别、描述和跨学科关联信息。提取结果按照重要性排序，核心知识点排在最前面。

### 4.4 文档导出模块

文档导出模块将复习资料生成为多种格式的文档，支持专业排版和自定义设置。

**生成文档**

请求路径为POST /api/v1/exports/generate，请求体包含导出设置。设置参数包括：title（文档标题）、template（模板类型，可选academic、modern、compact、colorful）、include_overview（是否包含知识点概述）、include_examples（是否包含典型例题）、include_solutions（是否包含解题思路）、include_practice（是否包含练习题目）、header_text（页眉内容）、footer_text（页脚内容）、add_watermark（是否添加水印）、add_page_numbers（是否添加页码）、highlight_knowledge（是否高亮知识点）。生成是异步过程，返回任务ID供后续查询状态。

**下载文档**

请求路径为GET /api/v1/exports/{export_id}/download，返回文档的下载链接。链接具有时效性，有效期为24小时。下载前需要先确认导出任务已完成。文档格式支持Markdown（GFM规范）、Word（Office 2016+兼容）和PDF（支持文本搜索和书签导航）。

**预览文档**

请求路径为GET /api/v1/exports/{export_id}/preview，返回文档的HTML预览内容。预览页面展示文档的排版效果和内容组织，可以在线阅读无需下载。预览链接的有效期为1小时。

## 五、运维监控

### 5.1 日志管理

项目采用集中式日志管理架构，所有服务的日志通过Fluentd收集后存储在Elasticsearch中，通过Kibana进行可视化查询和分析。日志格式采用JSON结构，包含时间戳、日志级别、服务名称、请求ID、用户ID和具体消息等字段。

```json
{
  "timestamp": "2024-01-15T10:30:00.000Z",
  "level": "INFO",
  "service": "backend",
  "request_id": "req_abc123",
  "user_id": "user_xyz789",
  "message": "试卷分析完成",
  "context": {
    "paper_id": "paper_123",
    "question_count": 45,
    "processing_time_ms": 3250
  }
}
```

日志级别规范：DEBUG用于开发调试信息，INFO用于正常业务日志，WARNING用于异常但不影响功能的情况，ERROR用于需要关注的错误，CRITICAL用于系统级严重错误。生产环境默认日志级别为INFO，排查问题时可以临时调整为DEBUG。

日志查询示例（Kibana Query Language）：

```
# 查询特定用户的操作日志
user_id : "user_xyz789"

# 查询最近1小时的错误日志
level : "ERROR" AND @timestamp > now-1h

# 查询特定试卷的分析日志
context.paper_id : "paper_123"
```

### 5.2 监控指标

项目使用Prometheus收集监控指标，Grafana进行可视化展示。关键监控指标包括：

**应用层指标**

QPS（每秒请求数）反映系统的吞吐能力，正常运行时应维持在预期范围内。请求延迟分布（p50、p90、p99）用于评估系统响应性能，目标是p99延迟小于1秒。错误率反映系统的稳定性，正常情况应低于0.1%。活跃连接数用于评估系统负载情况。

**基础设施指标**

CPU使用率反映计算资源的消耗情况，目标是不超过80%。内存使用率反映内存资源消耗，目标是维持在70%以下。磁盘I/O反映存储子系统的性能，频繁的读写操作可能成为瓶颈。网络带宽反映数据传输的负载情况。

**业务层指标**

试卷分析成功率反映OCR和AI模块的稳定性。题目生成质量评分反映AI模型的输出质量。用户活跃度反映平台的受欢迎程度。文档导出成功率反映导出模块的稳定性。

### 5.3 告警配置

告警规则通过Prometheus Alertmanager进行管理：

```yaml
# alerting-rules.yml
groups:
- name: ai-exam-platform
  rules:
  # CPU使用率告警
  - alert: HighCPUUsage
    expr: rate(container_cpu_usage_seconds_total{namespace="ai-exam-platform"}[5m]) > 0.8
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "CPU使用率过高"
      description: "服务 {{ $labels.pod }} 的CPU使用率超过80%"
  
  # 内存使用率告警
  - alert: HighMemoryUsage
    expr: container_memory_usage_bytes{namespace="ai-exam-platform"} / container_spec_memory_limit_bytes > 0.85
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "内存使用率过高"
      description: "服务 {{ $labels.pod }} 的内存使用率超过85%"
  
  # 错误率告警
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.01
    for: 3m
    labels:
      severity: critical
    annotations:
      summary: "错误率过高"
      description: "服务 {{ $labels.pod }} 的5xx错误率超过1%"
  
  # 响应延迟告警
  - alert: HighLatency
    expr: histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m])) > 1
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "响应延迟过高"
      description: "服务 {{ $labels.pod }} 的99分位延迟超过1秒"
  
  # 服务不可用告警
  - alert: ServiceDown
    expr: up{namespace="ai-exam-platform"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "服务不可用"
      description: "服务 {{ $labels.pod }} 不可用"
```

告警通知渠道配置：

```yaml
# alertmanager.yml
global:
  resolve_timeout: 5m

route:
  group_by: ['alertname']
  receiver: 'default-receiver'
  routes:
  - match:
      severity: critical
    receiver: 'critical-receiver'
    continue: true
  - match:
      severity: warning
    receiver: 'warning-receiver'

receivers:
- name: 'default-receiver'
  email_configs:
  - to: 'alerts@example.com'
    send_resolved: true
  webhook_configs:
  - url: 'http://dingtalk-webhook:8060/dingtalk/webhook'

- name: 'critical-receiver'
  email_configs:
  - to: 'critical@example.com'
    send_resolved: true
  webhook_configs:
  - url: 'http://dingtalk-webhook:8060/dingtalk/webhook?at=all'
```

### 5.4 性能优化

**数据库优化**

为高频查询创建合适的索引，定期执行ANALYZE更新统计信息。使用EXPLAIN ANALYZE分析慢查询的执行计划，优化低效的查询语句。配置合适的连接池大小，PostgreSQL的连接池建议设置为CPU核心数的2-3倍。对于复杂查询，使用物化视图缓存中间结果。

**缓存优化**

Redis缓存采用分级策略：热点数据缓存1小时，普通数据缓存5分钟，实时数据不缓存。使用Redis Pipeline批量操作减少网络开销。配置合理的内存淘汰策略，LRU（最近最少使用）适合缓存场景。开启Redis持久化功能，AOF持久化配置为everysec模式。

**应用优化**

使用异步处理IO密集型任务，避免阻塞主线程。合理设置超时时间，避免请求长时间挂起。使用连接池复用数据库连接，减少连接创建开销。对静态资源启用Gzip压缩，减少传输数据量。使用CDN加速静态资源的分发。

**AI模型优化**

模型量化减少模型体积和推理时间，INT8量化可以在保持精度的前提下将推理速度提升2-3倍。模型剪枝移除不重要的参数，进一步压缩模型。使用TensorRT或ONNX Runtime等推理优化框架。批处理推理合并多个请求，提高GPU利用率。模型预热减少首次推理的冷启动延迟。

## 六、安全保障

### 6.1 身份认证与授权

系统采用JWT令牌进行身份认证，令牌包含用户ID、角色和过期时间等信息。采用RS256算法签名，私钥保存在密钥管理系统中，公钥暴露给客户端验证。令牌有效期为7天，支持刷新机制延长会话。敏感操作（如删除试卷）需要重新验证密码。

权限控制采用RBAC（基于角色的访问控制）模型。系统定义三种角色：学生（Student）可以上传试卷、生成题目、导出文档；教师（Teacher）除学生权限外，还可以管理共享资源、查看统计数据；管理员（Admin）拥有全部权限，包括用户管理、系统配置等。角色权限存储在数据库中，支持动态调整。

### 6.2 数据安全

用户密码采用bcrypt算法加密存储，Cost Factor设置为12。每个密码都有唯一的盐值，防止彩虹表攻击。数据库启用SSL连接，传输过程加密。敏感数据（如API密钥）使用专门的密钥管理服务存储，不直接写入代码或配置文件。

数据备份采用3-2-1策略：保留3份数据副本，存储在2种不同的介质上，其中1份保存在异地。备份数据加密存储，定期进行恢复演练验证备份有效性。数据库连接信息通过环境变量注入，不硬编码在代码中。

### 6.3 网络安全

API接口启用CORS严格配置，只允许指定的域名访问。请求体大小限制在100MB，防止恶意上传超大文件。启用Rate Limiting限制单IP的请求频率，防止DDoS攻击。请求头中的X-Frame-Options设置为SAMEORIGIN，防止点击劫持。

HTTPS强制跳转，所有API必须通过HTTPS访问。证书使用Let's Encrypt签发的免费证书，通过cert-manager自动续期。敏感接口（如登录）增加额外的验证码验证。Web应用防火墙（WAF）过滤常见的攻击请求，如SQL注入、XSS跨站脚本等。

### 6.4 审计追踪

所有敏感操作都记录在操作日志中，包括操作人、操作时间、操作内容和操作结果。日志不可修改和删除，防止篡改审计记录。定期导出审计日志进行分析，识别异常行为模式。安全事件触发实时告警，安全团队及时响应处置。

审计日志保留期限为1年，满足合规要求。法律相关的审计日志根据案件需要延长保留期限。审计日志与用户身份关联，可以追溯到具体的操作人员和时间点。

## 七、项目结构

### 7.1 前端项目结构

```
frontend/
├── public/                    # 静态资源目录
│   ├── favicon.ico
│   └── robots.txt
├── src/
│   ├── assets/                # 资源文件
│   │   ├── images/
│   │   └── icons/
│   ├── components/            # 公共组件
│   │   ├── common/            # 通用组件
│   │   │   ├── Button/
│   │   │   ├── Input/
│   │   │   └── Modal/
│   │   ├── layout/            # 布局组件
│   │   │   ├── Header/
│   │   │   ├── Sidebar/
│   │   │   └── Footer/
│   │   └── business/          # 业务组件
│   │       ├── PaperUploader/
│   │       ├── QuestionGenerator/
│   │       └── KnowledgeGraph/
│   ├── pages/                 # 页面组件
│   │   ├── Home/
│   │   ├── Upload/
│   │   ├── Generate/
│   │   ├── Knowledge/
│   │   └── Export/
│   ├── services/              # API服务
│   │   ├── api.js             # Axios实例
│   │   ├── auth.js            # 认证接口
│   │   ├── paper.js           # 试卷接口
│   │   └── question.js        # 题目接口
│   ├── store/                 # 状态管理
│   │   └── index.js           # Zustand Store
│   ├── hooks/                 # 自定义Hook
│   │   ├── useAuth.js
│   │   ├── usePaper.js
│   │   └── useAI.js
│   ├── utils/                 # 工具函数
│   │   ├── format.js
│   │   ├── validate.js
│   │   └── constants.js
│   ├── styles/                # 全局样式
│   │   ├── index.css
│   │   └── variables.css
│   ├── App.jsx
│   └── main.jsx
├── .env                       # 环境变量
├── .eslintrc.js               # ESLint配置
├── tailwind.config.js         # Tailwind配置
└── vite.config.js             # Vite配置
```

### 7.2 后端项目结构

```
backend/
├── api/                       # API入口
│   ├── __init__.py
│   ├── main.py                # FastAPI应用
│   ├── routes/                # 路由定义
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── papers.py
│   │   ├── questions.py
│   │   ├── knowledge.py
│   │   └── exports.py
│   └── middleware/            # 中间件
│       ├── __init__.py
│       ├── auth.py
│       ├── cors.py
│       └── logging.py
├── services/                  # 业务逻辑
│   ├── __init__.py
│   ├── paper_analyzer.py      # 试卷分析
│   ├── ai_generator.py        # AI生成
│   ├── knowledge_extractor.py # 知识提取
│   ├── document_exporter.py   # 文档导出
│   └── ocr_service.py         # OCR服务
├── models/                    # 数据模型
│   ├── __init__.py
│   ├── user.py
│   ├── paper.py
│   ├── question.py
│   └── knowledge.py
├── schemas/                   # Pydantic模型
│   ├── __init__.py
│   ├── user.py
│   ├── paper.py
│   └── common.py
├── repositories/              # 数据访问
│   ├── __init__.py
│   ├── user_repository.py
│   └── paper_repository.py
├── database/                  # 数据库配置
│   ├── __init__.py
│   ├── connection.py
│   └── migrations/
├── utils/                     # 工具函数
│   ├── __init__.py
│   ├── file_utils.py
│   └── text_utils.py
├── requirements.txt
└── Dockerfile
```

## 八、快速开始

### 8.1 本地开发环境启动

```bash
# 1. 克隆项目
git clone https://github.com/your-org/ai-exam-platform.git
cd ai-exam-platform

# 2. 启动基础设施服务
docker-compose -f docker-compose.infra.yml up -d

# 3. 创建Python虚拟环境
pyenv virtualenv 3.11.0 exam-platform
pyenv activate exam-platform
pip install -r backend/requirements.txt

# 4. 安装前端依赖
cd frontend
npm install

# 5. 配置环境变量
cp .env.example .env
# 编辑.env文件，配置数据库连接等信息

# 6. 初始化数据库
cd backend
alembic upgrade head

# 7. 启动后端服务
uvicorn api.main:app --reload --port 8000

# 8. 启动前端开发服务器（新终端）
cd frontend
npm run dev
```

### 8.2 生产环境部署

```bash
# 1. 准备Kubernetes集群
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/configmap.yaml

# 2. 部署数据库
kubectl apply -f k8s/postgres-statefulset.yaml
kubectl apply -f k8s/postgres-service.yaml

# 3. 部署中间件
kubectl apply -f k8s/redis-deployment.yaml
kubectl apply -f k8s/elasticsearch-deployment.yaml
kubectl apply -f k8s/minio-deployment.yaml

# 4. 构建并推送镜像
docker build -t exam-platform/backend:latest ./backend
docker push exam-platform/backend:latest
docker build -t exam-platform/frontend:latest ./frontend
docker push exam-platform/frontend:latest

# 5. 部署应用
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-service.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml

# 6. 配置Ingress
kubectl apply -f k8s/ingress.yaml

# 7. 验证部署
kubectl get pods -n ai-exam-platform
kubectl get ingress -n ai-exam-platform
```

### 8.3 验证部署成功

```bash
# 1. 检查服务状态
curl http://localhost:8000/api/health

# 2. 检查前端页面
curl http://localhost:80

# 3. 查看应用日志
kubectl logs -f deployment/backend -n ai-exam-platform

# 4. 访问Swagger文档
# 浏览器打开 http://localhost:8000/api/docs
```

## 九、常见问题排查

### 9.1 数据库连接问题

如果出现数据库连接失败的错误，首先检查PostgreSQL服务是否正常运行。使用docker ps或kubectl命令确认数据库Pod处于Running状态。检查连接字符串是否正确，包括主机地址、端口、用户名和密码。确认数据库已经创建了对应的数据库和用户，并且用户具有访问权限。检查防火墙设置，确保数据库端口已开放。

```bash
# 排查步骤
docker exec -it exam-postgres psql -U exam_user -d ai_exam_platform
\dt
SELECT 1;
```

### 9.2 缓存服务问题

Redis连接问题通常表现为请求响应缓慢或间歇性失败。检查Redis服务状态，确认服务正常运行。验证Redis连接字符串和密码配置是否正确。检查Redis内存使用情况，如果内存已满可能导致连接拒绝。确认Redis的maxclients配置允许足够的连接数。

```bash
# 排查步骤
redis-cli ping
redis-cli info memory
redis-cli client list
```

### 9.3 AI模型加载问题

AI功能不可用可能由多种原因导致。首先确认PyTorch和Transformers库已正确安装，且版本兼容。检查模型文件是否已下载，首次运行会自动下载预训练模型。如果使用GPU加速，确认CUDA驱动版本与PyTorch版本兼容。模型加载需要较大内存，确保服务器有足够的可用内存。

```python
# 验证PyTorch安装
import torch
print(torch.__version__)
print(torch.cuda.is_available())

# 验证模型加载
from transformers import AutoModel, AutoTokenizer
model_name = "hfl/chinese-bert-wwm-ext"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)
print("模型加载成功")
```

### 9.4 文件上传问题

文件上传失败可能是由多种原因导致。检查上传文件大小是否超过限制，默认限制为50MB。确认上传目录具有写权限，Docker环境下需要挂载Volume。检查文件类型是否在允许的列表中（PDF、DOCX、JPG、PNG）。查看服务端日志获取详细的错误信息。

```javascript
// 前端常见错误处理
const handleUpload = async (file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    // 其他表单字段...
    await api.post('/papers/upload', formData);
  } catch (error) {
    if (error.response?.status === 413) {
      showToast('文件大小超过限制', 'error');
    } else if (error.response?.status === 415) {
      showToast('不支持的文件格式', 'error');
    } else {
      showToast('上传失败，请重试', 'error');
    }
  }
};
```

## 十、联系方式与支持

项目开发过程中如遇到问题，可以通过以下渠道获取帮助：查看项目文档中的常见问题部分；搜索GitHub Issues中是否有类似问题；创建新的Issue描述遇到的问题；在项目Wiki中查找详细的使用指南。团队承诺在工作日24小时内响应重要问题的咨询。

本实施指南会持续更新，请定期查阅最新版本以获取最新的部署说明和最佳实践。
