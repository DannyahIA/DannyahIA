"""
Enhanced SVG Renderer - Versão com animações CSS e métricas avançadas

Mantém a simplicidade (sem dependências externas) mas adiciona:
- Animações CSS suaves
- Comparações temporais (mês anterior)
- Sistema de scoring contextualizado
- Visual polish e efeitos
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta
import math


class EnhancedSVGRenderer:
    """
    Renderizador SVG aprimorado com animações e métricas avançadas.
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
    
    def _create_animations(self) -> str:
        """Cria animações CSS suaves e performáticas."""
        return """
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        @keyframes slideUp {
            from { transform: translateY(10px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        @keyframes scaleIn {
            from { transform: scale(0.95); opacity: 0; }
            to { transform: scale(1); opacity: 1; }
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        @keyframes glow {
            0%, 100% { filter: drop-shadow(0 0 3px currentColor); }
            50% { filter: drop-shadow(0 0 8px currentColor); }
        }
        .animated { animation: fadeIn 0.6s ease-out; }
        .slide-up { animation: slideUp 0.5s ease-out; }
        .scale-in { animation: scaleIn 0.4s ease-out; }
        .pulse { animation: pulse 2s ease-in-out infinite; }
        .glow { animation: glow 2s ease-in-out infinite; }
        """
    
    def _create_base_styles(self) -> str:
        """Estilos base com tipografia do sistema."""
        text_color = self.theme['colors']['text']
        secondary = self.theme['colors']['textSecondary']
        
        return f"""
        * {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica', 'Arial', sans-serif;
        }}
        text {{ fill: {text_color}; }}
        .title {{ 
            font-size: 20px; 
            font-weight: 600; 
            fill: {self.theme['colors']['accent']}; 
        }}
        .subtitle {{ 
            font-size: 14px; 
            font-weight: 500; 
            fill: {secondary}; 
        }}
        .value {{ font-size: 28px; font-weight: 700; }}
        .value-large {{ font-size: 36px; font-weight: 700; }}
        .label {{ font-size: 12px; opacity: 0.7; }}
        .label-small {{ font-size: 10px; opacity: 0.6; }}
        .badge {{
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .metric-change {{
            font-size: 13px;
            font-weight: 600;
        }}
        .trend-up {{ fill: {self.theme['colors']['success']}; }}
        .trend-down {{ fill: {self.theme['colors']['danger']}; }}
        .trend-neutral {{ fill: {secondary}; }}
        """
    
    def create_card(self, width: int, height: int, title: str, 
                   content: List[str], subtitle: str = "") -> str:
        """Cria um card SVG animado."""
        bg = self.theme['colors']['card']
        
        subtitle_svg = f'<text class="subtitle animated" x="24" y="65" style="animation-delay: 0.1s">{subtitle}</text>' if subtitle else ""
        content_svg = '\n    '.join(content)
        
        return f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
    <style>
        {self._create_base_styles()}
        {self._create_animations()}
    </style>
    <rect class="scale-in" width="{width}" height="{height}" fill="{bg}" rx="12"/>
    <text class="title animated" x="24" y="40">{title}</text>
    {subtitle_svg}
    {content_svg}
</svg>'''
    
    def _calculate_tier(self, metrics: Dict[str, Any]) -> Tuple[str, str, str, str]:
        """
        Calcula tier do desenvolvedor com contexto.
        Retorna: (tier, icon, color, description)
        """
        total_commits = metrics.get('total_commits', 0)
        total_repos = metrics.get('total_repos', 0)
        current_streak = metrics.get('activity_streak', {}).get('current', 0)
        total_prs = metrics.get('total_prs', 0)
        
        # Scoring ponderado
        score = (
            total_commits * 2 +      # Commits contam muito
            total_repos * 5 +        # Repos são importantes
            current_streak * 3 +     # Consistência é valiosa
            total_prs * 4            # PRs mostram colaboração
        )
        
        # Tiers com contexto
        if score >= 1000:
            return "Elite", "👑", self.theme['colors']['purple'], "Top 1% developers"
        elif score >= 600:
            return "Expert", "💎", self.theme['colors']['accent'], "Highly experienced"
        elif score >= 350:
            return "Advanced", "⚡", self.theme['colors']['success'], "Solid experience"
        elif score >= 150:
            return "Intermediate", "🌟", self.theme['colors']['warning'], "Growing developer"
        else:
            return "Beginner", "🌱", self.theme['colors']['success'], "Starting journey"
    
    def _get_trend_indicator(self, current: float, previous: float) -> Tuple[str, str, str]:
        """
        Retorna indicador de tendência.
        Returns: (arrow, class, percentage_change)
        """
        if previous == 0:
            return "●", "trend-neutral", "New"
        
        change = ((current - previous) / previous) * 100
        
        if abs(change) < 1:
            return "●", "trend-neutral", "±0%"
        elif change > 0:
            return "↑", "trend-up", f"+{change:.0f}%"
        else:
            return "↓", "trend-down", f"{change:.0f}%"
    
    def generate_stats_hero(self, metrics: Dict[str, Any], 
                           history: Dict[str, Any] = None,
                           output_name: str = "stats_hero.svg") -> str:
        """Gera card hero com estatísticas e comparações - 1200px."""
        width, height = 1200, 320
        
        # Dados atuais
        total_commits = metrics.get('total_commits', 0)
        total_prs = metrics.get('total_prs', 0)
        total_repos = metrics.get('total_repos', 0)
        current_streak = metrics.get('activity_streak', {}).get('current', 0)
        contributors = metrics.get('contributors', 0)
        stars = metrics.get('total_stars', 0)
        
        # Dados históricos (30 dias atrás)
        prev_data = {}
        if history:
            months = history.get('monthly_snapshots', [])
            if len(months) >= 2:
                prev_data = months[-2]  # Mês anterior
        
        prev_commits = prev_data.get('total_commits', total_commits)
        prev_prs = prev_data.get('total_prs', total_prs)
        prev_repos = prev_data.get('total_repos', total_repos)
        
        # Calcular tier
        tier, tier_icon, tier_color, tier_desc = self._calculate_tier(metrics)
        
        # Preparar estatísticas com trends em 2 linhas de 3 cards
        stats_row1 = [
            {
                "label": "Total Commits",
                "value": total_commits,
                "prev": prev_commits,
                "x": 40,
                "y": 140,
                "icon": "📝",
                "width": 360
            },
            {
                "label": "Pull Requests",
                "value": total_prs,
                "prev": prev_prs,
                "x": 420,
                "y": 140,
                "icon": "🔀",
                "width": 360
            },
            {
                "label": "Repositories",
                "value": total_repos,
                "prev": prev_repos,
                "x": 800,
                "y": 140,
                "icon": "📦",
                "width": 360
            },
        ]
        
        stats_row2 = [
            {
                "label": "Current Streak",
                "value": current_streak,
                "prev": current_streak,
                "x": 40,
                "y": 240,
                "icon": "🔥",
                "width": 360
            },
            {
                "label": "Contributors",
                "value": contributors,
                "prev": contributors,
                "x": 420,
                "y": 240,
                "icon": "👥",
                "width": 360
            },
            {
                "label": "Stars Earned",
                "value": stars,
                "prev": stars,
                "x": 800,
                "y": 240,
                "icon": "⭐",
                "width": 360
            },
        ]
        
        content = []
        
        # Título com tier badge
        content.append(f'''<g class="fade-in">
    <text class="title" x="40" y="45">GitHub Statistics Overview</text>
    <rect x="920" y="22" width="240" height="36" fill="{tier_color}" rx="18" opacity="0.2"/>
    <text x="940" y="46" style="font-size: 18px">{tier_icon}</text>
    <text x="970" y="46" style="font-size: 16px; font-weight: 700; fill: {tier_color}">{tier}</text>
