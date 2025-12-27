# AI大学考试复习辅助平台 - 数据库设计

## 一、数据库概述

### 1.1 数据库选型

| 数据库 | 用途 | 理由 |
|--------|------|------|
| PostgreSQL 15 | 主数据库 | 功能强大，支持JSONB，事务处理完善 |
| Redis 7 | 缓存层 | 高性能，支持多种数据结构 |
| Elasticsearch 8 | 全文检索 | 强大的搜索和分析能力 |
| MinIO | 对象存储 | 兼容S3协议，存储试卷文件 |

### 1.2 架构设计

```
┌─────────────────────────────────────────────────────────┐
│                   应用层 (Application)                    │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│                   数据访问层 (Data Access)                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   SQLAlchemy │  │    Redis     │  │ Elasticsearch│  │
│  │    ORM       │  │    Client    │  │    Client    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│                   数据存储层 (Storage)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  PostgreSQL  │  │    Redis     │  │  MinIO/      │  │
│  │  (主数据库)   │  │  (缓存)      │  │  S3 (文件)   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## 二、核心表结构

### 2.1 用户相关表

#### 2.1.1 用户表 (users)

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    avatar_url VARCHAR(500),
    role VARCHAR(20) DEFAULT 'student' CHECK (role IN ('student', 'teacher', 'admin')),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'banned')),
    settings JSONB DEFAULT '{}',
    last_login_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_status ON users(status);

-- 触发器自动更新updated_at
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();
```

#### 2.1.2 用户设置表 (user_settings)

```sql
CREATE TABLE user_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    key VARCHAR(100) NOT NULL,
    value JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(user_id, key)
);

CREATE INDEX idx_user_settings_user ON user_settings(user_id);
```

### 2.2 试卷相关表

#### 2.2.1 试卷表 (papers)

```sql
CREATE TABLE papers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    subject VARCHAR(100) NOT NULL,
    course VARCHAR(100) NOT NULL,
    chapter VARCHAR(200),
    difficulty DECIMAL(2,1) DEFAULT 3.0 CHECK (difficulty BETWEEN 1 AND 5),
    exam_date DATE,
    total_pages INTEGER DEFAULT 0,
    question_count INTEGER DEFAULT 0,
    file_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(20) NOT NULL,
    file_size BIGINT DEFAULT 0,
    file_hash VARCHAR(64),
    analysis_status VARCHAR(20) DEFAULT 'pending' 
        CHECK (analysis_status IN ('pending', 'processing', 'completed', 'failed')),
    analysis_result JSONB,
    layout_signature VARCHAR(64),
    is_duplicate BOOLEAN DEFAULT FALSE,
    duplicate_of UUID,
    tags TEXT[],
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_papers_user ON papers(user_id);
CREATE INDEX idx_papers_subject_course ON papers(subject, course);
CREATE INDEX idx_papers_chapter ON papers(chapter);
CREATE INDEX idx_papers_difficulty ON papers(difficulty);
CREATE INDEX idx_papers_exam_date ON papers(exam_date);
CREATE INDEX idx_papers_analysis_status ON papers(analysis_status);
CREATE INDEX idx_papers_file_hash ON papers(file_hash);
CREATE INDEX idx_papers_created_at ON papers(created_at DESC);

-- 部分索引：只索引活跃的试卷
CREATE INDEX idx_papers_active ON papers(user_id, subject, course)
    WHERE analysis_status = 'completed';
```

#### 2.2.2 试卷分析结果表 (paper_analysis)

```sql
CREATE TABLE paper_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    paper_id UUID REFERENCES papers(id) ON DELETE CASCADE,
    question_count INTEGER NOT NULL,
    question_types JSONB NOT NULL,
    difficulty_distribution JSONB NOT NULL,
    knowledge_points JSONB NOT NULL,
    topic_coverage JSONB,
    quality_score DECIMAL(3,2),
    processing_time_ms INTEGER,
    model_version VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_paper_analysis_paper ON paper_analysis(paper_id);
```

### 2.3 题目相关表

#### 2.3.1 题目表 (questions)

