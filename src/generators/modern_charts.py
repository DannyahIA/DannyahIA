"""
Modern Chart Generators - Gráficos profissionais e interativos

Este módulo cria gráficos modernos:
- Stats Hero com glassmorphism
- Language Pie Chart interativo
- Activity Heatmap estilo GitHub
- Streak Progress com rings animados
- Tier Ranking com badges
- Repository Cards clicáveis
"""

import json
import math
from pathlib import Path
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta
from .advanced_svg_renderer import AdvancedSVGRenderer


class ModernChartGenerator:
    """
    Gera gráficos modernos e profissionais para o dashboard.
    """
    
    def __init__(self, base_path: str = "."):
        """
        Inicializa o gerador.
        
        Args:
            base_path: Caminho base do projeto
        """
        self.base_path = Path(base_path)
        self.renderer = AdvancedSVGRenderer(base_path)
        self.theme = self.renderer.theme
        self.output_dir = self.base_path / "assets"
        self.output_dir.mkdir(exist_ok=True)
        
    def generate_stats_hero(self, metrics: Dict[str, Any], 
                           github_username: str = "",
                           output_name: str = "stats_hero.svg") -> str:
        """
        Gera card hero principal com estatísticas em destaque.
        Design com glassmorphism e gradientes.
        """
        width, height = 900, 280
        padding = 32
        
        children = []
        
        # Título com gradiente
        children.append(f'''<g class="animated">
        <text class="title" x="{padding}" y="{padding + 32}" 
              fill="url(#gradient-accent)" font-size="36" font-weight="800">
            ⚡ GitHub Analytics
        </text>
        <text class="text-secondary" x="{padding}" y="{padding + 58}" 
              font-size="14">
            Powered by advanced metrics • Updated daily via GitHub Actions
        </text>
    </g>''')
        
        # Grid de estatísticas 4x1
        stats = [
            {
                "label": "Total Commits",
                "value": metrics.get('total_commits', 0),
                "icon": "📝",
                "gradient": "emerald",
                "link": f"https://github.com/{github_username}?tab=repositories"
            },
            {
                "label": "Pull Requests",
                "value": metrics.get('total_prs', 0),
                "icon": "🔀",
                "gradient": "purple",
                "link": f"https://github.com/pulls?q=is%3Apr+author%3A{github_username}"
            },
            {
                "label": "Repositories",
                "value": metrics.get('total_repos', 0),
                "icon": "📦",
                "gradient": "accent",
                "link": f"https://github.com/{github_username}?tab=repositories"
            },
            {
                "label": "Current Streak",
                "value": f"{metrics.get('activity_streak', {}).get('current', 0)} days",
                "icon": "🔥",
                "gradient": "fire",
                "link": f"https://github.com/{github_username}"
            }
        ]
        
        grid_y = padding + 100
        col_width = (width - padding * 5) // 4
        stat_height = 120
        
        for i, stat in enumerate(stats):
            x = padding + i * (col_width + padding)
            delay = i * 0.15
            
            link_start = f'<a href="{stat["link"]}" target="_blank">' if stat.get("link") else ""
            link_end = '</a>' if stat.get("link") else ""
            
            children.append(f'''{link_start}
    <g class="interactive scale-in" style="animation-delay: {delay}s">
        <rect x="{x}" y="{grid_y}" width="{col_width}" height="{stat_height}" 
              rx="{self.theme['radiusLarge']}" 
              fill="url(#gradient-{stat['gradient']})" opacity="0.12" 
              stroke="url(#gradient-{stat['gradient']})" stroke-width="1" stroke-opacity="0.3" />
        
        <text class="text-muted" x="{x + col_width/2}" y="{grid_y + 28}" 
              text-anchor="middle" font-size="11" letter-spacing="0.5px">
            {stat['label'].upper()}
        </text>
        
        <text x="{x + col_width/2}" y="{grid_y + 72}" 
              text-anchor="middle" font-size="36" font-weight="800" 
              fill="url(#gradient-{stat['gradient']})">
            {stat['icon']}
        </text>
        
        <text class="heading" x="{x + col_width/2}" y="{grid_y + 100}" 
              text-anchor="middle" font-size="24" font-weight="700">
            {stat['value']}
        </text>
    </g>
{link_end}''')
        
        svg_content = self.renderer.create_card_container(width, height, children, glass=True)
        output_path = self.output_dir / output_name
        with open(output_path, 'w') as f:
            f.write(svg_content)
        
        return str(output_path)
    
    def generate_language_pie(self, metrics: Dict[str, Any],
                              output_name: str = "language_pie.svg") -> str:
        """
        Gera gráfico de pizza (donut) interativo de linguagens.
        """
        width, height = 500, 500
        padding = 32
        
        languages = metrics.get('top_languages', {})
        total = sum(languages.values())
        
        # Top 8 linguagens
        lang_data = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:8]
        
        children = []
        
        # Título
        children.append(f'''<g class="animated">
        <text class="title" x="{width/2}" y="{padding + 24}" 
              text-anchor="middle">💻 Top Languages</text>
    </g>''')
        
        # Configuração do donut
        center_x = width / 2
        center_y = height / 2 + 20
        outer_radius = 140
        inner_radius = 95
        
        # Desenha slices do donut
        current_angle = -90  # Começa no topo
        
        for i, (lang, count) in enumerate(lang_data):
            percentage = (count / total) * 100
            slice_angle = (percentage / 100) * 360
            
            # Cor da linguagem
            lang_color = self.theme.get('languageColors', {}).get(
                lang, 
                self.theme['colors']['accent']
            )
            
            # Calcula path do slice
            path = self._create_donut_slice(
                center_x, center_y, 
                inner_radius, outer_radius,
                current_angle, slice_angle
            )
            
            # Label position (no meio do slice)
            label_angle = current_angle + slice_angle / 2
            label_radius = outer_radius + 30
            label_x = center_x + label_radius * math.cos(math.radians(label_angle))
            label_y = center_y + label_radius * math.sin(math.radians(label_angle))
            
            delay = i * 0.1
            
            children.append(f'''<g class="bar animated" style="animation-delay: {delay}s">
        <path d="{path}" fill="{lang_color}" opacity="0.9" 
              stroke="{self.theme['colors']['background']}" stroke-width="2" />
        <line x1="{center_x + (outer_radius + 5) * math.cos(math.radians(label_angle))}" 
              y1="{center_y + (outer_radius + 5) * math.sin(math.radians(label_angle))}" 
              x2="{label_x - 20 if label_x < center_x else label_x + 20}" 
              y2="{label_y}" 
              stroke="{lang_color}" stroke-width="1.5" opacity="0.6" />
        <text class="text" x="{label_x}" y="{label_y - 5}" 
              text-anchor="{'end' if label_x < center_x else 'start'}" 
              font-weight="600" font-size="13">
            {lang}
        </text>
        <text class="text-secondary" x="{label_x}" y="{label_y + 10}" 
              text-anchor="{'end' if label_x < center_x else 'start'}" 
              font-size="11">
            {percentage:.1f}%
        </text>
    </g>''')
            
            current_angle += slice_angle
        
        # Círculo central com total
        children.append(f'''<g class="scale-in" style="animation-delay: 0.5s">
        <circle cx="{center_x}" cy="{center_y}" r="{inner_radius}" 
                fill="{self.theme['colors']['card']}" 
                stroke="url(#gradient-accent)" stroke-width="3" />
        <text class="heading" x="{center_x}" y="{center_y - 8}" 
              text-anchor="middle" font-size="28" font-weight="700" 
              fill="url(#gradient-accent)">
            {len(lang_data)}
        </text>
        <text class="text-secondary" x="{center_x}" y="{center_y + 12}" 
              text-anchor="middle" font-size="12">
            Languages
        </text>
    </g>''')
        
        svg_content = self.renderer.create_card_container(width, height, children)
        output_path = self.output_dir / output_name
        with open(output_path, 'w') as f:
            f.write(svg_content)
        
        return str(output_path)
    
    def _create_donut_slice(self, cx: float, cy: float, 
                           inner_r: float, outer_r: float,
                           start_angle: float, slice_angle: float) -> str:
        """Cria path SVG para um slice de donut."""
        end_angle = start_angle + slice_angle
        
        # Converte para radianos
        start_rad = math.radians(start_angle)
        end_rad = math.radians(end_angle)
        
        # Pontos externos
        outer_start_x = cx + outer_r * math.cos(start_rad)
        outer_start_y = cy + outer_r * math.sin(start_rad)
        outer_end_x = cx + outer_r * math.cos(end_rad)
        outer_end_y = cy + outer_r * math.sin(end_rad)
        
        # Pontos internos
        inner_start_x = cx + inner_r * math.cos(start_rad)
        inner_start_y = cy + inner_r * math.sin(start_rad)
        inner_end_x = cx + inner_r * math.cos(end_rad)
        inner_end_y = cy + inner_r * math.sin(end_rad)
        
        # Large arc flag
        large_arc = 1 if slice_angle > 180 else 0
        
        return f"""M {outer_start_x} {outer_start_y}
                   A {outer_r} {outer_r} 0 {large_arc} 1 {outer_end_x} {outer_end_y}
                   L {inner_end_x} {inner_end_y}
                   A {inner_r} {inner_r} 0 {large_arc} 0 {inner_start_x} {inner_start_y}
                   Z"""
    
    def generate_activity_heatmap(self, metrics: Dict[str, Any],
                                  output_name: str = "activity_heatmap.svg") -> str:
        """
        Gera heatmap de contribuições estilo GitHub.
        """
        width, height = 900, 200
        padding = 32
        
        children = []
        
        # Título
        children.append(f'''<g class="animated">
        <text class="title" x="{padding}" y="{padding + 20}">
            📊 Contribution Activity
        </text>
    </g>''')
        
        # Gera dados para últimos 12 meses (simplificado)
        daily_stats = metrics.get('daily_stats', {}).get('commits_per_day', [])
        
        # Configuração do heatmap
        cell_size = 12
        cell_gap = 3
        weeks = 52
        days = 7
        
        start_x = padding
        start_y = padding + 50
        
        # Cria células do heatmap
        max_commits = max((day.get('count', 0) for day in daily_stats), default=1)
        
        for week in range(weeks):
            for day in range(days):
                x = start_x + week * (cell_size + cell_gap)
                y = start_y + day * (cell_size + cell_gap)
                
                # Simula dados (em produção, usar dados reais)
                commits = 0
                if daily_stats and len(daily_stats) > week * 7 + day:
                    commits = daily_stats[week * 7 + day].get('count', 0)
                
                # Calcula intensidade da cor
                intensity = min(commits / max(max_commits, 1), 1)
                
                if commits == 0:
                    color = self.theme['colors']['border']
                    opacity = 0.3
                elif intensity < 0.25:
                    color = self.theme['colors']['success']
                    opacity = 0.3
                elif intensity < 0.5:
                    color = self.theme['colors']['success']
                    opacity = 0.5
                elif intensity < 0.75:
                    color = self.theme['colors']['success']
                    opacity = 0.7
                else:
                    color = self.theme['colors']['success']
                    opacity = 1.0
                
                delay = (week * days + day) * 0.001
                
                children.append(f'''<rect class="bar animated" 
                    x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" 
                    rx="2" fill="{color}" opacity="{opacity}"
                    style="animation-delay: {delay}s">
                    <title>{commits} contributions</title>
                </rect>''')
        
        # Legenda
        legend_x = start_x
        legend_y = start_y + days * (cell_size + cell_gap) + 20
        
        children.append(f'''<g class="animated" style="animation-delay: 0.5s">
        <text class="text-secondary" x="{legend_x}" y="{legend_y}" font-size="11">Less</text>
        <rect x="{legend_x + 35}" y="{legend_y - 10}" width="{cell_size}" height="{cell_size}" 
              rx="2" fill="{self.theme['colors']['border']}" opacity="0.3" />
        <rect x="{legend_x + 52}" y="{legend_y - 10}" width="{cell_size}" height="{cell_size}" 
              rx="2" fill="{self.theme['colors']['success']}" opacity="0.3" />
        <rect x="{legend_x + 69}" y="{legend_y - 10}" width="{cell_size}" height="{cell_size}" 
              rx="2" fill="{self.theme['colors']['success']}" opacity="0.6" />
        <rect x="{legend_x + 86}" y="{legend_y - 10}" width="{cell_size}" height="{cell_size}" 
              rx="2" fill="{self.theme['colors']['success']}" opacity="0.9" />
        <text class="text-secondary" x="{legend_x + 105}" y="{legend_y}" font-size="11">More</text>
    </g>''')
        
        svg_content = self.renderer.create_card_container(width, height, children)
        output_path = self.output_dir / output_name
        with open(output_path, 'w') as f:
            f.write(svg_content)
        
        return str(output_path)
    
    def generate_streak_progress(self, metrics: Dict[str, Any],
                                 output_name: str = "streak_progress.svg") -> str:
        """
        Gera card de streak com progress rings.
        """
        width, height = 400, 280
        padding = 32
        
        children = []
        
        # Título
        children.append(f'''<g class="animated">
        <text class="title" x="{padding}" y="{padding + 20}">
            🔥 Contribution Streak
        </text>
    </g>''')
        
        # Dados de streak
        current_streak = metrics.get('activity_streak', {}).get('current', 0)
        longest_streak = metrics.get('activity_streak', {}).get('longest', 0)
        
        # Dois progress rings lado a lado
        ring_y = padding + 80
        ring_radius = 60
        
        # Ring 1: Current Streak
        ring1_x = width / 3
        current_percentage = min((current_streak / max(longest_streak, 1)) * 100, 100)
        
        children.append(
            self.renderer.create_progress_ring(
                int(ring1_x), ring_y, ring_radius, 
                current_percentage, "Current"
            ).replace('class="scale-in"', 'class="scale-in" style="animation-delay: 0.2s"')
        )
        
        children.append(f'''<text class="heading" x="{ring1_x}" y="{ring_y + ring_radius + 35}" 
              text-anchor="middle" font-size="32" font-weight="700" 
              fill="url(#gradient-fire)">
            {current_streak}
        </text>
        <text class="text-secondary" x="{ring1_x}" y="{ring_y + ring_radius + 55}" 
              text-anchor="middle" font-size="12">
            days
        </text>''')
        
        # Ring 2: Longest Streak
        ring2_x = width * 2 / 3
        
        children.append(
            self.renderer.create_progress_ring(
                int(ring2_x), ring_y, ring_radius, 
                100, "Longest"
            ).replace('class="scale-in"', 'class="scale-in" style="animation-delay: 0.4s"')
        )
        
        children.append(f'''<text class="heading" x="{ring2_x}" y="{ring_y + ring_radius + 35}" 
              text-anchor="middle" font-size="32" font-weight="700" 
              fill="url(#gradient-emerald)">
            {longest_streak}
        </text>
        <text class="text-secondary" x="{ring2_x}" y="{ring_y + ring_radius + 55}" 
              text-anchor="middle" font-size="12">
            days
        </text>''')
        
        svg_content = self.renderer.create_card_container(width, height, children)
        output_path = self.output_dir / output_name
        with open(output_path, 'w') as f:
            f.write(svg_content)
        
        return str(output_path)
    
    def generate_languages_compact(self, metrics: Dict[str, Any],
                                   output_name: str = "languages_compact.svg") -> str:
        """
        Gera gráfico compacto de linguagens com barras horizontais.
        """
        width, height = 450, 320
        padding = 28
        
        languages = metrics.get('top_languages', {})
        total = sum(languages.values())
        
        # Top 6 linguagens
        lang_data = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:6]
        
        children = []
        
        # Título
        children.append(f'''<g class="animated">
        <text class="title" x="{padding}" y="{padding + 20}" font-size="20">
            💻 Top Languages
        </text>
    </g>''')
        
        # Barras
        bar_height = 32
        bar_spacing = 12
        start_y = padding + 60
        max_bar_width = width - padding * 2 - 80
        
        for i, (lang, count) in enumerate(lang_data):
            y = start_y + i * (bar_height + bar_spacing)
            percentage = (count / total) * 100
            bar_width = (percentage / 100) * max_bar_width
            
            # Cor da linguagem
            lang_color = self.theme.get('languageColors', {}).get(
                lang, 
                self.theme['colors']['accent']
            )
            
            delay = i * 0.1
            
            children.append(f'''<g class="bar animated" style="animation-delay: {delay}s">
        <rect x="{padding}" y="{y}" width="{max_bar_width}" height="{bar_height}" 
              rx="16" fill="{lang_color}" opacity="0.1" />
        <rect x="{padding}" y="{y}" width="{bar_width}" height="{bar_height}" 
              rx="16" fill="{lang_color}" opacity="0.9" />
        <circle cx="{padding + 14}" cy="{y + bar_height/2}" r="5" fill="{lang_color}" />
        <text class="text" x="{padding + 26}" y="{y + bar_height/2 + 5}" 
              font-size="13" font-weight="600">{lang}</text>
        <text class="text-secondary" x="{width - padding - 10}" y="{y + bar_height/2 + 5}" 
              text-anchor="end" font-size="12">{percentage:.1f}%</text>
    </g>''')
        
        svg_content = self.renderer.create_card_container(width, height, children)
        output_path = self.output_dir / output_name
        with open(output_path, 'w') as f:
            f.write(svg_content)
        
        return str(output_path)