</g>''')
        
        # Linha divisória
        content.append(f'''<line x1="40" y1="75" x2="1160" y2="75" stroke="{self.theme['colors']['border']}" stroke-width="1" opacity="0.3"/>''')
        
        # Primeira linha de stats
        delay = 0.2
        for stat in stats_row1:
            arrow, trend_class, change = self._get_trend_indicator(stat['value'], stat['prev'])
            trend_color = self.theme['colors']['success'] if arrow == "↑" else self.theme['colors']['error'] if arrow == "↓" else self.theme['colors']['textSecondary']
            
            content.append(f'''<g class="slide-up" style="animation-delay: {delay}s">
    <!-- Card background -->
    <rect x="{stat['x']}" y="{stat['y'] - 30}" width="{stat['width']}" height="85" 
          fill="{self.theme['colors']['backgroundSecondary']}" rx="10" opacity="0.5"/>
    
    <!-- Icon -->
    <text x="{stat['x'] + 20}" y="{stat['y'] - 5}" style="font-size: 24px">{stat['icon']}</text>
    
    <!-- Label -->
    <text class="label" x="{stat['x'] + 20}" y="{stat['y'] + 20}">{stat['label']}</text>
    
    <!-- Value -->
    <text x="{stat['x'] + 20}" y="{stat['y'] + 48}" style="font-size: 32px; font-weight: 700; fill: {self.theme['colors']['accent']}">{stat['value']}</text>
    
    <!-- Trend badge -->
    <rect x="{stat['x'] + stat['width'] - 90}" y="{stat['y'] + 25}" width="70" height="24" fill="{trend_color}" rx="12" opacity="0.2"/>
    <text x="{stat['x'] + stat['width'] - 55}" y="{stat['y'] + 42}" text-anchor="middle" 
          style="font-size: 12px; font-weight: 700; fill: {trend_color}">{arrow} {change}</text>
</g>''')
            delay += 0.1
        
        # Segunda linha de stats
        for stat in stats_row2:
            arrow, trend_class, change = self._get_trend_indicator(stat['value'], stat['prev'])
            trend_color = self.theme['colors']['success'] if arrow == "↑" else self.theme['colors']['error'] if arrow == "↓" else self.theme['colors']['textSecondary']
            
            content.append(f'''<g class="slide-up" style="animation-delay: {delay}s">
    <!-- Card background -->
    <rect x="{stat['x']}" y="{stat['y'] - 30}" width="{stat['width']}" height="85" 
          fill="{self.theme['colors']['backgroundSecondary']}" rx="10" opacity="0.5"/>
    
    <!-- Icon -->
    <text x="{stat['x'] + 20}" y="{stat['y'] - 5}" style="font-size: 24px">{stat['icon']}</text>
    
    <!-- Label -->
    <text class="label" x="{stat['x'] + 20}" y="{stat['y'] + 20}">{stat['label']}</text>
    
    <!-- Value -->
    <text x="{stat['x'] + 20}" y="{stat['y'] + 48}" style="font-size: 32px; font-weight: 700; fill: {self.theme['colors']['accent']}">{stat['value']}</text>
    
    <!-- Trend badge -->
    <rect x="{stat['x'] + stat['width'] - 90}" y="{stat['y'] + 25}" width="70" height="24" fill="{trend_color}" rx="12" opacity="0.2"/>
    <text x="{stat['x'] + stat['width'] - 55}" y="{stat['y'] + 42}" text-anchor="middle" 
          style="font-size: 12px; font-weight: 700; fill: {trend_color}">{arrow} {change}</text>
</g>''')
            delay += 0.1
        
        subtitle = f"📊 Last updated: {datetime.now().strftime('%B %d, %Y')}"
        svg_content = self.create_card(width, height, "", content, subtitle)
        
        output_path = self.output_dir / output_name
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        return str(output_path)
    
    def generate_language_chart(self, metrics: Dict[str, Any],
                                output_name: str = "language_chart.svg") -> str:
        """Gera gráfico de linguagens em 2 colunas com visualizações sofisticadas."""
        width, height = 1200, 500
        
        languages = metrics.get('top_languages', {})
        total = sum(languages.values()) or 1
        
        lang_data = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:12]
        
        # Cores específicas por linguagem
        colors = {
            'Python': '#3572A5',
            'TypeScript': '#3178c6',
            'JavaScript': '#f1e05a',
            'Go': '#00ADD8',
            'PHP': '#4F5D95',
            'Java': '#b07219',
            'C++': '#f34b7d',
            'Ruby': '#701516',
            'HTML': '#e34c26',
            'CSS': '#563d7c',
            'Shell': '#89e051',
            'Rust': '#dea584',
            'Swift': '#ffac45',
            'Kotlin': '#A97BFF',
            'C#': '#178600',
            'Dart': '#00B4AB',
        }
        
        # Ícones por linguagem
        icons = {
            'Python': '🐍',
            'TypeScript': '📘',
            'JavaScript': '📙',
            'Go': '🔷',
            'PHP': '🐘',
            'Java': '☕',
            'C++': '⚙️',
            'Ruby': '💎',
            'HTML': '🌐',
            'CSS': '🎨',
            'Shell': '🐚',
            'Rust': '🦀',
            'Swift': '🍎',
            'Kotlin': '🅺',
            'C#': '#️⃣',
            'Dart': '🎯',
        }
        
        content = []
        
        # Coluna esquerda: Top 6 com barras horizontais
        content.append(f'''<g class="fade-in">
    <text x="30" y="95" style="font-size: 16px; font-weight: 700; fill: {self.theme['colors']['text']}">
        📊 Primary Languages
    </text>
    <line x1="30" y1="105" x2="400" y2="105" stroke="{self.theme['colors']['accent']}" stroke-width="2" opacity="0.3"/>