```sql
CREATE TABLE questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    paper_id UUID REFERENCES papers(id) ON DELETE SET NULL,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    content TEXT NOT NULL,
    question_type VARCHAR(50) NOT NULL 
        CHECK (question_type IN ('choice', 'fill', 'judge', 'essay', 'calculation', 'matching')),
    difficulty VARCHAR(20) DEFAULT 'medium' 
        CHECK (difficulty IN ('easy', 'medium', 'hard')),
    score DECIMAL(5,2) DEFAULT 2.00,
    options JSONB,
    answer TEXT NOT NULL,
    explanation TEXT,
    analysis TEXT,
    page_number INTEGER,
    line_number INTEGER,
    source_type VARCHAR(20) DEFAULT 'uploaded' 
        CHECK (source_type IN ('uploaded', 'ai_generated', 'manual')),
    ai_generated BOOLEAN DEFAULT FALSE,
    generation_params JSONB,
    usage_count INTEGER DEFAULT 0,
    correct_rate DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_questions_paper ON questions(paper_id);
CREATE INDEX idx_questions_user ON questions(user_id);
CREATE INDEX idx_questions_type ON questions(question_type);
CREATE INDEX idx_questions_difficulty ON questions(difficulty);
CREATE INDEX idx_questions_source ON questions(source_type);
CREATE INDEX idx_questions_created_at ON questions(created_at DESC);

-- GIN索引用于全文搜索
CREATE INDEX idx_questions_content_gin 
    ON questions USING GIN(to_tsvector('chinese', content));
```

#### 2.3.2 题目-知识点关联表 (question_knowledge)

```sql
CREATE TABLE question_knowledge (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question_id UUID REFERENCES questions(id) ON DELETE CASCADE,
    knowledge_point_id UUID REFERENCES knowledge_points(id) ON DELETE CASCADE,
    relevance_score DECIMAL(3,2) DEFAULT 1.00,
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(question_id, knowledge_point_id)
);

CREATE INDEX idx_question_knowledge_question ON question_knowledge(question_id);
CREATE INDEX idx_question_knowledge_knowledge ON question_knowledge(knowledge_point_id);
```

### 2.4 知识点相关表

#### 2.4.1 知识点表 (knowledge_points)

```sql
CREATE TABLE knowledge_points (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    name VARCHAR(255) NOT NULL,
    subject VARCHAR(100) NOT NULL,
    course VARCHAR(100) NOT NULL,
    chapter VARCHAR(200),
    importance VARCHAR(20) DEFAULT 'normal' 
        CHECK (importance IN ('core', 'important', 'normal')),
    parent_id UUID REFERENCES knowledge_points(id) ON DELETE SET NULL,
    description TEXT,
    example TEXT,
    solution TEXT,
    cross_domain JSONB DEFAULT '[]',
    related_points UUID[] DEFAULT '{}',
    example_count INTEGER DEFAULT 0,
    question_count INTEGER DEFAULT 0,
    mastery_rate DECIMAL(5,2),
    study_time_minutes INTEGER DEFAULT 0,
    tags TEXT[],
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_knowledge_subject_course ON knowledge_points(subject, course);
CREATE INDEX idx_knowledge_chapter ON knowledge_points(chapter);
CREATE INDEX idx_knowledge_importance ON knowledge_points(importance);
CREATE INDEX idx_knowledge_parent ON knowledge_points(parent_id);
CREATE INDEX idx_knowledge_user ON knowledge_points(user_id);

-- GIN索引用于名称搜索
CREATE INDEX idx_knowledge_name_gin 
    ON knowledge_points USING GIN(to_tsvector('chinese', name));

-- 全文检索索引
CREATE INDEX idx_knowledge_description_gin 
    ON knowledge_points USING GIN(to_tsvector('chinese', description));
```

#### 2.4.2 知识点关系表 (knowledge_relations)

```sql
CREATE TABLE knowledge_relations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_kp_id UUID REFERENCES knowledge_points(id) ON DELETE CASCADE,
    target_kp_id UUID REFERENCES knowledge_points(id) ON DELETE CASCADE,
    relation_type VARCHAR(50) NOT NULL 
        CHECK (relation_type IN ('prerequisite', 'related', 'similar', 'extends', 'contrast')),
    strength DECIMAL(3,2) DEFAULT 0.80,
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(source_kp_id, target_kp_id, relation_type)
);

CREATE INDEX idx_knowledge_relations_source ON knowledge_relations(source_kp_id);
CREATE INDEX idx_knowledge_relations_target ON knowledge_relations(target_kp_id);
CREATE INDEX idx_knowledge_relations_type ON knowledge_relations(relation_type);
```

### 2.5 文档导出相关表

#### 2.5.1 导出任务表 (export_tasks)

```sql
CREATE TABLE export_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    template VARCHAR(50) DEFAULT 'academic',
    export_format VARCHAR(20) NOT NULL 
        CHECK (export_format IN ('markdown', 'word', 'pdf', 'html')),
    settings JSONB NOT NULL,
    content JSONB,
    file_path VARCHAR(500),
    file_size BIGINT,
    status VARCHAR(20) DEFAULT 'pending'
        CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    error_message TEXT,
    download_count INTEGER DEFAULT 0,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

CREATE INDEX idx_export_tasks_user ON export_tasks(user_id);
CREATE INDEX idx_export_tasks_status ON export_tasks(status);
CREATE INDEX idx_export_tasks_created_at ON export_tasks(created_at DESC);
CREATE INDEX idx_export_tasks_expires ON export_tasks(expires_at);
```

