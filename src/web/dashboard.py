"""
TokenMeter Web Dashboard
简单的 Web 仪表盘
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

router = APIRouter()

# 模板目录
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """主仪表盘页面"""
    html_content = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TokenMeter - AI Cost Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f172a;
            color: #e2e8f0;
            min-height: 100vh;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            text-align: center;
        }
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }
        .header p {
            opacity: 0.9;
            font-size: 1.1rem;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        .stat-card {
            background: #1e293b;
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid #334155;
            transition: transform 0.2s;
        }
        .stat-card:hover {
            transform: translateY(-4px);
            border-color: #667eea;
        }
        .stat-card h3 {
            color: #94a3b8;
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
        }
        .stat-card .value {
            font-size: 2rem;
            font-weight: 700;
            color: #f8fafc;
        }
        .stat-card .change {
            font-size: 0.875rem;
            margin-top: 0.5rem;
        }
        .change.positive { color: #4ade80; }
        .change.negative { color: #f87171; }
        
        .section {
            background: #1e293b;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            border: 1px solid #334155;
        }
        .section h2 {
            font-size: 1.25rem;
            margin-bottom: 1rem;
            color: #f8fafc;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            text-align: left;
            padding: 0.75rem;
            border-bottom: 1px solid #334155;
        }
        th {
            color: #94a3b8;
            font-weight: 500;
            font-size: 0.875rem;
        }
        tr:hover {
            background: #334155;
        }
        
        .loading {
            text-align: center;
            padding: 3rem;
            color: #64748b;
        }
        
        .refresh-btn {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            background: #667eea;
            color: white;
            border: none;
            padding: 1rem 1.5rem;
            border-radius: 50px;
            cursor: pointer;
            font-size: 1rem;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
            transition: all 0.2s;
        }
        .refresh-btn:hover {
            background: #764ba2;
            transform: scale(1.05);
        }
        
        .badge {
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 500;
        }
        .badge-openai { background: #10a37f; color: white; }
        .badge-azure { background: #0078d4; color: white; }
        .badge-claude { background: #cc785c; color: white; }
        
        @media (max-width: 768px) {
            .header h1 { font-size: 1.75rem; }
            .container { padding: 1rem; }
            .stat-card .value { font-size: 1.5rem; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎫 TokenMeter</h1>
        <p>企业级 MaaS 成本追踪与归因分析平台</p>
    </div>
    
    <div class="container">
        <div class="stats-grid" id="stats-grid">
            <div class="loading">加载中...</div>
        </div>
        
        <div class="section">
            <h2>📊 项目成本排行</h2>
            <div id="projects-table"><div class="loading">加载中...</div></div>
        </div>
        
        <div class="section">
            <h2>🏢 团队成本排行</h2>
            <div id="teams-table"><div class="loading">加载中...</div></div>
        </div>
        
        <div class="section">
            <h2>🤖 模型使用统计</h2>
            <div id="models-table"><div class="loading">加载中...</div></div>
        </div>
    </div>
    
    <button class="refresh-btn" onclick="loadAllData()">🔄 刷新数据</button>
    
    <script>
        const API_BASE = '/api/v1';
        
        // 格式化数字
        function formatNumber(num) {
            if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
            if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
            return num.toLocaleString();
        }
        
        // 格式化货币
        function formatCurrency(num) {
            return '$' + num.toFixed(4);
        }
        
        // 获取 Provider Badge
        function getProviderBadge(provider) {
            const badges = {
                'openai': '<span class="badge badge-openai">OpenAI</span>',
                'azure': '<span class="badge badge-azure">Azure</span>',
                'claude': '<span class="badge badge-claude">Claude</span>'
            };
            return badges[provider.toLowerCase()] || provider;
        }
        
        // 加载汇总数据
        async function loadSummary() {
            try {
                const res = await fetch(`${API_BASE}/stats/summary?days=30`);
                const data = await res.json();
                
                const summary = data.summary;
                const providers = data.by_provider;
                const models = data.by_model;
                
                // 计算主要提供商
                let mainProvider = providers[0] || {provider: '-', cost: 0};
                
                document.getElementById('stats-grid').innerHTML = `
                    <div class="stat-card">
                        <h3>30天总成本</h3>
                        <div class="value">${formatCurrency(summary.total_cost)}</div>
                        <div class="change">总计</div>
                    </div>
                    <div class="stat-card">
                        <h3>总调用次数</h3>
                        <div class="value">${formatNumber(summary.total_requests)}</div>
                        <div class="change">API 请求</div>
                    </div>
                    <div class="stat-card">
                        <h3>总 Token 用量</h3>
                        <div class="value">${formatNumber(summary.total_tokens)}</div>
                        <div class="change">输入 + 输出</div>
                    </div>
                    <div class="stat-card">
                        <h3>主要提供商</h3>
                        <div class="value" style="font-size: 1.25rem;">${getProviderBadge(mainProvider.provider)}</div>
                        <div class="change">${formatCurrency(mainProvider.cost)}</div>
                    </div>
                `;
                
                // 渲染模型统计
                document.getElementById('models-table').innerHTML = `
                    <table>
                        <thead>
                            <tr>
                                <th>模型</th>
                                <th>调用次数</th>
                                <th>Token 数</th>
                                <th>成本</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${models.map(m => `
                                <tr>
                                    <td>${m.model}</td>
                                    <td>${formatNumber(m.requests)}</td>
                                    <td>${formatNumber(m.tokens)}</td>
                                    <td>${formatCurrency(m.cost)}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                `;
            } catch (e) {
                console.error('Failed to load summary:', e);
            }
        }
        
        // 加载项目统计
        async function loadProjects() {
            try {
                const res = await fetch(`${API_BASE}/stats/projects?days=30`);
                const data = await res.json();
                
                document.getElementById('projects-table').innerHTML = `
                    <table>
                        <thead>
                            <tr>
                                <th>项目</th>
                                <th>调用次数</th>
                                <th>Token 数</th>
                                <th>成本</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.projects.map(p => `
                                <tr>
                                    <td>${p.project}</td>
                                    <td>${formatNumber(p.requests)}</td>
                                    <td>${formatNumber(p.tokens)}</td>
                                    <td>${formatCurrency(p.cost)}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                `;
            } catch (e) {
                console.error('Failed to load projects:', e);
            }
        }
        
        // 加载团队统计
        async function loadTeams() {
            try {
                const res = await fetch(`${API_BASE}/stats/teams?days=30`);
                const data = await res.json();
                
                document.getElementById('teams-table').innerHTML = `
                    <table>
                        <thead>
                            <tr>
                                <th>团队</th>
                                <th>调用次数</th>
                                <th>Token 数</th>
                                <th>成本</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.teams.map(t => `
                                <tr>
                                    <td>${t.team}</td>
                                    <td>${formatNumber(t.requests)}</td>
                                    <td>${formatNumber(t.tokens)}</td>
                                    <td>${formatCurrency(t.cost)}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                `;
            } catch (e) {
                console.error('Failed to load teams:', e);
            }
        }
        
        // 加载所有数据
        function loadAllData() {
            loadSummary();
            loadProjects();
            loadTeams();
        }
        
        // 页面加载时自动刷新
        loadAllData();
        
        // 每30秒自动刷新
        setInterval(loadAllData, 30000);
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)