</g>''')
        
        y_pos = 130
        delay = 0.2
        
        for i, (lang, count) in enumerate(lang_data[:6]):
            percentage = (count / total) * 100
            bar_width = (percentage / 100) * 320
            color = colors.get(lang, self.theme['colors']['accent'])
            icon = icons.get(lang, '📝')
            
            content.append(f'''<g class="slide-up" style="animation-delay: {delay}s">
    <!-- Background bar -->
    <rect x="30" y="{y_pos}" width="320" height="40" fill="{self.theme['colors']['border']}" rx="8" opacity="0.15"/>
    
    <!-- Animated progress bar -->
    <rect x="30" y="{y_pos}" width="0" height="40" fill="url(#lang-gradient-{i})" rx="8" opacity="0.9">
        <animate attributeName="width" from="0" to="{bar_width}" dur="1.2s" begin="{delay}s" fill="freeze"/>
    </rect>
    
    <!-- Language info -->
    <text x="42" y="{y_pos + 20}" style="font-size: 14px; font-weight: 600; fill: {self.theme['colors']['text']}">
        {icon} {lang}
    </text>
    <text x="42" y="{y_pos + 34}" style="font-size: 10px; fill: {self.theme['colors']['textSecondary']}">
        {count} files
    </text>
    
    <!-- Percentage badge -->
    <rect x="360" y="{y_pos + 8}" width="60" height="24" fill="{color}" rx="12" opacity="0.2"/>
    <text x="390" y="{y_pos + 24}" text-anchor="middle" style="font-size: 12px; font-weight: 700; fill: {color}">
        {percentage:.1f}%
    </text>
</g>
<defs>
    <linearGradient id="lang-gradient-{i}" x1="0%" y1="0%" x2="100%" y2="0%">
        <stop offset="0%" style="stop-color:{color};stop-opacity:0.6" />
        <stop offset="100%" style="stop-color:{color};stop-opacity:0.9" />
    </linearGradient>
</defs>''')
            y_pos += 52
            delay += 0.1
        
        # Coluna direita: Linguagens secundárias em grid compacto
        content.append(f'''<g class="fade-in" style="animation-delay: 0.4s">
    <text x="470" y="95" style="font-size: 16px; font-weight: 700; fill: {self.theme['colors']['text']}">
        🔧 Secondary Languages
    </text>
    <line x1="470" y1="105" x2="840" y2="105" stroke="{self.theme['colors']['accent']}" stroke-width="2" opacity="0.3"/>
</g>''')
        
        # Grid de linguagens secundárias (6-12)
        grid_x = 470
        grid_y = 130
        col = 0
        delay = 0.6
        
        for i, (lang, count) in enumerate(lang_data[6:12]):
            percentage = (count / total) * 100
            color = colors.get(lang, self.theme['colors']['accent'])
            icon = icons.get(lang, '📝')
            
            x_pos = grid_x + (col * 190)
            y_pos = grid_y + ((i // 2) * 105)
            
            content.append(f'''<g class="scale-in" style="animation-delay: {delay}s">
    <!-- Card background -->
    <rect x="{x_pos}" y="{y_pos}" width="180" height="90" fill="{self.theme['colors']['card']}" rx="12" 
          stroke="{color}" stroke-width="2" opacity="0.8"/>
    
    <!-- Language icon and name -->
    <text x="{x_pos + 15}" y="{y_pos + 30}" style="font-size: 24px">{icon}</text>
    <text x="{x_pos + 50}" y="{y_pos + 32}" style="font-size: 14px; font-weight: 600; fill: {self.theme['colors']['text']}">
        {lang}
    </text>
    
    <!-- Stats -->
    <text x="{x_pos + 15}" y="{y_pos + 55}" style="font-size: 11px; fill: {self.theme['colors']['textSecondary']}">
        Files: {count}
    </text>
    
    <!-- Circular progress indicator -->
    <circle cx="{x_pos + 155}" cy="{y_pos + 65}" r="18" fill="none" 
            stroke="{self.theme['colors']['border']}" stroke-width="3" opacity="0.3"/>
    <circle cx="{x_pos + 155}" cy="{y_pos + 65}" r="18" fill="none" 
            stroke="{color}" stroke-width="3" opacity="0.9"
            stroke-dasharray="{percentage * 1.13} 113" 
            transform="rotate(-90 {x_pos + 155} {y_pos + 65})">
        <animate attributeName="stroke-dasharray" from="0 113" to="{percentage * 1.13} 113" 
                 dur="1s" begin="{delay}s" fill="freeze"/>
    </circle>
    <text x="{x_pos + 155}" y="{y_pos + 70}" text-anchor="middle" 
          style="font-size: 9px; font-weight: 700; fill: {color}">
        {percentage:.0f}%
    </text>
</g>''')
            col = 1 - col
            delay += 0.08
        
        # Estatísticas gerais no rodapé
        total_langs = len(lang_data)
        most_used = lang_data[0] if lang_data else ("N/A", 0)
        most_used_pct = (most_used[1] / total) * 100 if total > 0 else 0
        
        content.append(f'''<g class="fade-in" style="animation-delay: 1s">
    <rect x="30" y="430" width="840" height="32" fill="{self.theme['colors']['accent']}" rx="8" opacity="0.1"/>
    <text x="45" y="451" style="font-size: 12px; font-weight: 600; fill: {self.theme['colors']['textSecondary']}">
        📈 Total: {total_langs} languages • 🏆 Most used: {most_used[0]} ({most_used_pct:.1f}%) • 📁 Total files: {total}
    </text>
