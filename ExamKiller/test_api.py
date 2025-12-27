import requests
import json

print("=" * 60)
print("     ExamKiller - 完整功能测试")
print("=" * 60)

# 1. 健康检查
print("\n[1] 健康检查...")
r = requests.get('http://localhost:8001/api/health')
result = r.json()
print(f"    状态: {result['status']}")
print(f"    消息: {result['message']}")

# 2. 测试知识点提取
print("\n[2] 测试知识点提取...")
test_text = """函数极限的定义：当x→x0时，若对任意ε>0，存在δ>0，使得当0<|x-x0|<δ时，|f(x)-A|<ε，则称A为f(x)的极限。

重要极限：
1. lim(x→0) sinx/x = 1
2. lim(x→∞) (1+1/x)^x = e

极限的运算法则：
- 和差的极限等于极限的和差
- 积的极限等于极限的积
- 商的极限等于极限的商（分母不为零）"""

data = {'text': test_text}
r = requests.post('http://localhost:8001/api/knowledge/extract', json=data)
result = r.json()
print(f"    成功: {result.get('success')}")
if result.get('knowledge_points'):
    print(f"    提取到 {len(result['knowledge_points'])} 个知识点:")
    for kp in result['knowledge_points'][:5]:
        importance_cn = {'core': '核心', 'important': '重要', 'normal': '一般'}
        print(f"      - {kp['name']} ({importance_cn.get(kp['importance'], kp['importance'])})")

# 3. 测试题目生成
print("\n[3] 测试AI题目生成...")
question_data = {
    'review_input': {'text': test_text, 'source_type': 'text'},
    'settings': {
        'question_count': 5,
        'easy_ratio': 40,
        'medium_ratio': 40,
        'hard_ratio': 20,
        'question_types': ['choice', 'fill']
    }
}
r = requests.post('http://localhost:8001/api/questions/generate', json=question_data)
result = r.json()
print(f"    成功: {result.get('success')}")
print(f"    生成题目数: {result.get('total_count', 0)}")
print(f"    预计用时: {result.get('estimated_time', 0)} 分钟")
if result.get('questions'):
    print("    前3道题目:")
    for i, q in enumerate(result['questions'][:3]):
        print(f"      {i+1}. [{q['type']}] {q['content'][:50]}...")

# 4. 获取知识图谱
print("\n[4] 获取知识图谱...")
r = requests.get('http://localhost:8001/api/knowledge/graph')
result = r.json()
print(f"    节点数: {len(result.get('nodes', []))}")
print(f"    边数: {len(result.get('links', []))}")
print("    节点列表:")
for node in result.get('nodes', [])[:3]:
    print(f"      - {node['name']} ({node['importance']})")

# 5. 试卷上传测试
print("\n[5] 测试试卷上传...")
paper_data = {
    'title': '高等数学2024期末试卷A卷',
    'subject': '理学',
    'course': '高等数学',
    'chapter': '第1-8章',
    'difficulty': 3.0,
    'exam_date': '2024-12-20'
}
r = requests.post('http://localhost:8001/api/papers/upload', json=paper_data)
result = r.json()
print(f"    成功: {result.get('success')}")
print(f"    试卷ID: {result.get('paper_id', 'N/A')}")
print(f"    消息: {result.get('message', '')}")

# 6. 获取试卷列表
print("\n[6] 获取试卷列表...")
r = requests.get('http://localhost:8001/api/papers')
result = r.json()
print(f"    试卷数量: {len(result.get('papers', []))}")

# 7. 测试文档生成
print("\n[7] 测试复习文档生成...")
export_data = {
    'title': '高等数学重点知识归纳',
    'template': 'academic',
    'content': '函数极限相关知识点总结，包含极限定义、运算法则、重要极限等内容。'
}
r = requests.post('http://localhost:8001/api/exports/generate', json=export_data)
result = r.json()
print(f"    成功: {result.get('success')}")
print(f"    文档格式: {result.get('format', 'N/A')}")

print("\n" + "=" * 60)
print("     所有测试完成！")
print("=" * 60)
print("\n现在你可以打开浏览器访问:")
print("  http://localhost:8001  (如果通过后端服务访问)")
print("  或直接打开文件: ExamKiller/index.html")
print("\n确保前端JavaScript中的API地址为: http://localhost:8001/api")
