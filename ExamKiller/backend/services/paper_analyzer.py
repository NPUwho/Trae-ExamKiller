from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from enum import Enum
import hashlib
import re

class QuestionType(Enum):
    CHOICE = "choice"
    FILL = "fill"
    JUDGE = "judge"
    ESSAY = "essay"
    CALCULATION = "calculation"

class Difficulty(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3

@dataclass
class OCRResult:
    text: str
    confidence: float
    bounding_box: Tuple[float, float, float, float]
    block_type: str

@dataclass
class PaperStructure:
    pages: List['Page']
    metadata: 'PaperMetadata'

@dataclass
class Page:
    page_number: int
    width: float
    height: float
    header: Optional[str]
    footer: Optional[str]
    columns: int
    blocks: List['ContentBlock']

@dataclass
class ContentBlock:
    block_type: str
    content: str
    position: Tuple[float, float]
    size: Tuple[float, float]
    confidence: float

@dataclass
class PaperMetadata:
    title: str
    subject: str
    course: str
    chapter: Optional[str]
    exam_date: Optional[str]
    difficulty: float
    total_pages: int
    question_count: int

@dataclass
class Question:
    id: str
    content: str
    question_type: QuestionType
    difficulty: Difficulty
    score: float
    options: List[str]
    answer: str
    explanation: Optional[str]
    knowledge_points: List[str]
    page_number: int
    line_number: int

@dataclass
class KnowledgePoint:
    id: str
    name: str
    subject: str
    course: str
    chapter: Optional[str]
    importance: str
    parent_id: Optional[str]
    description: str
    cross_domain: List[str]

class PaperParser:
    def __init__(self):
        self.supported_formats = ['pdf', 'docx', 'jpg', 'jpeg', 'png']
    
    def parse(self, file_path: str) -> PaperStructure:
        ext = file_path.split('.')[-1].lower()
        if ext not in self.supported_formats:
            raise ValueError(f"不支持的文件格式: {ext}")
        
        if ext == 'pdf':
            return self._parse_pdf(file_path)
        elif ext == 'docx':
            return self._parse_docx(file_path)
        else:
            return self._parse_image(file_path)
    
    def _parse_pdf(self, file_path: str) -> PaperStructure:
        pages = []
        metadata = PaperMetadata(
            title="解析的试卷",
            subject="",
            course="",
            chapter=None,
            exam_date=None,
            difficulty=3.0,
            total_pages=1,
            question_count=0
        )
        return PaperStructure(pages=pages, metadata=metadata)
    
    def _parse_docx(self, file_path: str) -> PaperStructure:
        pages = []
        metadata = PaperMetadata(
            title="解析的试卷",
            subject="",
            course="",
            chapter=None,
            exam_date=None,
            difficulty=3.0,
            total_pages=1,
            question_count=0
        )
        return PaperStructure(pages=pages, metadata=metadata)
    
    def _parse_image(self, file_path: str) -> PaperStructure:
        pages = []
        metadata = PaperMetadata(
            title="解析的试卷",
            subject="",
            course="",
            chapter=None,
            exam_date=None,
            difficulty=3.0,
            total_pages=1,
            question_count=0
        )
        return PaperStructure(pages=pages, metadata=metadata)

class OCREngine:
    def __init__(self):
        self.engines = {}
    
    def recognize(self, image_path: str) -> List[OCRResult]:
        results = []
        return results
    
    def detect_tables(self, image_path: str) -> List[Dict]:
        tables = []
        return tables

class LayoutAnalyzer:
    def __init__(self):
        self.header_patterns = []
        self.footer_patterns = []
        self.page_number_patterns = []
    
    def analyze(self, page_image) -> Dict:
        header = self._detect_header(page_image)
        footer = self._detect_footer(page_image)
        columns = self._detect_columns(page_image)
        page_number = self._detect_page_number(page_image)
        
        return {
            "header": header,
            "footer": footer,
            "columns": columns,
            "page_number": page_number,
            "margin_top": 72.0,
            "margin_bottom": 72.0,
            "margin_left": 72.0,
            "margin_right": 72.0,
            "line_spacing": 12.0,
            "font_size": 12.0
        }
    
    def _detect_header(self, page_image) -> Optional[str]:
        return None
    
    def _detect_footer(self, page_image) -> Optional[str]:
        return None
    
    def _detect_columns(self, page_image) -> int:
        return 1
    
    def _detect_page_number(self, page_image) -> Optional[str]:
        return None
    
    def generate_layout_signature(self, layout_info: Dict) -> str:
        signature_str = f"{layout_info.get('columns', 1)}_{layout_info.get('font_size', 12)}"
        return hashlib.md5(signature_str.encode()).hexdigest()[:16]

class QuestionExtractor:
    def __init__(self):
        self.question_patterns = {
            QuestionType.CHOICE: [
                r'^\d+[.、)]\s*.+\?\s*$',
                r'^第\s*\d+\s*题[.、)]\s*.+\?\s*$'
            ],
            QuestionType.FILL: [
                r'^\d+[.、)]\s*.+\____.*$',
                r'^第\s*\d+\s*题[.、)]\s*.+\____.*$'
            ],
            QuestionType.JUDGE: [
                r'^\d+[.、)]\s*.+[是否对错].*\?$',
                r'^判断.*：.+$'
            ],
            QuestionType.ESSAY: [
                r'^\d+[.、)]\s*.+简述.+\?$',
                r'^第\s*\d+\s*题[.、)]\s*.+论述.+\?$'
            ]
        }
    
    def extract(self, text: str, layout_info: Dict) -> List[Question]:
        questions = []
        lines = text.split('\n')
        
        current_question = None
        question_buffer = []
        
        for line_num, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            question_type = self._detect_question_type(line)
            
            if question_type or self._is_new_question(line, lines, line_num):
                if current_question and question_buffer:
                    content = '\n'.join(question_buffer)
                    question = self._create_question(content, current_question, line_num)
                    questions.append(question)
                
                current_question = question_type if question_type else QuestionType.ESSAY
                question_buffer = [line]
            else:
                if current_question:
                    question_buffer.append(line)
        
        if current_question and question_buffer:
            content = '\n'.join(question_buffer)
            question = self._create_question(content, current_question, len(lines))
            questions.append(question)
        
        return questions
    
    def _detect_question_type(self, line: str) -> Optional[QuestionType]:
        for qtype, patterns in self.question_patterns.items():
            for pattern in patterns:
                if re.match(pattern, line):
                    return qtype
        return None
    
    def _is_new_question(self, line: str, lines: List[str], current_idx: int) -> bool:
        if current_idx == 0:
            return bool(re.match(r'^\d+[.、)]', line))
        
        prev_line = lines[current_idx - 1].strip()
        has_question_number = bool(re.match(r'^\d+[.、)]', line))
        prev_is_blank = not prev_line or prev_line.endswith('。')
        
        return has_question_number and prev_is_blank
    
    def _create_question(self, content: str, qtype: QuestionType, line_num: int) -> Question:
        question_id = hashlib.md5(content.encode()).hexdigest()[:16]
        
        options = self._extract_options(content) if qtype == QuestionType.CHOICE else []
        answer = self._extract_answer(content, qtype)
        score = self._estimate_score(content, qtype)
        
        return Question(
            id=question_id,
            content=content,
            question_type=qtype,
            difficulty=self._estimate_difficulty(content),
            score=score,
            options=options,
            answer=answer,
            explanation=None,
            knowledge_points=[],
            page_number=line_num // 50 + 1,
            line_number=line_num % 50
        )
    
    def _extract_options(self, content: str) -> List[str]:
        options = []
        option_pattern = r'^([A-D])[.、）]\s*(.+)$'
        for line in content.split('\n'):
            match = re.match(option_pattern, line.strip())
            if match:
                options.append(f"{match.group(1)}. {match.group(2)}")
        return options
    
    def _extract_answer(self, content: str, qtype: QuestionType) -> str:
        if qtype == QuestionType.CHOICE:
            for line in content.split('\n'):
                if line.strip().startswith('答案：'):
                    return line.split('：')[-1].strip()
            return ""
        return ""
    
    def _estimate_score(self, content: str, qtype: QuestionType) -> float:
        base_scores = {
            QuestionType.CHOICE: 2.0,
            QuestionType.FILL: 3.0,
            QuestionType.JUDGE: 2.0,
            QuestionType.ESSAY: 8.0,
            QuestionType.CALCULATION: 10.0
        }
        return base_scores.get(qtype, 2.0)
    
    def _estimate_difficulty(self, content: str) -> Difficulty:
        complex_indicators = ['证明', '计算', '综合', '应用']
        easy_indicators = ['定义', '概念', '基本', '简单']
        
        content_lower = content.lower()
        complex_count = sum(1 for ind in complex_indicators if ind in content_lower)
        easy_count = sum(1 for ind in easy_indicators if ind in content_lower)
        
        if complex_count > easy_count:
            return Difficulty.HARD
        elif easy_count > complex_count:
            return Difficulty.EASY
        return Difficulty.MEDIUM

class PaperSimilarity:
    def __init__(self):
        self.threshold = 0.85
    
    def calculate_similarity(self, paper1: PaperStructure, paper2: PaperStructure) -> float:
        text1 = self._extract_text(paper1)
        text2 = self._extract_text(paper2)
        
        jaccard_sim = self._jaccard_similarity(text1, text2)
        layout_sim = self._layout_similarity(paper1, paper2)
        knowledge_sim = self._knowledge_similarity(paper1, paper2)
        
        total_similarity = (
            0.4 * jaccard_sim +
            0.3 * layout_sim +
            0.3 * knowledge_sim
        )
        
        return total_similarity
    
    def _extract_text(self, paper: PaperStructure) -> set:
        words = set()
        for page in paper.pages:
            for block in page.blocks:
                for char in block.content:
                    words.add(char)
        return words
    
    def _jaccard_similarity(self, set1: set, set2: set) -> float:
        if not set1 or not set2:
            return 0.0
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union > 0 else 0.0
    
    def _layout_similarity(self, paper1: PaperStructure, paper2: PaperStructure) -> float:
        layout1 = paper1.metadata
        layout2 = paper2.metadata
        
        if layout1.difficulty != layout2.difficulty:
            return 0.7
        
        return 0.9
    
    def _knowledge_similarity(self, paper1: PaperStructure, paper2: PaperStructure) -> float:
        return 0.8
    
    def is_duplicate(self, paper1: PaperStructure, paper2: PaperStructure) -> bool:
        return self.calculate_similarity(paper1, paper2) >= self.threshold