</g>''')
        
        subtitle = f"Last updated: {datetime.now().strftime('%B %d, %Y')}"
        svg_content = self.create_card(width, height, "💻 Language Distribution", content, subtitle)
        
        output_path = self.output_dir / output_name
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        return str(output_path)
    
    def generate_activity_timeline(self, metrics: Dict[str, Any],
                                   output_name: str = "activity_timeline.svg") -> str:
        """Gera timeline de atividade com comparação."""
        width, height = 600, 240
        
        daily_stats = metrics.get('daily_stats', {}).get('commits_per_day', [])
        
        # Últimos 30 dias
        recent_days = daily_stats[-30:] if len(daily_stats) >= 30 else daily_stats
        total_commits = sum(day.get('count', 0) for day in recent_days)
        avg_per_day = total_commits / len(recent_days) if recent_days else 0
        
        # Comparar com período anterior
        previous_days = daily_stats[-60:-30] if len(daily_stats) >= 60 else []
        prev_total = sum(day.get('count', 0) for day in previous_days) if previous_days else total_commits
        
        arrow, trend_class, change = self._get_trend_indicator(total_commits, prev_total)
        
        content = []
        
        # Métricas principais
        content.append(f'''<g class="scale-in">
        <text class="label" x="24" y="110">Last 30 days</text>
        <text class="value-large" x="24" y="150" fill="{self.theme['colors']['accent']}">{total_commits}</text>
        <text class="metric-change {trend_class}" x="24" y="175">{arrow} {change} vs previous</text>
        <text class="label-small" x="24" y="195">Avg: {avg_per_day:.1f}/day</text>
    </g>''')
        
        # Mini gráfico de barras
        if recent_days:
            bar_x = 200
            bar_y = 100
            max_count = max((d.get('count', 0) for d in recent_days), default=1)
            
            for i, day in enumerate(recent_days[-25:]):
                count = day.get('count', 0)
                bar_height = (count / max_count) * 70 if max_count > 0 else 0
                x = bar_x + i * 9
                y = bar_y + 70 - bar_height
                
                opacity = 0.4 + (count / max_count) * 0.6 if max_count > 0 else 0.4
                
                content.append(f'''<rect class="animated" x="{x}" y="{y}" width="6" height="{bar_height}" 
                    fill="{self.theme['colors']['accent']}" rx="3" opacity="{opacity}" 
                    style="animation-delay: {i * 0.02}s">
                    <title>{count} commits on {day.get('date', 'N/A')}</title>
                </rect>''')
        
        subtitle = "Contribution activity trend"
        svg_content = self.create_card(width, height, "📈 Recent Activity", content, subtitle)
        
        output_path = self.output_dir / output_name
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        return str(output_path)
    
    def generate_streak_card(self, metrics: Dict[str, Any],
                            output_name: str = "streak_progress.svg") -> str:
        """Gera card unificado de streak, tier e atividade - 1200px."""
        width, height = 1200, 280
        
        # Dados de streak
        current_streak = metrics.get('activity_streak', {}).get('current', 0)
        longest_streak = metrics.get('activity_streak', {}).get('longest', 0)
        
        # Dados de tier
        total_commits = metrics.get('total_commits', 0)
        total_repos = metrics.get('total_repos', 0)
        total_prs = metrics.get('total_prs', 0)
        score = total_commits * 2 + total_repos * 5 + current_streak * 3 + total_prs * 4
        tier, tier_icon, tier_color, tier_desc = self._calculate_tier(metrics)
        
        # Calcular progresso até próximo milestone de streak
        milestones = [7, 14, 30, 60, 100, 180, 365]
        next_milestone = next((m for m in milestones if m > current_streak), 365)
        streak_progress = (current_streak / next_milestone) * 100
        
        # Próximo tier
        tier_thresholds = {
            "Beginner": (150, "Intermediate"),
            "Intermediate": (350, "Advanced"),
            "Advanced": (600, "Expert"),
            "Expert": (1000, "Elite"),
            "Elite": (1000, "Elite")
        }
        next_threshold, next_tier = tier_thresholds.get(tier, (1000, "Elite"))
        tier_progress = min((score / next_threshold) * 100, 100) if tier != "Elite" else 100
        
        # Simular dados de commits dos últimos 30 dias para sparkline
        daily_commits = metrics.get('daily_stats', {}).get('commits_per_day', [])
        if not daily_commits or len(daily_commits) < 30:
            # Dados simulados se não houver histórico
            import random
            daily_commits = [{'count': random.randint(0, 5)} for _ in range(30)]
        last_30 = daily_commits[-30:] if len(daily_commits) >= 30 else daily_commits
        
        content = []
        
        # Seção 1: Streak com anel animado (esquerda)
        radius = 50
        circumference = 2 * math.pi * radius
        offset = circumference - (streak_progress / 100) * circumference
        
        content.append(f'''<g class="scale-in">
    <rect x="30" y="80" width="350" height="180" fill="{self.theme['colors']['backgroundSecondary']}" rx="12" opacity="0.5"/>
    
    <!-- Título da seção -->
    <text x="50" y="110" style="font-size: 14px; font-weight: 700; fill: {self.theme['colors']['text']}">
        🔥 Contribution Streak
    </text>
    
    <!-- Anel de progresso -->
    <circle cx="120" cy="180" r="{radius + 5}" fill="none" 
            stroke="{self.theme['colors']['border']}" stroke-width="8" opacity="0.2"/>
    <circle cx="120" cy="180" r="{radius + 5}" fill="none" 
            stroke="{self.theme['colors']['success']}" stroke-width="8" 
            stroke-dasharray="{circumference}" stroke-dashoffset="{offset}"
            stroke-linecap="round" transform="rotate(-90 120 180)" opacity="0.9">
        <animate attributeName="stroke-dashoffset" 
                 from="{circumference}" to="{offset}" 
                 dur="1.5s" fill="freeze"/>
    </circle>
    <text x="120" y="185" text-anchor="middle" style="font-size: 32px; font-weight: 700; fill: {self.theme['colors']['success']}">{current_streak}</text>
    <text x="120" y="205" text-anchor="middle" class="label">days</text>
    
    <!-- Stats -->
    <text x="220" y="150" class="label">🏆 Longest</text>
    <text x="220" y="175" style="font-size: 24px; font-weight: 700; fill: {self.theme['colors']['purple']}">{longest_streak}</text>
    
    <text x="220" y="205" class="label">🎯 Next</text>
    <text x="220" y="230" style="font-size: 16px; font-weight: 700; fill: {self.theme['colors']['warning']}">{next_milestone} days</text>