#### 2.5.2 文档模板表 (document_templates)

```sql
CREATE TABLE document_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL,
    preview_image VARCHAR(500),
    template_config JSONB NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 2.6 系统相关表

#### 2.6.1 操作日志表 (operation_logs)

```sql
CREATE TABLE operation_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id UUID,
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_operation_logs_user ON operation_logs(user_id);
CREATE INDEX idx_operation_logs_action ON operation_logs(action);
CREATE INDEX idx_operation_logs_resource ON operation_logs(resource_type, resource_id);
CREATE INDEX idx_operation_logs_created_at ON operation_logs(created_at DESC);

-- 分区表按月
CREATE TABLE operation_logs_partitioned (
    LIKE operation_logs INCLUDING ALL
) PARTITION BY RANGE (created_at);

CREATE TABLE operation_logs_2024_01 PARTITION OF operation_logs_partitioned
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
CREATE TABLE operation_logs_2024_02 PARTITION OF operation_logs_partitioned
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
```

## 三、索引策略

### 3.1 复合索引

```sql
-- 试卷查询常用组合
CREATE INDEX idx_papers_user_subject_course ON papers(user_id, subject, course);
CREATE INDEX idx_papers_analysis_status_created ON papers(analysis_status, created_at DESC);

-- 题目查询常用组合
CREATE INDEX idx_questions_type_difficulty ON questions(question_type, difficulty);
CREATE INDEX idx_questions_paper_created ON questions(paper_id, created_at DESC);

-- 知识点查询常用组合
CREATE INDEX idx_knowledge_subject_course_chapter ON knowledge_points(subject, course, chapter);
CREATE INDEX idx_knowledge_importance_created ON knowledge_points(importance, created_at DESC);
```

### 3.2 部分索引

```sql
-- 只索引已完成的分析结果
CREATE INDEX idx_papers_completed ON papers(user_id, subject)
    WHERE analysis_status = 'completed';

-- 只索引AI生成的题目
CREATE INDEX idx_questions_ai_generated ON questions(paper_id)
    WHERE ai_generated = true;

-- 只索引活跃的知识点
CREATE INDEX idx_knowledge_active ON knowledge_points(subject, course)
    WHERE question_count > 0;
```

### 3.3 索引维护

```sql
-- 定期重建索引
REINDEX INDEX CONCURRENTLY idx_papers_user_subject_course;

-- 分析表以优化查询计划
ANALYZE papers;
ANALYZE questions;
ANALYZE knowledge_points;
```

## 四、分区策略

### 4.1 试卷分区（按年份）

```sql
CREATE TABLE papers_partitioned (
    LIKE papers INCLUDING ALL
) PARTITION BY RANGE (created_at);

CREATE TABLE papers_2024 PARTITION OF papers_partitioned
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
CREATE TABLE papers_2025 PARTITION OF papers_partitioned
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
```

### 4.2 日志分区（按月）

```sql
CREATE TABLE logs_partitioned (
    LIKE operation_logs INCLUDING ALL
) PARTITION BY RANGE (created_at);

-- 自动创建月度分区
CREATE OR REPLACE FUNCTION create_log_partition()
RETURNS void AS $$
DECLARE
    partition_date DATE;
BEGIN
    FOR i IN 0..11 LOOP
        partition_date := DATE_TRUNC('month', CURRENT_DATE + (i || ' months')::INTERVAL);
        EXECUTE format(
            'CREATE TABLE IF NOT EXISTS logs_%I PARTITION OF logs_partitioned
             FOR VALUES FROM (%L) TO (%L)',
            to_char(partition_date, 'YYYY_MM'),
            partition_date,
            partition_date + INTERVAL '1 month'
        );
    END LOOP;
END;
$$ LANGUAGE plpgsql;
```

## 五、数据归档策略

### 5.1 归档策略

```sql
-- 创建归档表
CREATE TABLE papers_archive (
    LIKE papers INCLUDING ALL
);

-- 归档超过2年的试卷
INSERT INTO papers_archive
SELECT * FROM papers 
WHERE created_at < NOW() - INTERVAL '2 years'
  AND analysis_status = 'completed';

DELETE FROM papers 
WHERE created_at < NOW() - INTERVAL '2 years'
  AND analysis_status = 'completed';

-- 创建归档索引
CREATE INDEX idx_papers_archive_user ON papers_archive(user_id, subject);
CREATE INDEX idx_papers_archive_created ON papers_archive(created_at DESC);
```

### 5.2 自动归档脚本

```bash
#!/bin/bash
# archive_data.sh

DAYS=730
BACKUP_DIR="/backup/postgresql"
DATE=$(date +%Y%m%d)

