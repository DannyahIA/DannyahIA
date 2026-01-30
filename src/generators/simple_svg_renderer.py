"""
Simple SVG Renderer - Versão simplificada e robusta sem dependências externas

Esta versão:
- Remove imports de fontes externas (Google Fonts)
- Usa apenas fontes do sistema
- Simplifica gradientes
- Remove animações complexas
- Foca em compatibilidade máxima
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import math


class SimpleSVGRenderer:
    """
    Renderizador SVG simplificado e robusto.
    """
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.theme = self._load_theme()
        self.output_dir = self.base_path / "assets"
        self.output_dir.mkdir(exist_ok=True)
        
    def _load_theme(self, theme_name: str = "dark") -> Dict[str, Any]:
        theme_path = self.base_path / "themes" / f"{theme_name}.json"
        with open(theme_path, 'r') as f:
            return json.load(f)
    
    def create_simple_card(self, width: int, height: int, title: str, 
                          content: List[str]) -> str:
        """Cria um card SVG simples e robusto."""
        bg = self.theme['colors']['card']
        text_color = self.theme['colors']['text']
        accent = self.theme['colors']['accent']
        
        content_svg = '\n    '.join(content)
        
        return f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
    <style>
        text {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica', 'Arial', sans-serif;
            fill: {text_color};
        }}
        .title {{ font-size: 20px; font-weight: 600; fill: {accent}; }}
        .value {{ font-size: 28px; font-weight: 700; }}
        .label {{ font-size: 12px; opacity: 0.7; }}
    </style>
    <rect width="{width}" height="{height}" fill="{bg}" rx="12"/>
    <text class="title" x="24" y="40">{title}</text>
    {content_svg}
</svg>'''
    
    def generate_stats_simple(self, metrics: Dict[str, Any], 
                             output_name: str = "stats_simple.svg") -> str:
        """Gera card de estatísticas simples."""
        width, height = 800, 240
        
        stats = [
            {"label": "Commits", "value": metrics.get('total_commits', 0), "x": 60, "y": 120},
            {"label": "Pull Requests", "value": metrics.get('total_prs', 0), "x": 260, "y": 120},
            {"label": "Repositories", "value": metrics.get('total_repos', 0), "x": 460, "y": 120},
            {"label": "Streak", "value": f"{metrics.get('activity_streak', {}).get('current', 0)} days", "x": 660, "y": 120},
        ]
        
        content = []
        for stat in stats:
            content.append(f'''<g>
        <text class="label" x="{stat['x']}" y="{stat['y']}">{stat['label']}</text>
        <text class="value" x="{stat['x']}" y="{stat['y'] + 35}" fill="{self.theme['colors']['accent']}">{stat['value']}</text>
    </g>''')
        
        svg_content = self.create_simple_card(width, height, "📊 GitHub Statistics", content)
        
        output_path = self.output_dir / output_name
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        return str(output_path)
    
    def generate_languages_simple(self, metrics: Dict[str, Any],
                                  output_name: str = "languages_simple.svg") -> str:
        """Gera gráfico de linguagens simples."""
        width, height = 450, 280
        
        languages = metrics.get('top_languages', {})
        total = sum(languages.values()) or 1
        
        lang_data = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:6]
        
        # Cores simples para linguagens
        colors = {
            'Python': '#3572A5',
            'TypeScript': '#3178c6',
            'JavaScript': '#f1e05a',
            'Go': '#00ADD8',
            'PHP': '#4F5D95',
            'HTML': '#e34c26',
            'CSS': '#563d7c',
            'Shell': '#89e051',
        }
        
        content = []
        y_pos = 90
        
        for i, (lang, count) in enumerate(lang_data):
            percentage = (count / total) * 100
            bar_width = (percentage / 100) * 350
            color = colors.get(lang, self.theme['colors']['accent'])
            
            content.append(f'''<g>
        <rect x="24" y="{y_pos}" width="{bar_width}" height="24" fill="{color}" rx="4"/>
        <text x="34" y="{y_pos + 17}" style="font-size: 13px">{lang}</text>
        <text x="400" y="{y_pos + 17}" style="font-size: 12px; fill: {self.theme['colors']['textSecondary']}">{percentage:.1f}%</text>
    </g>''')
            y_pos += 32
        
        svg_content = self.create_simple_card(width, height, "💻 Top Languages", content)
        
        output_path = self.output_dir / output_name
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        return str(output_path)
    
    def generate_activity_simple(self, metrics: Dict[str, Any],
                                output_name: str = "activity_simple.svg") -> str:
        """Gera gráfico de atividade simples."""
        width, height = 450, 200
        
        daily_stats = metrics.get('daily_stats', {}).get('commits_per_day', [])
        total_commits = sum(day.get('count', 0) for day in daily_stats)
        
        content = []
        content.append(f'''<g>
        <text class="label" x="24" y="90">Last 30 days</text>
        <text class="value" x="24" y="125" fill="{self.theme['colors']['accent']}" style="font-size: 36px">{total_commits}</text>
        <text class="label" x="24" y="150">total commits</text>
    </g>''')
        
        # Mini barras
        if daily_stats:
            bar_x = 180
            bar_y = 90
            max_count = max((d.get('count', 0) for d in daily_stats), default=1)
            
            for i, day in enumerate(daily_stats[-20:]):
                count = day.get('count', 0)
                bar_height = (count / max_count) * 60 if max_count > 0 else 0
                x = bar_x + i * 12
                y = bar_y + 60 - bar_height
                
                content.append(f'<rect x="{x}" y="{y}" width="8" height="{bar_height}" fill="{self.theme["colors"]["accent"]}" rx="2"/>')
        
        svg_content = self.create_simple_card(width, height, "📈 Recent Activity", content)
        
        output_path = self.output_dir / output_name
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        return str(output_path)
    
    def generate_streak_simple(self, metrics: Dict[str, Any],
                              output_name: str = "streak_simple.svg") -> str:
        """Gera card de streak simples."""
        width, height = 450, 180
        
        current_streak = metrics.get('activity_streak', {}).get('current', 0)
        longest_streak = metrics.get('activity_streak', {}).get('longest', 0)
        
        content = []
        content.append(f'''<g>
        <circle cx="100" cy="110" r="40" fill="{self.theme['colors']['accent']}" opacity="0.2"/>
        <text class="value" x="100" y="120" text-anchor="middle" style="font-size: 32px" fill="{self.theme['colors']['accent']}">{current_streak}</text>
        <text class="label" x="100" y="160" text-anchor="middle">Current Streak</text>
    </g>''')
        
        content.append(f'''<g>
        <text class="label" x="220" y="100">Longest Streak</text>
        <text class="value" x="220" y="130" style="font-size: 24px" fill="{self.theme['colors']['success']}">{longest_streak} days</text>
    </g>''')
        
        svg_content = self.create_simple_card(width, height, "🔥 Contribution Streak", content)
        
        output_path = self.output_dir / output_name
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        return str(output_path)
    
    def generate_tier_simple(self, metrics: Dict[str, Any],
                            output_name: str = "tier_simple.svg") -> str:
        """Gera card de tier simples."""
        width, height = 450, 200
        
        total_commits = metrics.get('total_commits', 0)
        total_repos = metrics.get('total_repos', 0)
        current_streak = metrics.get('activity_streak', {}).get('current', 0)
        
        score = total_commits * 2 + total_repos * 5 + current_streak * 3
        
        if score >= 500:
            tier = "Elite"
            tier_icon = "👑"
            color = self.theme['colors']['purple']
        elif score >= 300:
            tier = "Expert"
            tier_icon = "💎"
            color = self.theme['colors']['accent']
        elif score >= 150:
            tier = "Advanced"
            tier_icon = "⚡"
            color = self.theme['colors']['success']
        elif score >= 50:
            tier = "Intermediate"
            tier_icon = "🌟"
            color = self.theme['colors']['warning']
        else:
            tier = "Beginner"
            tier_icon = "🌱"
            color = self.theme['colors']['success']
        
        content = []
        content.append(f'''<g>
        <rect x="24" y="70" width="180" height="90" rx="12" fill="{color}" opacity="0.15"/>
        <text x="114" y="110" text-anchor="middle" style="font-size: 36px">{tier_icon}</text>
        <text x="114" y="140" text-anchor="middle" class="value" style="font-size: 18px" fill="{color}">{tier}</text>
    </g>''')
        
        content.append(f'''<g>
        <text class="label" x="240" y="100">Developer Score</text>
        <text class="value" x="240" y="135" style="font-size: 28px">{score}</text>
    </g>''')
        
        svg_content = self.create_simple_card(width, height, "⭐ Developer Tier", content)
        
        output_path = self.output_dir / output_name
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        return str(output_path)