</g>''')
        
        # Seção 2: Tier Badge (centro)
        content.append(f'''<g class="scale-in" style="animation-delay: 0.2s">
    <rect x="400" y="80" width="350" height="180" fill="{self.theme['colors']['backgroundSecondary']}" rx="12" opacity="0.5"/>
    
    <!-- Título da seção -->
    <text x="420" y="110" style="font-size: 14px; font-weight: 700; fill: {self.theme['colors']['text']}">
        ⭐ Developer Tier
    </text>
    
    <!-- Badge grande do tier -->
    <rect x="440" y="130" width="140" height="110" rx="16" fill="{tier_color}" opacity="0.15"/>
    <rect x="440" y="130" width="140" height="110" rx="16" fill="none" 
          stroke="{tier_color}" stroke-width="3" opacity="0.5"/>
    <text x="510" y="175" text-anchor="middle" style="font-size: 38px" class="glow">{tier_icon}</text>
    <text x="510" y="210" text-anchor="middle" style="font-size: 18px; font-weight: 700; fill: {tier_color}">{tier}</text>
    <text x="510" y="228" text-anchor="middle" class="label" style="font-size: 9px">{tier_desc}</text>
    
    <!-- Score e progresso -->
    <text x="605" y="145" class="label">Score</text>
    <text x="605" y="170" style="font-size: 28px; font-weight: 700; fill: {self.theme['colors']['accent']}">{score}</text>
</g>''')
        
        if tier != "Elite":
            bar_width = (tier_progress / 100) * 120
            content.append(f'''<g class="slide-up" style="animation-delay: 0.3s">
    <text x="605" y="195" class="label">→ {next_tier}</text>
    <rect x="605" y="202" width="120" height="6" rx="3" fill="{self.theme['colors']['border']}" opacity="0.3"/>
    <rect x="605" y="202" width="{bar_width}" height="6" rx="3" fill="{tier_color}">
        <animate attributeName="width" from="0" to="{bar_width}" dur="1s" begin="0.3s" fill="freeze"/>
    </rect>
    <text x="605" y="220" class="label" style="font-size: 9px">{tier_progress:.0f}% complete</text>
</g>''')
        
        # Seção 3: Sparkline de atividade (direita)
        spark_x = 790
        spark_y = 80
        spark_width = 380
        spark_height = 180
        
        content.append(f'''<g class="fade-in" style="animation-delay: 0.4s">
    <rect x="{spark_x}" y="{spark_y}" width="{spark_width}" height="{spark_height}" 
          fill="{self.theme['colors']['backgroundSecondary']}" rx="12" opacity="0.5"/>
    
    <!-- Título da seção -->
    <text x="{spark_x + 20}" y="{spark_y + 30}" style="font-size: 14px; font-weight: 700; fill: {self.theme['colors']['text']}">
        📊 Last 30 Days Activity
    </text>
</g>''')
        
        # Desenhar sparkline
        max_commits = max([d.get('count', 0) for d in last_30]) or 1
        bar_width = (spark_width - 60) / 30
        
        for i, day in enumerate(last_30):
            commits = day.get('count', 0)
            bar_height = (commits / max_commits) * 100 if max_commits > 0 else 0
            bar_x = spark_x + 30 + (i * bar_width)
            bar_y = spark_y + spark_height - 60 - bar_height
            
            # Cor baseada na intensidade
            if commits == 0:
                bar_color = self.theme['colors']['border']
                opacity = 0.2
            elif commits <= max_commits * 0.3:
                bar_color = self.theme['colors']['success']
                opacity = 0.4
            elif commits <= max_commits * 0.7:
                bar_color = self.theme['colors']['success']
                opacity = 0.7
            else:
                bar_color = self.theme['colors']['success']
                opacity = 1.0
            
            content.append(f'''<rect x="{bar_x}" y="{bar_y}" width="{bar_width - 2}" height="{bar_height}" 
          fill="{bar_color}" rx="1" opacity="{opacity}">
    <animate attributeName="height" from="0" to="{bar_height}" dur="0.8s" begin="{0.4 + i * 0.01}s" fill="freeze"/>
    <animate attributeName="y" from="{spark_y + spark_height - 60}" to="{bar_y}" dur="0.8s" begin="{0.4 + i * 0.01}s" fill="freeze"/>
</rect>''')
        
        # Estatísticas do sparkline
        total_last_30 = sum(d.get('count', 0) for d in last_30)
        avg_per_day = total_last_30 / 30
        
        content.append(f'''<g class="slide-up" style="animation-delay: 0.8s">
    <text x="{spark_x + 30}" y="{spark_y + spark_height - 25}" class="label">
        Total: {total_last_30} commits • Avg: {avg_per_day:.1f}/day • Peak: {max_commits}
    </text>
