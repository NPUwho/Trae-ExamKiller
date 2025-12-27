from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import hashlib
import re
import requests
import json

class Difficulty(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class Importance(Enum):
    CORE = "core"
    IMPORTANT = "important"
    NORMAL = "normal"

class QwenAPIClient:
    def __init__(self, base_url: str, api_key: str, model_name: str):
        self.base_url = base_url
        self.api_key = api_key
        self.model_name = model_name
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    
    def call_api(self, messages: List[Dict]) -> str:
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2048
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Qwen API Error: {e}")
            return f"API调用失败: {str(e)}"

@dataclass
class ExtractedKnowledge:
    name: str
    importance: Importance
    description: str
    cross_domain: List[str]
    related_points: List[str]

class KnowledgeExtractor:
    def __init__(self, model_path: str = None, qwen_client: QwenAPIClient = None):
        self.important_patterns = {
            Importance.CORE: [
                r'定义|概念|原理|定理|公式|重要|核心|关键',
                r'必须掌握|重点|主要|基本'
            ],
            Importance.IMPORTANT: [
                r'性质|应用|方法|技巧|常见',
                r'需要注意|容易出错|经常考'
            ],
            Importance.NORMAL: [
                r'了解|知道|熟悉|参考'
            ]
        }
        
        self.domain_keywords = {
            'math': ['极限', '导数', '积分', '函数', '数列', '级数', '矩阵'],
            'physics': ['力', '能', '热', '光', '电磁', '量子'],
            'chemistry': ['元素', '反应', '化学键', '溶液', '有机'],
            'computer': ['算法', '数据结构', '网络', '数据库', '编程']
        }
        
        self.qwen_client = qwen_client
    
    def extract(self, text: str) -> List[ExtractedKnowledge]:
        if self.qwen_client:
            return self._extract_with_ai(text)
        else:
            return self._extract_with_rules(text)
    
    def _extract_with_rules(self, text: str) -> List[ExtractedKnowledge]:
        sentences = self._split_sentences(text)
        knowledge_points = []
        
        for sentence in sentences:
            importance = self._classify_importance(sentence)
            if importance:
                name = self._extract_name(sentence)
                if name and len(name) >= 2:
                    cross_domain = self._find_cross_domain(name)
                    related = self._find_related(name, sentences)
                    
                    knowledge_points.append(ExtractedKnowledge(
                        name=name,
                        importance=importance,
                        description=sentence[:100],
                        cross_domain=cross_domain,
                        related_points=related
                    ))
        
        return knowledge_points
    
    def _extract_with_ai(self, text: str) -> List[ExtractedKnowledge]:
        messages = [
            {
                "role": "system",
                "content": "你是一个专业的知识点提取助手。请从用户提供的文本中提取出核心知识点，并按照重要程度分类。每个知识点应包含名称、重要程度（core、important、normal）、简短描述以及相关知识点。请以JSON格式输出，包含一个knowledge_points数组，每个元素包含name、importance、description和related_points字段。"
            },
            {
                "role": "user",
                "content": text
            }
        ]
        
        response = self.qwen_client.call_api(messages)
        
        try:
            result = json.loads(response)
            extracted_points = []
            
            for point in result.get('knowledge_points', []):
                importance = Importance(point['importance'])
                cross_domain = self._find_cross_domain(point['name'])
                
                extracted_points.append(ExtractedKnowledge(
                    name=point['name'],
                    importance=importance,
                    description=point['description'],
                    cross_domain=cross_domain,
                    related_points=point.get('related_points', [])
                ))
            
            return extracted_points
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"AI提取结果解析失败: {e}")
            return self._extract_with_rules(text)
    
    def _split_sentences(self, text: str) -> List[str]:
        sentences = re.split(r'[。！？；\n]', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _classify_importance(self, text: str) -> Optional[Importance]:
        text_lower = text.lower()
        
        for importance, patterns in self.important_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    return importance
        
        if '如果' in text or '当' in text:
            return Importance.IMPORTANT
        
        return Importance.NORMAL
    
    def _extract_name(self, text: str) -> Optional[str]:
        patterns = [
            r'([^\s\d，。！？；:：]+(?:定义|概念|定理|法则|原理|性质))',
            r'([^\s\d，。！？；:：]{2,10})(?:是指|是|指|称为)',
            r'((?:第|一|二|三|四|五|六|七|八|九|十)+(?:章|节|部分|点|条|款))'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        words = text.split()
        if words:
            return words[0][:10]
        
        return None
    
    def _find_cross_domain(self, name: str) -> List[str]:
        cross_domains = []
        
        for domain, keywords in self.domain_keywords.items():
            if any(kw in name for kw in keywords):
                cross_domains.append(domain)
        
        return cross_domains
    
    def _find_related(self, name: str, sentences: List[str]) -> List[str]:
        related = []
        name_chars = set(name)
        
        for sentence in sentences:
            if sentence == name:
                continue
            
            overlap = len(set(sentence) & name_chars)
            if overlap >= 3:
                related_point = self._extract_name(sentence)
                if related_point and related_point != name:
                    related.append(related_point)
        
        return related[:5]

class KnowledgeGraph:
    def __init__(self):
        self.nodes = {}
        self.edges = {}
    
    def add_knowledge_point(self, point: ExtractedKnowledge):
        if point.name not in self.nodes:
            self.nodes[point.name] = {
                'importance': point.importance.value,
                'description': point.description,
                'domains': point.cross_domain,
                'examples': 0,
                'children': []
            }
        
        for related in point.related_points:
            self.add_edge(point.name, related)
    
    def add_edge(self, source: str, target: str):
        if source not in self.edges:
            self.edges[source] = []
        
        if target not in self.edges[source]:
            self.edges[source].append(target)
    
    def get_related(self, name: str, depth: int = 2) -> List[str]:
        related = set()
        current_level = {name}
        
        for _ in range(depth):
            next_level = set()
            for node in current_level:
                if node in self.edges:
                    next_level.update(self.edges[node])
            
            related.update(next_level)
            current_level = next_level
        
        return list(related)
    
    def get_subtree(self, root: str) -> Dict:
        if root not in self.nodes:
            return {}
        
        subtree = {
            'name': root,
            'importance': self.nodes[root]['importance'],
            'children': []
        }
        
        if root in self.edges:
            for child in self.edges[root]:
                child_subtree = self.get_subtree(child)
                if child_subtree:
                    subtree['children'].append(child_subtree)
        
        return subtree

class QuestionGenerator:
    def __init__(self, model_path: str = None, qwen_client: QwenAPIClient = None):
        self.question_templates = {
            Difficulty.EASY: [
                "请简述{knowledge}的定义。",
                "{knowledge}的基本性质是什么？",
                "下列关于{knowledge}的说法正确的是？"
            ],
            Difficulty.MEDIUM: [
                "请证明{knowledge}的相关性质。",
                "应用{knowledge}解决以下问题。",
                "比较{knowledge}与相关概念的异同。"
            ],
            Difficulty.HARD: [
                "综合运用{knowledge}解决复杂问题。",
                "分析{knowledge}在实际应用中的难点。",
                "设计一个涉及{knowledge}的综合题目。"
            ]
        }
        
        self.knowledge_graph = KnowledgeGraph()
        self.qwen_client = qwen_client
    
    def set_knowledge_graph(self, graph: KnowledgeGraph):
        self.knowledge_graph = graph
    
    def generate(
        self,
        knowledge_points: List[ExtractedKnowledge],
        settings: Dict
    ) -> List[Dict]:
        if self.qwen_client:
            return self._generate_with_ai(knowledge_points, settings)
        else:
            return self._generate_with_rules(knowledge_points, settings)
    
    def _generate_with_rules(self, knowledge_points: List[ExtractedKnowledge], settings: Dict) -> List[Dict]:
        questions = []
        question_count = settings.get('question_count', 20)
        difficulty_ratio = settings.get('difficulty_ratio', {
            'easy': 0.3,
            'medium': 0.5,
            'hard': 0.2
        })
        
        difficulty_map = []
        difficulty_map.extend([Difficulty.EASY] * int(question_count * difficulty_ratio['easy']))
        difficulty_map.extend([Difficulty.MEDIUM] * int(question_count * difficulty_ratio['medium']))
        difficulty_map.extend([Difficulty.HARD] * int(question_count * difficulty_ratio['hard']))
        
        while len(difficulty_map) < question_count:
            difficulty_map.append(Difficulty.MEDIUM)
        
        for i in range(question_count):
            knowledge = knowledge_points[i % len(knowledge_points)]
            difficulty = difficulty_map[i]
            
            template = self._select_template(knowledge, difficulty)
            question_text = template.format(knowledge=knowledge.name)
            
            question = {
                'id': hashlib.md5(question_text.encode()).hexdigest()[:16],
                'content': question_text,
                'type': self._infer_type(knowledge, difficulty),
                'difficulty': difficulty.value,
                'score': self._calculate_score(difficulty),
                'answer': self._generate_answer(knowledge, difficulty),
                'explanation': self._generate_explanation(knowledge, difficulty),
                'knowledge_point': knowledge.name,
                'importance': knowledge.importance.value
            }
            
            questions.append(question)
        
        return questions
    
    def _generate_with_ai(self, knowledge_points: List[ExtractedKnowledge], settings: Dict) -> List[Dict]:
        questions = []
        question_count = settings.get('question_count', 20)
        
        # 准备AI生成的提示
        knowledge_text = "\n".join([
            f"- {kp.name}（{kp.importance.value}）：{kp.description}"
            for kp in knowledge_points
        ])
        
        difficulty_ratio = settings.get('difficulty_ratio', {
            'easy': 0.3,
            'medium': 0.5,
            'hard': 0.2
        })
        
        messages = [
            {
                "role": "system",
                "content": "你是一个专业的题目生成助手，请根据提供的知识点生成高质量的题目。每个题目应包含内容、题型（选择题、填空题、判断题、简答题、计算题）、难度（easy、medium、hard）、答案和解析。请以JSON格式输出，包含一个questions数组，每个元素包含content、type、difficulty、answer、explanation字段。"
            },
            {
                "role": "user",
                "content": f"请根据以下知识点生成{question_count}道题目：\n{knowledge_text}\n\n难度分布：\n- 简单：{difficulty_ratio['easy']*100}%\n- 中等：{difficulty_ratio['medium']*100}%\n- 困难：{difficulty_ratio['hard']*100}%\n\n请生成多样化的题型，包括选择题、填空题、判断题、简答题等。"
            }
        ]
        
        response = self.qwen_client.call_api(messages)
        
        try:
            result = json.loads(response)
            ai_questions = result.get('questions', [])
            
            for i, q in enumerate(ai_questions[:question_count]):
                question = {
                    'id': hashlib.md5((q['content'] + str(i)).encode()).hexdigest()[:16],
                    'content': q['content'],
                    'type': q['type'],
                    'difficulty': q['difficulty'],
                    'score': self._calculate_score(Difficulty(q['difficulty'])),
                    'answer': q['answer'],
                    'explanation': q['explanation'],
                    'knowledge_point': knowledge_points[i % len(knowledge_points)].name,
                    'importance': knowledge_points[i % len(knowledge_points)].importance.value
                }
                questions.append(question)
            
            return questions
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"AI生成结果解析失败: {e}")
            return self._generate_with_rules(knowledge_points, settings)
    
    def _select_template(self, knowledge: ExtractedKnowledge, difficulty: Difficulty) -> str:
        templates = self.question_templates[difficulty]
        
        if knowledge.importance == Importance.CORE:
            return templates[0] if difficulty == Difficulty.EASY else templates[1]
        
        return templates[0]
    
    def _infer_type(self, knowledge: ExtractedKnowledge, difficulty: Difficulty) -> str:
        if difficulty == Difficulty.EASY:
            return 'choice' if knowledge.importance != Importance.NORMAL else 'fill'
        elif difficulty == Difficulty.MEDIUM:
            return 'fill'
        else:
            return 'essay'
    
    def _calculate_score(self, difficulty: Difficulty) -> float:
        scores = {
            Difficulty.EASY: 2.0,
            Difficulty.MEDIUM: 4.0,
            Difficulty.HARD: 8.0
        }
        return scores[difficulty]
    
    def _generate_answer(self, knowledge: ExtractedKnowledge, difficulty: Difficulty) -> str:
        return f"答案需根据{knowledge.name}的定义和性质进行分析。"
    
    def _generate_explanation(self, knowledge: ExtractedKnowledge, difficulty: Difficulty) -> str:
        return f"本题考查{knowledge.name}的理解和应用，{knowledge.description}"

class StrategyEngine:
    def __init__(self):
        self.difficulty_weights = {
            'easy': {'choice': 0.6, 'fill': 0.3, 'essay': 0.1},
            'medium': {'choice': 0.4, 'fill': 0.4, 'essay': 0.2},
            'hard': {'choice': 0.3, 'fill': 0.4, 'essay': 0.3}
        }
    
    def calculate_strategy(
        self,
        knowledge_points: List[ExtractedKnowledge],
        historical_data: Optional[Dict] = None
    ) -> Dict:
        strategy = {}
        
        for kp in knowledge_points:
            if kp.importance == Importance.CORE:
                difficulty = 'hard'
            elif kp.importance == Importance.IMPORTANT:
                difficulty = 'medium'
            else:
                difficulty = 'easy'
            
            strategy[kp.name] = {
                'difficulty': difficulty,
                'question_count': self._calculate_count(kp.importance),
                'type_distribution': self.difficulty_weights[difficulty],
                'time_allocation': self._calculate_time(kp.importance)
            }
        
        return strategy
    
    def _calculate_count(self, importance: Importance) -> int:
        counts = {
            Importance.CORE: 5,
            Importance.IMPORTANT: 3,
            Importance.NORMAL: 1
        }
        return counts[importance]
    
    def _calculate_time(self, importance: Importance) -> int:
        times = {
            Importance.CORE: 15,
            Importance.IMPORTANT: 10,
            Importance.NORMAL: 5
        }
        return times[importance]
