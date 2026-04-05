"""
图纸尺寸查看组件 - 前端JS
放在 frontend/static/drawing-viewer.js
"""

class DrawingViewer {
    constructor(apiBaseUrl = 'http://localhost:8000') {
        this.apiBase = apiBaseUrl;
    }

    /**
     * 获取图纸尺寸信息
     */
    async getDimensions(drawingNo) {
        try {
            const response = await fetch(`${this.apiBase}/drawings/${drawingNo}/dimensions`);
            const data = await response.json();
            return data;
        } catch (error) {
            return {
                status: 'error',
                error: error.message
            };
        }
    }

    /**
     * 渲染尺寸信息到页面
     */
    renderDimensions(containerId, data) {
        const container = document.getElementById(containerId);
        if (!container) return;

        if (data.status === 'error') {
            container.innerHTML = `
                <div class="error-box">
                    <h4>❌ 获取尺寸失败</h4>
                    <p>${data.error}</p>
                </div>
            `;
            return;
        }

        if (data.status === 'parsed' && data.dimensions) {
            // 有尺寸数据
            const dims = data.dimensions;
            const summary = dims.summary || {};
            const mainDims = summary.mainDimensions || [];

            let html = `
                <div class="dimensions-box">
                    <h4>📐 ${data.drawingNo} 尺寸信息</h4>
                    
                    <div class="dim-summary">
                        <div class="stat">
                            <span class="number">${summary.totalEntities || 0}</span>
                            <span class="label">实体总数</span>
                        </div>
                        <div class="stat">
                            <span class="number">${summary.totalDimensionsExtracted || 0}</span>
                            <span class="label">尺寸标注</span>
                        </div>
                        <div class="stat">
                            <span class="number">${dims.entityCount?.circles || 0}</span>
                            <span class="label">圆孔数量</span>
                        </div>
                    </div>
            `;

            // 主要尺寸列表
            if (mainDims.length > 0) {
                html += `
                    <div class="dim-list">
                        <h5>主要尺寸</h5>
                        <ul>
                `;
                mainDims.forEach(d => {
                    html += `<li>${d.description || d.text || JSON.stringify(d)}</li>`;
                });
                html += `</ul></div>`;
            }

            // 图纸范围
            if (dims.boundingBox) {
                html += `
                    <div class="bbox-info">
                        <h5>图纸范围</h5>
                        <p>宽度: ${dims.boundingBox.width} mm</p>
                        <p>高度: ${dims.boundingBox.height} mm</p>
                    </div>
                `;
            }

            html += `</div>`;
            container.innerHTML = html;

        } else if (data.status === 'dwg_only') {
            // 只有DWG，需要转换
            container.innerHTML = `
                <div class="convert-box">
                    <h4>⚠️ 需要转换格式</h4>
                    <p>当前只有DWG格式，需要转换为DXF才能解析尺寸。</p>
                    
                    <div class="convert-options">
                        <h5>转换方案：</h5>
                        ${data.solution?.options?.map(opt => `
                            <div class="option">
                                <strong>${opt.method}</strong>
                                <p>${opt.description}</p>
                                ${opt.url ? `<a href="${opt.url}" target="_blank">打开转换工具 →</a>` : ''}
                            </div>
                        `).join('') || ''}
                    </div>
                    
                    <p class="note">
                        💡 推荐方案：联系管理员预转换所有DXF文件后统一上传
                    </p>
                </div>
            `;
        } else {
            container.innerHTML = `
                <div class="info-box">
                    <p>图纸状态: ${data.status}</p>
                    <p>${data.note || ''}</p>
                </div>
            `;
        }
    }

    /**
     * 添加尺寸查看按钮到图纸卡片
     */
    addDimensionButton(drawingCard, drawingNo) {
        const btn = document.createElement('button');
        btn.className = 'btn-dimensions';
        btn.innerHTML = '📐 查看尺寸';
        btn.onclick = async () => {
            btn.disabled = true;
            btn.innerHTML = '⏳ 加载中...';
            
            // 创建或获取尺寸显示区域
            let dimContainer = drawingCard.querySelector('.dimensions-container');
            if (!dimContainer) {
                dimContainer = document.createElement('div');
                dimContainer.className = 'dimensions-container';
                drawingCard.appendChild(dimContainer);
            }
            
            const data = await this.getDimensions(drawingNo);
            this.renderDimensions(dimContainer.id || (dimContainer.id = `dim-${drawingNo}`), data);
            
            btn.innerHTML = '📐 刷新尺寸';
            btn.disabled = false;
        };
        
        drawingCard.querySelector('.meta')?.appendChild(btn);
    }

    /**
     * AI问答查询尺寸
     */
    async askAboutDimensions(question) {
        try {
            const response = await fetch(`${this.apiBase}/ai/query?question=${encodeURIComponent(question)}`);
            const data = await response.json();
            return data;
        } catch (error) {
            return {
                answer: `查询出错: ${error.message}`,
                error: error.message
            };
        }
    }
}

// CSS样式（可以放在style标签或单独CSS文件）
const drawingViewerStyles = `
.dimensions-box {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 15px;
    margin-top: 10px;
}

.dimensions-box h4 {
    margin: 0 0 15px 0;
    color: #667eea;
}

.dim-summary {
    display: flex;
    gap: 20px;
    margin-bottom: 15px;
}

.stat {
    text-align: center;
    padding: 10px;
    background: white;
    border-radius: 6px;
    min-width: 80px;
}

.stat .number {
    display: block;
    font-size: 24px;
    font-weight: bold;
    color: #667eea;
}

.stat .label {
    font-size: 12px;
    color: #666;
}

.dim-list h5 {
    margin: 15px 0 10px 0;
}

.dim-list ul {
    margin: 0;
    padding-left: 20px;
}

.dim-list li {
    margin: 5px 0;
    color: #333;
}

.bbox-info {
    margin-top: 15px;
    padding-top: 15px;
    border-top: 1px solid #e0e0e0;
}

.convert-box {
    background: #fff3e0;
    border-left: 4px solid #ff9800;
    padding: 15px;
    margin-top: 10px;
}

.convert-options {
    margin: 15px 0;
}

.option {
    background: white;
    padding: 10px;
    margin: 10px 0;
    border-radius: 6px;
}

.option a {
    color: #667eea;
    text-decoration: none;
}

.btn-dimensions {
    background: #667eea;
    color: white;
    border: none;
    padding: 6px 12px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 13px;
    margin-left: 10px;
}

.btn-dimensions:hover {
    background: #5a67d8;
}

.btn-dimensions:disabled {
    background: #ccc;
    cursor: not-allowed;
}
`;

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DrawingViewer;
}