</g>''')
        
        subtitle = f"Keep pushing! Your consistency is your superpower �"
        svg_content = self.create_card(width, height, "", content, subtitle)
        
        output_path = self.output_dir / output_name
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        return str(output_path)
    
    def generate_tier_card(self, metrics: Dict[str, Any],
                          output_name: str = "tier_ranking.svg") -> str:
        """Gera card de tier com contexto e progressão."""
        width, height = 450, 240
        
        total_commits = metrics.get('total_commits', 0)
        total_repos = metrics.get('total_repos', 0)
        current_streak = metrics.get('activity_streak', {}).get('current', 0)
        total_prs = metrics.get('total_prs', 0)
        
        # Calcular score e tier
        score = total_commits * 2 + total_repos * 5 + current_streak * 3 + total_prs * 4
        tier, icon, color, description = self._calculate_tier(metrics)
        
        # Próximo tier
        tier_thresholds = {
            "Beginner": (150, "Intermediate"),
            "Intermediate": (350, "Advanced"),
            "Advanced": (600, "Expert"),
            "Expert": (1000, "Elite"),
            "Elite": (1000, "Elite")  # Max tier
        }
        
        next_threshold, next_tier = tier_thresholds.get(tier, (1000, "Elite"))
        progress_to_next = min((score / next_threshold) * 100, 100) if tier != "Elite" else 100
        points_needed = max(0, next_threshold - score)
        
        content = []
        
        # Badge do tier com glow
        content.append(f'''<g class="scale-in">
        <rect x="24" y="85" width="190" height="110" rx="16" fill="{color}" opacity="0.12"/>
        <rect x="24" y="85" width="190" height="110" rx="16" fill="none" 
              stroke="{color}" stroke-width="2" opacity="0.3"/>
        <text x="119" y="125" text-anchor="middle" style="font-size: 42px" class="glow">{icon}</text>
        <text x="119" y="155" text-anchor="middle" class="value" style="font-size: 20px" fill="{color}">{tier}</text>
        <text x="119" y="175" text-anchor="middle" class="label-small">{description}</text>
    </g>''')
        
        # Métricas e progresso
        content.append(f'''<g class="slide-up" style="animation-delay: 0.2s">
        <text class="label" x="240" y="105">Developer Score</text>
        <text class="value" x="240" y="140" fill="{self.theme['colors']['accent']}">{score}</text>
    </g>''')
        
        if tier != "Elite":
            bar_width = (progress_to_next / 100) * 170
            content.append(f'''<g class="slide-up" style="animation-delay: 0.3s">
            <text class="label" x="240" y="165">Progress to {next_tier}</text>
            <rect x="240" y="175" width="170" height="6" rx="3" fill="{self.theme['colors']['border']}" opacity="0.3"/>
            <rect x="240" y="175" width="{bar_width}" height="6" rx="3" fill="{color}">
                <animate attributeName="width" from="0" to="{bar_width}" dur="1s" begin="0.3s" fill="freeze"/>
            </rect>
            <text class="label-small" x="240" y="195">{points_needed} points needed</text>
        </g>''')
        else:
            content.append(f'''<g class="slide-up" style="animation-delay: 0.3s">
            <text class="label" x="240" y="170">🎉 Maximum Tier!</text>
            <text class="label-small" x="240" y="190">You're among the elite</text>
        </g>''')
        
        subtitle = "Based on commits, repos, PRs, and streak"
        svg_content = self.create_card(width, height, "⭐ Developer Tier", content, subtitle)
        
        output_path = self.output_dir / output_name
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        return str(output_path)
    
    def generate_performance_comparison(self, metrics: Dict[str, Any], history: Dict[str, Any],
                                       output_name: str = "performance_comparison.svg") -> str:
        """Gera gráfico de linhas comparando mês atual vs anterior com dados diários reais."""
        width, height = 1200, 450
        
        # Carregar dados diários do JSON
        daily_activity_path = self.base_path / "data" / "daily_activity.json"
        try:
            with open(daily_activity_path, 'r', encoding='utf-8') as f:
                daily_data = json.load(f)
        except FileNotFoundError:
            # Fallback para dados simulados se o arquivo não existir
            daily_data = {"daily_stats": {}}
        
        daily_stats = daily_data.get('daily_stats', {})
        
        # Obter mês atual e anterior
        now = datetime.now()
        current_month_key = now.strftime('%Y-%m')
        prev_month_date = now.replace(day=1) - timedelta(days=1)
        prev_month_key = prev_month_date.strftime('%Y-%m')
        
        # Extrair dados diários
        prev_month_data = daily_stats.get(prev_month_key, [])
        curr_month_data = daily_stats.get(current_month_key, [])
        
        # Processar dados diários para o gráfico
        def process_daily_commits(month_data):
            """Extrai commits cumulativos por dia."""
            cumulative = []
            total = 0
            for day in month_data:
                total += day.get('commits', 0)
                cumulative.append(total)
            return cumulative if cumulative else [0]
        
        prev_daily = process_daily_commits(prev_month_data)
        curr_daily = process_daily_commits(curr_month_data)
        
        # Garantir que temos pelo menos 31 dias (preencher com último valor)
        while len(prev_daily) < 31:
            prev_daily.append(prev_daily[-1] if prev_daily else 0)
        while len(curr_daily) < 31:
            curr_daily.append(curr_daily[-1] if curr_daily else 0)
        
        # Calcular totais e estatísticas
        prev_commits = prev_daily[-1] if prev_daily else 0
        curr_commits = curr_daily[-1] if curr_daily else 0
        
        prev_prs = sum(day.get('prs', 0) for day in prev_month_data)
        curr_prs = sum(day.get('prs', 0) for day in curr_month_data)
        
        # Para repos, usar dados do history se disponível
        snapshots = history.get('monthly_snapshots', [])
        prev_repos = snapshots[-2].get('total_repos', 0) if len(snapshots) >= 2 else 0
        curr_repos = snapshots[-1].get('total_repos', 0) if len(snapshots) >= 1 else metrics.get('total_repos', 0)
        
        # Configuração do gráfico - ajustado para 1200px
        chart_x = 80
        chart_y = 140
        chart_width = 1040
        chart_height = 220
        
        # Encontrar valor máximo para escala
        max_value = max(max(prev_daily + curr_daily), 10)
        
        # Função para converter valor para coordenada Y
        def value_to_y(value):
            return chart_y + chart_height - (value / max_value * chart_height)
        
        # Função para converter índice do dia para coordenada X
        def day_to_x(day):
            return chart_x + (day / 30 * chart_width)
        
        content = []
        
        # Grid de fundo
        content.append(f'''<g class="fade-in" opacity="0.15">''')
        for i in range(6):
            y = chart_y + (i * chart_height / 5)
            content.append(f'''    <line x1="{chart_x}" y1="{y}" x2="{chart_x + chart_width}" y2="{y}" 
                  stroke="{self.theme['colors']['border']}" stroke-width="1" stroke-dasharray="4,4"/>''')
        content.append(f'''</g>''')
        
        # Labels do eixo Y
        content.append(f'''<g class="fade-in" style="animation-delay: 0.2s">''')
        for i in range(6):
            value = int(max_value - (i * max_value / 5))
            y = chart_y + (i * chart_height / 5)
            content.append(f'''    <text x="{chart_x - 15}" y="{y + 4}" text-anchor="end" 
                  style="font-size: 11px; fill: {self.theme['colors']['textSecondary']}">{value}</text>''')
        content.append(f'''</g>''')
        
        # Labels do eixo X (dias)
        content.append(f'''<g class="fade-in" style="animation-delay: 0.3s">''')
        for i in [0, 7, 14, 21, 30]:
            x = day_to_x(i)
            content.append(f'''    <text x="{x}" y="{chart_y + chart_height + 20}" text-anchor="middle" 
                  style="font-size: 11px; fill: {self.theme['colors']['textSecondary']}">Day {i}</text>''')
        content.append(f'''</g>''')
        
        # Área sob a curva - Mês anterior (azul)
        prev_path = f"M {day_to_x(0)} {chart_y + chart_height}"
        for i, val in enumerate(prev_daily):
            prev_path += f" L {day_to_x(i)} {value_to_y(val)}"
        prev_path += f" L {day_to_x(30)} {chart_y + chart_height} Z"
        
        content.append(f'''<g class="fade-in" style="animation-delay: 0.4s">
    <path d="{prev_path}" fill="url(#prev-gradient)" opacity="0.3">
        <animate attributeName="opacity" from="0" to="0.3" dur="1s" begin="0.4s" fill="freeze"/>
    </path>