# 导出归档数据
pg_dump -U postgres -d exam_platform \
    -t papers_archive \
    -c | gzip > $BACKUP_DIR/papers_archive_$DATE.sql.gz

# 清理旧备份
find $BACKUP_DIR -name "papers_archive_*.sql.gz" -mtime +30 -delete

# 执行归档
psql -U postgres -d exam_platform -c "
    INSERT INTO papers_archive
    SELECT * FROM papers 
    WHERE created_at < NOW() - INTERVAL '$DAYS days'
      AND analysis_status = 'completed';
    
    DELETE FROM papers 
    WHERE created_at < NOW() - INTERVAL '$DAYS days'
      AND analysis_status = 'completed';
"
```

## 六、备份与恢复

### 6.1 备份策略

| 备份类型 | 频率 | 保留时间 | 存储位置 |
|---------|------|---------|---------|
| 全量备份 | 每天 02:00 | 30天 | 本地 + S3 |
| 增量备份 | 每小时 | 7天 | 本地 |
| WAL归档 | 实时 | 14天 | S3 |

### 6.2 备份脚本

```bash
#!/bin/bash
# backup.sh

set -e

BACKUP_DIR="/var/backups/postgresql"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# 创建备份目录
mkdir -p $BACKUP_DIR

# 全量备份
echo "Starting full backup at $(date)"
pg_basebackup -D $BACKUP_DIR/base -Ft -z -P -U replication

# 压缩备份
tar -czf $BACKUP_DIR/full_backup_$DATE.tar.gz -C $BACKUP_DIR base

# 清理旧备份
find $BACKUP_DIR -name "full_backup_*.tar.gz" -mtime +$RETENTION_DAYS -delete

# 上传到S3
aws s3 cp $BACKUP_DIR/full_backup_$DATE.tar.gz s3://exam-platform-backups/

echo "Backup completed at $(date)"
```

### 6.3 恢复脚本

```bash
#!/bin/bash
# restore.sh

BACKUP_FILE=$1
TARGET_DIR=/var/lib/postgresql/15/main

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: restore.sh <backup_file>"
    exit 1
fi

echo "Stopping PostgreSQL..."
systemctl stop postgresql

echo "Removing old data..."
rm -rf $TARGET_DIR/*

echo "Extracting backup..."
tar -xzf $BACKUP_FILE -C $TARGET_DIR

echo "Setting permissions..."
chown -R postgres:postgres $TARGET_DIR

echo "Starting PostgreSQL..."
systemctl start postgresql

echo "Recovery completed!"
```

## 七、性能优化

### 7.1 PostgreSQL配置优化

```sql
-- postgresql.conf 关键配置

-- 内存设置
shared_buffers = 8GB                    -- 总内存的25%
effective_cache_size = 24GB             -- 总内存的75%
work_mem = 256MB                        -- 复杂查询工作内存
maintenance_work_mem = 2GB              -- 维护操作内存
wal_buffers = 64MB                      -- WAL缓冲区

-- 并发设置
max_connections = 200
max_worker_processes = 16
max_parallel_workers_per_gather = 4
max_parallel_workers = 16

-- WAL和检查点
wal_level = replica
checkpoint_completion_target = 0.9
checkpoint_timeout = 15min
max_wal_size = 4GB
min_wal_size = 1GB

-- 查询优化器
random_page_cost = 1.1                  -- SSD优化
effective_io_concurrency = 200          -- SSD优化
default_statistics_target = 500

-- 自动清理
autovacuum = on
autovacuum_max_workers = 4
autovacuum_naptime = 30s
```

### 7.2 慢查询分析

```sql
-- 启用慢查询日志
ALTER SYSTEM SET log_min_duration_statement = 1000;
ALTER SYSTEM SET log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d ';

-- 查询最慢的TOP 20语句
SELECT 
    substring(query, 1, 100) AS query,
    calls,
    round(total_exec_time::numeric, 2) AS total_time,
    round(mean_exec_time::numeric, 2) AS mean_time,
    rows
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 20;
```

### 7.3 缓存策略

```python
# Redis缓存配置

CACHE_CONFIG = {
    # 用户会话缓存 (24小时)
    "user_session": {
        "ttl": 86400,
        "max_size": 10000
    },
    # 试卷分析结果 (1周)
    "paper_analysis": {
        "ttl": 604800,
        "max_size": 5000
    },
    # 知识点列表 (1小时)
    "knowledge_list": {
        "ttl": 3600,
        "max_size": 10000
    },
    # 用户设置 (1天)
    "user_settings": {
        "ttl": 86400,
        "max_size": 100000
    }
}

# 热点数据预加载
PRELOAD_KEYS = [
    "user:*:profile",
    "paper:*:analysis",
    "knowledge:graph:*"
]
```
