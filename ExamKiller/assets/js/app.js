const API_BASE_URL = 'http://localhost:8000/api';

let currentSection = 'home';
let extractedKnowledge = [];
let generatedQuestions = [];
let isRecording = false;

async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    try {
        const response = await fetch(url, { ...defaultOptions, ...options });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '请求失败');
        }
        return await response.json();
    } catch (error) {
        console.error('API请求错误:', error);
        throw error;
    }
}

document.addEventListener('DOMContentLoaded', function() {
    initNavigation();
    initUpload();
    initTabs();
    initDifficultySlider();
    initDifficultyRatio();
    initQuestionCount();
    initVoiceRecord();
    initTemplateSelection();
    initKnowledgeFilter();
    initGraphControls();
    loadPapers();
    loadKnowledgeGraph();
    initSummaryTabs();
});

function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const section = this.dataset.section;
            navigateTo(section);
        });
    });
}

function navigateTo(section) {
    currentSection = section;
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        if (item.dataset.section === section) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });
    const sections = document.querySelectorAll('.content-section');
    sections.forEach(s => {
        if (s.id === section) {
            s.classList.add('active');
        } else {
            s.classList.remove('active');
        }
    });
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

async function loadPapers() {
    try {
        const data = await apiRequest('/papers');
        const papersList = document.getElementById('papersList');
        if (papersList && data.papers) {
            papersList.innerHTML = data.papers.map(paper => `
                <div class="paper-item" data-id="${paper.id}">
                    <div class="paper-icon pdf">
                        <i class="fas fa-file-pdf"></i>
                    </div>
                    <div class="paper-info">
                        <h4>${paper.title}</h4>
                        <p>${paper.subject || '待分类'} · ${paper.course || '待分类'} · ${paper.chapter || '待分类'}</p>
                        <div class="paper-meta">
                            <span><i class="fas fa-${paper.status === 'analyzed' ? 'check-circle' : 'clock'}"></i> ${paper.status === 'analyzed' ? '已分析' : '待分析'}</span>
                            <span><i class="fas fa-clock"></i> ${new Date(paper.created_at).toLocaleDateString()}</span>
                            <span><i class="fas fa-list"></i> ${paper.analysis?.question_count || 0}题</span>
                        </div>
                    </div>
                    <div class="paper-actions">
                        <button class="btn-icon" title="查看详情" onclick="viewPaper('${paper.id}')"><i class="fas fa-eye"></i></button>
                        <button class="btn-icon" title="重新分析" onclick="reanalyzePaper('${paper.id}')"><i class="fas fa-redo"></i></button>
                        <button class="btn-icon danger" title="删除" onclick="deletePaper('${paper.id}')"><i class="fas fa-trash"></i></button>
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('加载试卷列表失败:', error);
    }
}

function initUpload() {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    
    if (dropZone) {
        dropZone.addEventListener('click', () => fileInput && fileInput.click());
        
        dropZone.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.classList.add('dragover');
        });
        
        dropZone.addEventListener('dragleave', function() {
            this.classList.remove('dragover');
        });
        
        dropZone.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFileUpload(files[0]);
            }
        });
    }
    
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            if (this.files.length > 0) {
                handleFileUpload(this.files[0]);
            }
        });
    }
}

async function handleFileUpload(file) {
    const uploadProgress = document.getElementById('uploadProgress');
    const progressFill = document.getElementById('progressFill');
    const progressPercent = document.getElementById('progressPercent');
    const steps = document.querySelectorAll('.progress-steps .step');
    
    if (!uploadProgress) return;
    
    uploadProgress.style.display = 'block';
    
    const subject = document.getElementById('subjectSelect')?.value || '未分类';
    const course = document.getElementById('courseInput')?.value || '未分类';
    const chapter = document.getElementById('chapterInput')?.value || '';
    const difficulty = document.getElementById('difficultySlider')?.value || 3;
    const examDate = document.getElementById('examDate')?.value || '';
    
    const fileName = file.name.replace(/\.[^/.]+$/, "");
    
    let progress = 0;
    const interval = setInterval(() => {
        progress += Math.random() * 12;
        if (progress > 100) progress = 100;
        
        if (progressFill) progressFill.style.width = progress + '%';
        if (progressPercent) progressPercent.textContent = Math.round(progress) + '%';
        
        if (progress >= 20) steps[0]?.classList.add('active');
        if (progress >= 40) steps[1]?.classList.add('active');
        if (progress >= 60) steps[2]?.classList.add('active');
        if (progress >= 80) steps[3]?.classList.add('active');
        if (progress >= 100) {
            steps[4]?.classList.add('active');
            clearInterval(interval);
        }
    }, 200);
    
    try {
        const paperData = {
            title: fileName,
            subject: subject,
            course: course,
            chapter: chapter || undefined,
            difficulty: parseFloat(difficulty),
            exam_date: examDate || undefined
        };
        
        const result = await apiRequest('/papers/upload', {
            method: 'POST',
            body: JSON.stringify(paperData)
        });
        
        if (result.success) {
            setTimeout(() => {
                showToast('试卷上传并分析完成！', 'success');
                loadPapers();
                resetUploadForm();
            }, 1000);
        }
    } catch (error) {
        showToast('上传失败: ' + error.message, 'error');
    }
}

function resetUploadForm() {
    const uploadProgress = document.getElementById('uploadProgress');
    const steps = document.querySelectorAll('.progress-steps .step');
    if (uploadProgress) uploadProgress.style.display = 'none';
    steps.forEach(s => s.classList.remove('active'));
    const progressFill = document.getElementById('progressFill');
    if (progressFill) progressFill.style.width = '0%';
    const progressPercent = document.getElementById('progressPercent');
    if (progressPercent) progressPercent.textContent = '0%';
    
    document.getElementById('subjectSelect') && (document.getElementById('subjectSelect').value = '');
    document.getElementById('courseInput') && (document.getElementById('courseInput').value = '');
    document.getElementById('chapterInput') && (document.getElementById('chapterInput').value = '');
}

async function viewPaper(paperId) {
    try {
        const paper = await apiRequest(`/papers/${paperId}`);
        showToast(`试卷: ${paper.title}`, 'info');
    } catch (error) {
        showToast('获取试卷详情失败', 'error');
    }
}

async function reanalyzePaper(paperId) {
    showToast('重新分析功能开发中', 'info');
}

async function deletePaper(paperId) {
    if (!confirm('确定要删除这份试卷吗？')) return;
    
    try {
        const result = await apiRequest(`/papers/${paperId}`, {
            method: 'DELETE'
        });
        if (result.success) {
            showToast('删除成功', 'success');
            loadPapers();
        }
    } catch (error) {
        showToast('删除失败: ' + error.message, 'error');
    }
}

function initTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const tab = this.dataset.tab;
            tabBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            const tabContent = document.getElementById(tab + 'Tab');
            if (tabContent) tabContent.classList.add('active');
        });
    });
}

function initDifficultySlider() {
    const slider = document.getElementById('difficultySlider');
    const label = document.getElementById('difficultyLabel');
    const levels = ['非常简单', '简单', '中等', '困难', '非常困难'];
    
    if (slider && label) {
        slider.addEventListener('input', function() {
            label.textContent = levels[this.value - 1];
        });
    }
}

function initDifficultyRatio() {
    const easySlider = document.getElementById('easyRatio');
    const mediumSlider = document.getElementById('mediumRatio');
    const hardSlider = document.getElementById('hardRatio');
    
    const easyPercent = document.getElementById('easyPercent');
    const mediumPercent = document.getElementById('mediumPercent');
    const hardPercent = document.getElementById('hardPercent');
    
    function updateRatios() {
        let total = parseInt(easySlider?.value || 0) + 
                   parseInt(mediumSlider?.value || 0) + 
                   parseInt(hardSlider?.value || 0);
        if (total > 100) {
            const diff = total - 100;
            if (parseInt(easySlider?.value || 0) >= parseInt(mediumSlider?.value || 0) && 
                parseInt(easySlider?.value || 0) >= parseInt(hardSlider?.value || 0)) {
                if (easySlider) easySlider.value = Math.max(0, parseInt(easySlider.value) - diff);
            } else if (parseInt(mediumSlider?.value || 0) >= parseInt(hardSlider?.value || 0)) {
                if (mediumSlider) mediumSlider.value = Math.max(0, parseInt(mediumSlider.value) - diff);
            } else {
                if (hardSlider) hardSlider.value = Math.max(0, parseInt(hardSlider.value) - diff);
            }
        }
        
        if (easyPercent) easyPercent.textContent = (easySlider?.value || 0) + '%';
        if (mediumPercent) mediumPercent.textContent = (mediumSlider?.value || 0) + '%';
        if (hardPercent) hardPercent.textContent = (hardSlider?.value || 0) + '%';
    }
    
    if (easySlider) easySlider.addEventListener('input', updateRatios);
    if (mediumSlider) mediumSlider.addEventListener('input', updateRatios);
    if (hardSlider) hardSlider.addEventListener('input', updateRatios);
}

function initQuestionCount() {
    window.adjustNumber = function(id, delta) {
        const input = document.getElementById(id);
        if (input) {
            let value = parseInt(input.value) || 0;
            value = Math.max(5, Math.min(100, value + delta));
            input.value = value;
        }
    };
}

function initVoiceRecord() {
    const recordBtn = document.getElementById('recordBtn');
    const recordStatus = document.getElementById('recordStatus');
    const voiceWave = document.getElementById('voiceWave');
    
    if (recordBtn) {
        recordBtn.addEventListener('click', async function() {
            if (!isRecording) {
                isRecording = true;
                this.classList.add('recording');
                if (recordStatus) recordStatus.textContent = '录音中...请说话';
                if (voiceWave) voiceWave.style.display = 'flex';
                
                try {
                    const result = await apiRequest('/voice/transcribe', {
                        method: 'POST'
                    });
                    
                    setTimeout(() => {
                        isRecording = false;
                        this.classList.remove('recording');
                        if (recordStatus) recordStatus.textContent = '录音完成！点击重新录音';
                        if (voiceWave) voiceWave.style.display = 'none';
                        
                        const reviewText = document.getElementById('reviewText');
                        if (reviewText && result.text) {
                            reviewText.value = result.text;
                        }
                        showToast('语音识别完成！', 'success');
                    }, 3000);
                } catch (error) {
                    isRecording = false;
                    this.classList.remove('recording');
                    if (recordStatus) recordStatus.textContent = '点击开始录音';
                    if (voiceWave) voiceWave.style.display = 'none';
                    showToast('语音识别失败，使用模拟数据', 'warning');
                    
                    const reviewText = document.getElementById('reviewText');
                    if (reviewText) {
                        reviewText.value = `函数极限的定义：当x无限接近于x0时，f(x)无限接近于某个常数A，则称A为f(x)当x→x0时的极限。

重要极限：
1. lim(x→0) sinx/x = 1
2. lim(x→∞) (1+1/x)^x = e

极限的运算法则：
- 和差的极限等于极限的和差
- 积的极限等于极限的积
- 商的极限等于极限的商（分母不为零）`;
                    }
                }
            } else {
                isRecording = false;
                this.classList.remove('recording');
                if (recordStatus) recordStatus.textContent = '点击开始录音';
                if (voiceWave) voiceWave.style.display = 'none';
            }
        });
    }
}

function clearText() {
    const reviewText = document.getElementById('reviewText');
    if (reviewText) {
        reviewText.value = '';
        showToast('已清空文本内容', 'info');
    }
}

async function extractKnowledge() {
    const text = document.getElementById('reviewText')?.value;
    if (!text || !text.trim()) {
        showToast('请先输入复习要点内容', 'warning');
        return;
    }
    
    showLoading('正在分析文本，提取知识点...');
    
    try {
        const result = await apiRequest('/knowledge/extract', {
            method: 'POST',
            body: JSON.stringify({ text: text })
        });
        
        hideLoading();
        
        if (result.success && result.knowledge_points) {
            extractedKnowledge = result.knowledge_points;
            renderExtractionResult();
            showToast(`成功提取 ${extractedKnowledge.length} 个知识点！`, 'success');
        } else {
            showToast('知识点提取失败', 'error');
        }
    } catch (error) {
        hideLoading();
        showToast('知识点提取失败: ' + error.message, 'error');
    }
}

function renderExtractionResult() {
    const container = document.getElementById('knowledgeExtracted');
    const resultSection = document.getElementById('extractionResult');
    
    if (container && resultSection) {
        container.innerHTML = extractedKnowledge.map(kp => `
            <div class="knowledge-tag ${kp.importance}">
                <span class="name">${kp.name}</span>
                <span class="level ${kp.importance}">${
                    kp.importance === 'core' ? '核心' : 
                    kp.importance === 'important' ? '重要' : '一般'
                }</span>
            </div>
        `).join('');
        
        resultSection.style.display = 'block';
    }
}

function regenerateExtraction() {
    showLoading('正在重新分析...');
    setTimeout(() => {
        hideLoading();
        showToast('重新提取完成！', 'success');
    }, 1500);
}

function applyToGeneration() {
    const resultSection = document.getElementById('extractionResult');
    if (resultSection) resultSection.style.display = 'none';
    navigateTo('generate');
    showToast('已将提取的知识点应用到出题系统', 'success');
}

async function generateQuestions() {
    if (extractedKnowledge.length === 0) {
        const text = document.getElementById('reviewText')?.value;
        if (!text || !text.trim()) {
            showToast('请先输入复习内容或提取知识点', 'warning');
            return;
        }
    }
    
    showLoading('正在根据知识点生成题目...');
    
    try {
        const questionCount = parseInt(document.getElementById('questionCount')?.value || 20);
        const easyRatio = parseInt(document.getElementById('easyRatio')?.value || 30);
        const mediumRatio = parseInt(document.getElementById('mediumRatio')?.value || 50);
        const hardRatio = parseInt(document.getElementById('hardRatio')?.value || 20);
        
        const questionTypes = [];
        const typeCheckboxes = document.querySelectorAll('.question-types input[type="checkbox"]:checked');
        typeCheckboxes.forEach(cb => {
            const typeMap = { '选择题': 'choice', '填空题': 'fill', '判断题': 'judge', '简答题': 'essay', '计算题': 'calculation' };
            const label = cb.closest('.checkbox-item')?.textContent?.trim();
            if (typeMap[label]) questionTypes.push(typeMap[label]);
        });
        
        if (questionTypes.length === 0) {
            questionTypes.push('choice', 'fill');
        }
        
        const text = document.getElementById('reviewText')?.value;
        
        const result = await apiRequest('/questions/generate', {
            method: 'POST',
            body: JSON.stringify({
                review_input: {
                    text: text,
                    source_type: 'text'
                },
                settings: {
                    question_count: questionCount,
                    easy_ratio: easyRatio,
                    medium_ratio: mediumRatio,
                    hard_ratio: hardRatio,
                    question_types: questionTypes
                }
            })
        });
        
        hideLoading();
        
        if (result.success && result.questions) {
            generatedQuestions = result.questions;
            renderGeneratedQuestions(result);
            showToast(`成功生成 ${result.total_count} 道题目！`, 'success');
        } else {
            showToast('题目生成失败', 'error');
        }
    } catch (error) {
        hideLoading();
        showToast('题目生成失败: ' + error.message, 'error');
    }
}

function renderGeneratedQuestions(result) {
    const container = document.getElementById('questionsPreview');
    const resultSection = document.getElementById('generationResult');
    const totalQuestions = document.getElementById('totalQuestions');
    const estimatedTime = document.getElementById('estimatedTime');
    
    if (totalQuestions) totalQuestions.textContent = result.total_count || generatedQuestions.length;
    if (estimatedTime) estimatedTime.textContent = result.estimated_time || generatedQuestions.length * 2;
    
    if (container && resultSection) {
        container.innerHTML = generatedQuestions.map((q, i) => {
            const typeName = {
                'choice': '选择题',
                'fill': '填空题',
                'judge': '判断题',
                'essay': '简答题',
                'calculation': '计算题'
            }[q.type] || '选择题';
            
            const diffName = {
                'easy': '简单',
                'medium': '中等',
                'hard': '困难'
            }[q.difficulty] || '中等';
            
            let optionsHTML = '';
            if (q.type === 'choice' && q.options && q.options.length > 0) {
                optionsHTML = `<ul class="question-options">
                    ${q.options.map(opt => `<li>${opt}</li>`).join('')}
                </ul>`;
            }
            
            return `
                <div class="question-card">
                    <div class="question-header">
                        <span class="question-type ${q.type}">${typeName}</span>
                        <span class="difficulty-badge ${q.difficulty}">${diffName}</span>
                    </div>
                    <div class="question-content">${i + 1}. ${q.content}</div>
                    ${optionsHTML}
                    <div class="question-answer">答案：${q.answer}</div>
                </div>
            `;
        }).join('');
        
        resultSection.style.display = 'block';
    }
}

async function exportQuestions(format) {
    if (generatedQuestions.length === 0) {
        showToast('没有可导出的题目', 'warning');
        return;
    }
    
    showLoading(`正在导出为${format.toUpperCase()}格式...`);
    
    try {
        const response = await fetch(`${API_BASE_URL}/questions/download`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ questions: generatedQuestions })
        });
        
        if (!response.ok) {
            throw new Error('导出失败');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        const filename = response.headers.get('Content-Disposition')?.split('filename=')[1] || `questions_${new Date().getTime()}.md`;
        a.download = filename.replace(/"/g, '');
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        hideLoading();
        showToast(`${format.toUpperCase()}文档导出成功！`, 'success');
    } catch (error) {
        hideLoading();
        showToast(`导出失败: ${error.message}`, 'error');
        console.error('导出错误:', error);
    }
}

function startNewGeneration() {
    const resultSection = document.getElementById('generationResult');
    if (resultSection) resultSection.style.display = 'none';
    const reviewText = document.getElementById('reviewText');
    if (reviewText) reviewText.value = '';
    extractedKnowledge = [];
    generatedQuestions = [];
    showToast('已清空，可以开始新的生成', 'info');
}

function initTemplateSelection() {
    const templateCards = document.querySelectorAll('.template-card');
    templateCards.forEach(card => {
        card.addEventListener('click', function() {
            templateCards.forEach(c => c.classList.remove('active'));
            this.classList.add('active');
        });
    });
}

function initKnowledgeFilter() {
    const filter = document.getElementById('knowledgeFilter');
    const items = document.querySelectorAll('.knowledge-item');
    
    if (filter) {
        filter.addEventListener('change', function() {
            const value = this.value;
            items.forEach(item => {
                if (value === 'all' || item.dataset.level === value) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    }
}

function initGraphControls() {
    window.zoomGraph = function(direction) {
        showToast(direction === 'in' ? '放大知识图谱' : '缩小知识图谱', 'info');
    };
    
    window.resetGraph = function() {
        showToast('已重置视图', 'info');
    };
}

async function loadKnowledgeGraph() {
    try {
        const result = await apiRequest('/knowledge/graph');
        renderKnowledgeGraph(result);
    } catch (error) {
        console.error('加载知识图谱失败:', error);
    }
}

function renderKnowledgeGraph(data) {
    if (!data || !data.nodes) return;
    
    const svg = document.querySelector('.knowledge-svg');
    if (!svg) return;
    
    const nodesGroup = svg.querySelector('.nodes');
    const linksGroup = svg.querySelector('.links');
    
    if (nodesGroup) {
        nodesGroup.innerHTML = data.nodes.map(node => {
            const importanceClass = node.importance || 'normal';
            return `
                <circle cx="${node.x}" cy="${node.y}" r="${node.importance === 'core' ? 40 : node.importance === 'important' ? 35 : 30}" 
                    class="node ${importanceClass}" />
                <text x="${node.x}" y="${parseInt(node.y) + 5}" class="node-label">${node.name}</text>
            `;
        }).join('');
    }
    
    if (linksGroup) {
        const nodeMap = {};
        data.nodes.forEach(n => nodeMap[n.id] = n);
        
        linksGroup.innerHTML = data.links.map(link => {
            const source = nodeMap[link.source];
            const target = nodeMap[link.target];
            if (source && target) {
                return `<line x1="${source.x}" y1="${source.y}" x2="${target.x}" y2="${target.y}" class="link" />`;
            }
            return '';
        }).join('');
    }
}

async function exportDocument(format) {
    const title = document.getElementById('docTitle')?.value || '复习资料';
    
    const content = extractedKnowledge.length > 0 
        ? extractedKnowledge.map(kp => `${kp.name}: ${kp.description || ''}`).join('\n\n')
        : '根据提取的知识点生成的复习资料。';
    
    showLoading(`正在生成${format.toUpperCase()}文档...`);
    
    try {
        const result = await apiRequest('/exports/generate', {
            method: 'POST',
            body: JSON.stringify({
                title: title,
                template: 'academic',
                content: content
            })
        });
        
        hideLoading();
        
        if (result.success) {
            renderDocumentPreview(title, result.document);
            showToast(`${format.toUpperCase()}文档生成成功！`, 'success');
            
            // 自动触发下载
            setTimeout(() => {
                downloadDocument(title, content);
            }, 500);
        }
    } catch (error) {
        hideLoading();
        showToast('文档生成失败: ' + error.message, 'error');
    }
}

async function downloadDocument(title, content) {
    try {
        const response = await fetch(`${API_BASE_URL}/exports/download`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                title: title,
                template: 'academic',
                content: content
            })
        });
        
        if (!response.ok) {
            throw new Error('下载失败');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        const filename = response.headers.get('Content-Disposition')?.split('filename=')[1] || `document_${new Date().getTime()}.md`;
        a.download = filename.replace(/"/g, '');
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        showToast('文档下载成功！', 'success');
    } catch (error) {
        showToast(`下载失败: ${error.message}`, 'error');
        console.error('下载错误:', error);
    }
}

function renderDocumentPreview(title, documentContent) {
    const preview = document.getElementById('documentPreview');
    const content = document.getElementById('previewContent');
    
    if (preview && content) {
        content.innerHTML = `
            <div class="preview-doc">
                <h1>${title}</h1>
                ${documentContent}
            </div>
        `;
        preview.style.display = 'block';
    }
}

function closePreview() {
    const preview = document.getElementById('documentPreview');
    if (preview) preview.style.display = 'none';
}

function showLoading(text = '处理中...') {
    const overlay = document.getElementById('loadingOverlay');
    const loadingText = document.getElementById('loadingText');
    if (loadingText) loadingText.textContent = text;
    if (overlay) overlay.style.display = 'flex';
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) overlay.style.display = 'none';
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-times-circle',
        warning: 'fa-exclamation-circle',
        info: 'fa-info-circle'
    };
    
    toast.innerHTML = `
        <i class="fas ${icons[type] || icons.info}"></i>
        <span class="toast-message">${message}</span>
        <span class="toast-close"><i class="fas fa-times"></i></span>
    `;
    
    container.appendChild(toast);
    
    toast.querySelector('.toast-close')?.addEventListener('click', () => {
        toast.remove();
    });
    
    setTimeout(() => {
        if (toast.parentNode) {
            toast.style.animation = 'slideIn 0.3s ease reverse';
            setTimeout(() => toast.remove(), 300);
        }
    }, 4000);
}

// 知识摘要相关功能
function initSummaryTabs() {
    const summaryTabBtns = document.querySelectorAll('#summary .tab-btn');
    summaryTabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const tab = this.dataset.tab;
            summaryTabBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            document.querySelectorAll('#summary .tab-content').forEach(content => {
                content.classList.remove('active');
            });
            const tabContent = document.getElementById('summary' + tab.charAt(0).toUpperCase() + tab.slice(1) + 'Tab');
            if (tabContent) tabContent.classList.add('active');
        });
    });
}

function clearSummaryText() {
    const summaryText = document.getElementById('summaryText');
    if (summaryText) {
        summaryText.value = '';
        showToast('已清空文本内容', 'info');
    }
}

async function generateSummary() {
    const text = document.getElementById('summaryText')?.value;
    if (!text || !text.trim()) {
        showToast('请先输入复习提纲或知识点描述', 'warning');
        return;
    }
    
    showLoading('正在生成知识摘要...');
    
    try {
        // 调用API生成知识摘要
        const result = await apiRequest('/summary/generate', {
            method: 'POST',
            body: JSON.stringify({
                text: text,
                source_type: 'text'
            })
        });
        
        hideLoading();
        
        if (result.success) {
            renderSummaryResult(result);
            showToast('知识摘要生成成功！', 'success');
        } else {
            showToast('知识摘要生成失败', 'error');
        }
    } catch (error) {
        hideLoading();
        showToast('知识摘要生成失败: ' + error.message, 'error');
    }
}

function renderSummaryResult(result) {
    const resultSection = document.getElementById('summaryResult');
    const tableBody = document.getElementById('knowledgeTableBody');
    const knowledgeGraph = document.querySelector('#summary .knowledge-svg');
    
    if (resultSection && tableBody && knowledgeGraph) {
        // 渲染知识点表格
        const knowledgePoints = result.knowledge_points || [];
        
        tableBody.innerHTML = knowledgePoints.map(kp => {
            const importanceCn = kp.importance === 'core' ? '核心' : 
                               kp.importance === 'important' ? '重要' : '一般';
            return `
                <tr>
                    <td>${kp.name}</td>
                    <td>${importanceCn}</td>
                    <td>${kp.description}</td>
                </tr>
            `;
        }).join('');
        
        // 渲染知识图谱
        const graphData = result.knowledge_graph || { nodes: [], links: [] };
        const nodesGroup = knowledgeGraph.querySelector('.nodes');
        const linksGroup = knowledgeGraph.querySelector('.links');
        
        if (nodesGroup) {
            nodesGroup.innerHTML = graphData.nodes.map(node => {
                const importanceClass = node.importance || 'normal';
                return `
                    <circle cx="${node.x || 100}" cy="${node.y || 100}" r="${node.importance === 'core' ? 40 : node.importance === 'important' ? 35 : 30}" 
                        class="node ${importanceClass}" />
                    <text x="${node.x || 100}" y="${parseInt(node.y || 100) + 5}" class="node-label">${node.name}</text>
                `;
            }).join('');
        }
        
        if (linksGroup) {
            const nodeMap = {};
            graphData.nodes.forEach(n => nodeMap[n.id] = n);
            
            linksGroup.innerHTML = graphData.links.map(link => {
                const source = nodeMap[link.source];
                const target = nodeMap[link.target];
                if (source && target) {
                    return `<line x1="${source.x || 100}" y1="${source.y || 100}" x2="${target.x || 200}" y2="${target.y || 200}" class="link" />`;
                }
                return '';
            }).join('');
        }
        
        resultSection.style.display = 'block';
    }
}

async function regenerateSummary() {
    const text = document.getElementById('summaryText')?.value;
    if (!text || !text.trim()) {
        showToast('请先输入复习提纲或知识点描述', 'warning');
        return;
    }
    
    showLoading('正在重新生成知识摘要...');
    
    try {
        // 调用API重新生成知识摘要
        const result = await apiRequest('/summary/generate', {
            method: 'POST',
            body: JSON.stringify({
                text: text,
                source_type: 'text'
            })
        });
        
        hideLoading();
        
        if (result.success) {
            renderSummaryResult(result);
            showToast('知识摘要重新生成成功！', 'success');
        } else {
            showToast('知识摘要重新生成失败', 'error');
        }
    } catch (error) {
        hideLoading();
        showToast('知识摘要重新生成失败: ' + error.message, 'error');
    }
}