</g>''')
        
        # Área sob a curva - Mês atual (verde)
        curr_path = f"M {day_to_x(0)} {chart_y + chart_height}"
        for i, val in enumerate(curr_daily):
            curr_path += f" L {day_to_x(i)} {value_to_y(val)}"
        curr_path += f" L {day_to_x(30)} {chart_y + chart_height} Z"
        
        content.append(f'''<g class="fade-in" style="animation-delay: 0.5s">
    <path d="{curr_path}" fill="url(#curr-gradient)" opacity="0.3">
        <animate attributeName="opacity" from="0" to="0.3" dur="1s" begin="0.5s" fill="freeze"/>
    </path>
</g>''')
        
        # Linha - Mês anterior
        prev_line = f"M {day_to_x(0)} {value_to_y(prev_daily[0])}"
        for i, val in enumerate(prev_daily[1:], 1):
            prev_line += f" L {day_to_x(i)} {value_to_y(val)}"
        
        content.append(f'''<g class="fade-in" style="animation-delay: 0.6s">
    <path d="{prev_line}" fill="none" stroke="{self.theme['colors']['accent']}" 
          stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
        <animate attributeName="stroke-dasharray" from="0 2000" to="2000 0" dur="2s" begin="0.6s" fill="freeze"/>
    </path>
</g>''')
        
        # Linha - Mês atual
        curr_line = f"M {day_to_x(0)} {value_to_y(curr_daily[0])}"
        for i, val in enumerate(curr_daily[1:], 1):
            curr_line += f" L {day_to_x(i)} {value_to_y(val)}"
        
        content.append(f'''<g class="fade-in" style="animation-delay: 0.7s">
    <path d="{curr_line}" fill="none" stroke="{self.theme['colors']['success']}" 
          stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
        <animate attributeName="stroke-dasharray" from="0 2000" to="2000 0" dur="2s" begin="0.7s" fill="freeze"/>
    </path>
</g>''')
        
        # Pontos finais destacados
        content.append(f'''<g class="scale-in" style="animation-delay: 1.2s">
    <circle cx="{day_to_x(30)}" cy="{value_to_y(prev_daily[-1])}" r="5" 
            fill="{self.theme['colors']['accent']}" stroke="{self.theme['colors']['background']}" stroke-width="2"/>
    <circle cx="{day_to_x(30)}" cy="{value_to_y(curr_daily[-1])}" r="5" 
            fill="{self.theme['colors']['success']}" stroke="{self.theme['colors']['background']}" stroke-width="2"/>
</g>''')
        
        # Legenda e estatísticas - ajustado para não sobrepor o subtítulo
        legend_y = 90
        
        # Mês anterior
        prev_month_name = prev_month_date.strftime('%B')
        prev_year = prev_month_date.strftime('%Y')
        content.append(f'''<g class="slide-up" style="animation-delay: 0.3s">
    <rect x="80" y="{legend_y - 8}" width="4" height="20" fill="{self.theme['colors']['accent']}" rx="2"/>
    <text x="95" y="{legend_y}" style="font-size: 13px; font-weight: 600; fill: {self.theme['colors']['text']}">
        {prev_month_name} {prev_year}
    </text>
    <text x="95" y="{legend_y + 15}" style="font-size: 11px; fill: {self.theme['colors']['textSecondary']}">
        {prev_commits} commits • {prev_prs} PRs • {prev_repos} repos
    </text>
</g>''')
        
        # Mês atual
        curr_month_name = now.strftime('%B')
        curr_year = now.strftime('%Y')
        content.append(f'''<g class="slide-up" style="animation-delay: 0.4s">
    <rect x="380" y="{legend_y - 8}" width="4" height="20" fill="{self.theme['colors']['success']}" rx="2"/>
    <text x="395" y="{legend_y}" style="font-size: 13px; font-weight: 600; fill: {self.theme['colors']['text']}">
        {curr_month_name} {curr_year}
    </text>
    <text x="395" y="{legend_y + 15}" style="font-size: 11px; fill: {self.theme['colors']['textSecondary']}">
        {curr_commits} commits • {curr_prs} PRs • {curr_repos} repos
    </text>
</g>''')
        
        # Comparação percentual
        change = ((curr_commits - prev_commits) / prev_commits * 100) if prev_commits > 0 else 100
        arrow = "↑" if change > 0 else "↓" if change < 0 else "●"
        trend_color = self.theme['colors']['success'] if change > 0 else self.theme['colors']['error'] if change < 0 else self.theme['colors']['textSecondary']
        
        content.append(f'''<g class="scale-in" style="animation-delay: 0.5s">
    <rect x="750" y="{legend_y - 15}" width="280" height="42" fill="{trend_color}" rx="8" opacity="0.15"/>
    <text x="770" y="{legend_y}" style="font-size: 13px; font-weight: 600; fill: {self.theme['colors']['text']}">
        Monthly Change
    </text>
    <text x="770" y="{legend_y + 17}" style="font-size: 20px; font-weight: 700; fill: {trend_color}">
        {arrow} {abs(change):.1f}%
    </text>
</g>''')
        
        # Gradientes
        content.append(f'''<defs>
    <linearGradient id="prev-gradient" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" style="stop-color:{self.theme['colors']['accent']};stop-opacity:0.4" />
        <stop offset="100%" style="stop-color:{self.theme['colors']['accent']};stop-opacity:0.05" />
    </linearGradient>
    <linearGradient id="curr-gradient" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" style="stop-color:{self.theme['colors']['success']};stop-opacity:0.4" />
        <stop offset="100%" style="stop-color:{self.theme['colors']['success']};stop-opacity:0.05" />
    </linearGradient>
</defs>''')
        
        subtitle = f"Daily commit activity comparison • Updated {datetime.now().strftime('%B %d, %Y')}"
        svg_content = self.create_card(width, height, "📈 Performance Trend", content, subtitle)
        
        output_path = self.output_dir / output_name
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        return str(output_path)
    
    def generate_featured_projects(self, output_name: str = "featured_projects.svg") -> str:
        """Gera lista de projetos destacados - 1200px."""
        width, height = 1200, 550
        
        # Carregar dados de projetos
        projects_path = self.base_path / "data" / "projects.json"
        try:
            with open(projects_path, 'r', encoding='utf-8') as f:
                projects_data = json.load(f)
        except FileNotFoundError:
            projects_data = {"featured_projects": []}
        
        projects = projects_data.get('featured_projects', [])[:6]  # Top 6 projetos
        
        # Cores por linguagem
        lang_colors = {
            'Python': '#3572A5',
            'TypeScript': '#3178c6',
            'JavaScript': '#f1e05a',
            'Go': '#00ADD8',
            'Java': '#b07219',
            'C++': '#f34b7d',
            'Ruby': '#701516',
            'PHP': '#4F5D95',
            'Shell': '#89e051',
            'Rust': '#dea584',
        }
        
        # Status icons e cores
        status_info = {
            'active': ('🟢', self.theme['colors']['success'], 'Active'),
            'maintenance': ('🟡', self.theme['colors']['warning'], 'Maintenance'),
            'archived': ('🔴', self.theme['colors']['error'], 'Archived'),
        }
        
        content = []
        
        # Cabeçalho
        content.append(f'''<g class="fade-in">
    <text class="title" x="40" y="45">🚀 Featured Projects</text>
    <text class="label" x="40" y="70">My most significant repositories and contributions</text>
</g>''')
        
        # Linha divisória
        content.append(f'''<line x1="40" y1="90" x2="1160" y2="90" stroke="{self.theme['colors']['border']}" stroke-width="1" opacity="0.3"/>''')
        
        # Grid de projetos (2 colunas)
        y_pos = 120
        col = 0
        delay = 0.2
        
        for i, project in enumerate(projects):
            x_pos = 40 if col == 0 else 620
            
            lang = project.get('language', 'Unknown')
            lang_color = lang_colors.get(lang, self.theme['colors']['accent'])
            status = project.get('status', 'active')
            status_icon, status_color, status_text = status_info.get(status, ('⚪', self.theme['colors']['textSecondary'], 'Unknown'))
            
            stars = project.get('stars', 0)
            forks = project.get('forks', 0)
            commits = project.get('commits', 0)
            
            # Calcular tempo desde última atualização
            try:
                last_update = datetime.strptime(project.get('last_updated', '2026-01-01'), '%Y-%m-%d')
                days_ago = (datetime.now() - last_update).days
                if days_ago == 0:
                    update_text = "Today"
                elif days_ago == 1:
                    update_text = "Yesterday"
                elif days_ago < 30:
                    update_text = f"{days_ago}d ago"
                elif days_ago < 365:
                    update_text = f"{days_ago // 30}mo ago"
                else:
                    update_text = f"{days_ago // 365}y ago"
            except:
                update_text = "Unknown"
            
            # URL do projeto
            project_url = project.get('url', '#')
            
            content.append(f'''<a href="{project_url}" target="_blank" class="slide-up" style="animation-delay: {delay}s">
    <g class="project-card" style="cursor: pointer;">
        <!-- Card background com hover effect -->
        <rect x="{x_pos}" y="{y_pos}" width="540" height="120" 
              fill="{self.theme['colors']['backgroundSecondary']}" rx="12" 
              stroke="{lang_color}" stroke-width="2" stroke-opacity="0.3" fill-opacity="0.5"
              style="transition: all 0.3s ease;">
            <animate attributeName="fill-opacity" 
                     begin="mouseover" end="mouseout" 
                     from="0.5" to="0.8" dur="0.3s" fill="freeze"/>
            <animate attributeName="stroke-opacity" 
                     begin="mouseover" end="mouseout" 
                     from="0.3" to="0.6" dur="0.3s" fill="freeze"/>
        </rect>
        
        <!-- Nome do projeto -->
        <text x="{x_pos + 20}" y="{y_pos + 30}" style="font-size: 16px; font-weight: 700; fill: {self.theme['colors']['text']}">
            {project.get('name', 'Unnamed Project')}
        </text>
        
        <!-- Ícone de link externo -->
        <text x="{x_pos + 485}" y="{y_pos + 30}" style="font-size: 12px; opacity: 0.6">🔗</text>
        
        <!-- Status badge -->
        <text x="{x_pos + 510}" y="{y_pos + 30}" style="font-size: 14px">{status_icon}</text>
        
        <!-- Descrição -->
        <text x="{x_pos + 20}" y="{y_pos + 52}" class="label" style="font-size: 11px">
            {(project.get('description') or 'No description')[:70]}{'...' if len(project.get('description') or '') > 70 else ''}
        </text>
        
        <!-- Language badge -->
        <rect x="{x_pos + 20}" y="{y_pos + 65}" width="80" height="20" fill="{lang_color}" rx="10" opacity="0.2"/>
        <circle cx="{x_pos + 32}" cy="{y_pos + 75}" r="4" fill="{lang_color}"/>
        <text x="{x_pos + 40}" y="{y_pos + 79}" style="font-size: 10px; font-weight: 600; fill: {lang_color}">
            {lang}
        </text>
        
        <!-- Estatísticas -->
        <text x="{x_pos + 120}" y="{y_pos + 79}" class="label" style="font-size: 10px">
            ⭐ {stars} • 🔀 {forks} • 📝 {commits} commits
        </text>
        
        <!-- Topics -->
        <g>''')
            
            # Topics (até 3)
            topics = project.get('topics', [])[:3]
            topic_x = x_pos + 20
            for topic in topics:
                content.append(f'''
        <rect x="{topic_x}" y="{y_pos + 90}" width="{len(topic) * 6 + 12}" height="18" 
              fill="{self.theme['colors']['accent']}" rx="9" opacity="0.15"/>
        <text x="{topic_x + 6}" y="{y_pos + 102}" style="font-size: 9px; font-weight: 600; fill: {self.theme['colors']['accent']}">
            #{topic}
        </text>''')
                topic_x += len(topic) * 6 + 18
            
            # Last updated
            content.append(f'''
    </g>
    
    <!-- Last updated -->
    <text x="{x_pos + 450}" y="{y_pos + 102}" text-anchor="end" class="label" style="font-size: 9px">
        Updated {update_text}
    </text>
    </g>
</a>''')
            
            col = 1 - col
            if col == 0:
                y_pos += 135
            delay += 0.1
        
        # Rodapé com estatísticas
        total_stars = sum(p.get('stars', 0) for p in projects)
        total_commits = sum(p.get('commits', 0) for p in projects)
        total_contributors = sum(p.get('contributors', 0) for p in projects)
        
        content.append(f'''<g class="fade-in" style="animation-delay: 1s">
    <line x1="40" y1="510" x2="1160" y2="510" stroke="{self.theme['colors']['border']}" stroke-width="1" opacity="0.3"/>
    <text x="60" y="535" style="font-size: 12px; font-weight: 600; fill: {self.theme['colors']['textSecondary']}">
        📊 Collective Impact: ⭐ {total_stars} stars • 📝 {total_commits} commits • 👥 {total_contributors} contributors
    </text>
</g>''')
        
        subtitle = f"Showcasing dedication and innovation • Updated {datetime.now().strftime('%B %d, %Y')}"
        svg_content = self.create_card(width, height, "", content, subtitle)
        
        output_path = self.output_dir / output_name
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        return str(output_path)

