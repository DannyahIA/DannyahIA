"""
Compact Chart Components - Componentes compactos para layouts responsivos

Cria versões compactas e otimizadas dos gráficos principais.
"""

from .modern_charts import ModernChartGenerator
from typing import Dict, Any


class CompactChartGenerator(ModernChartGenerator):
    """
    Extensão do ModernChartGenerator para criar versões compactas.
    """
    
    def generate_activity_compact(self, metrics: Dict[str, Any],
                                  output_name: str = "activity_compact.svg") -> str:
        """
        Gera gráfico compacto de atividade recente.
        """
        width, height = 450, 220
        padding = 28
        
        children = []
        
        # Título
        children.append(f'''<g class="animated">
        <text class="title" x="{padding}" y="{padding + 20}" font-size="20">
            📈 Recent Activity
        </text>
    </g>''')
        
        # Dados de atividade
        daily_stats = metrics.get('daily_stats', {}).get('commits_per_day', [])
        total_commits = sum(day.get('count', 0) for day in daily_stats)
        avg_commits = metrics.get('daily_stats', {}).get('average_commits', 0)
        
        # Mini stats
        stats_y = padding + 60
        
        children.append(f'''<g class="animated" style="animation-delay: 0.2s">
        <text class="text-secondary" x="{padding}" y="{stats_y}" font-size="12">
            Last 30 days
        </text>
        <text class="heading" x="{padding}" y="{stats_y + 30}" font-size="36" 
              font-weight="700" fill="url(#gradient-accent)">
            {total_commits}
        </text>
        <text class="text-secondary" x="{padding}" y="{stats_y + 50}" font-size="12">
            total commits
        </text>
    </g>''')
        
        # Mini bar chart
        chart_x = padding + 180
        chart_y = stats_y
        bar_width = 8
        bar_spacing = 4
        max_height = 100
        
        # Últimos 30 dias (ou menos)
        recent_days = daily_stats[-30:] if len(daily_stats) > 30 else daily_stats
        max_count = max((day.get('count', 0) for day in recent_days), default=1)
        
        for i, day in enumerate(recent_days[-20:]):  # Últimos 20 dias para caber
            count = day.get('count', 0)
            bar_height = (count / max(max_count, 1)) * max_height if max_count > 0 else 0
            x = chart_x + i * (bar_width + bar_spacing)
            y = chart_y + max_height - bar_height
            
            delay = 0.3 + i * 0.02
            
            children.append(f'''<rect class="bar animated" 
                x="{x}" y="{y}" width="{bar_width}" height="{bar_height}" 
                rx="3" fill="url(#gradient-accent)" 
                style="animation-delay: {delay}s">
                <title>{count} commits on {day.get('date', '')}</title>
            </rect>''')
        
        svg_content = self.renderer.create_card_container(width, height, children)
        output_path = self.output_dir / output_name
        with open(output_path, 'w') as f:
            f.write(svg_content)
        
        return str(output_path)
    
    def generate_streak_compact(self, metrics: Dict[str, Any],
                               output_name: str = "streak_compact.svg") -> str:
        """
        Gera card compacto de streak.
        """
        width, height = 450, 180
        padding = 28
        
        children = []
        
        # Título
        children.append(f'''<g class="animated">
        <text class="title" x="{padding}" y="{padding + 20}" font-size="20">
            🔥 Contribution Streak
        </text>
    </g>''')
        
        # Streak info
        current_streak = metrics.get('activity_streak', {}).get('current', 0)
        longest_streak = metrics.get('activity_streak', {}).get('longest', 0)
        
        stats_y = padding + 70
        
        # Current streak (destaque)
        children.append(f'''<g class="animated" style="animation-delay: 0.2s">
        <circle cx="{padding + 40}" cy="{stats_y}" r="35" 
                fill="url(#gradient-fire)" opacity="0.2" />
        <text x="{padding + 40}" y="{stats_y + 8}" 
              text-anchor="middle" font-size="32" font-weight="800" 
              fill="url(#gradient-fire)">
            {current_streak}
        </text>
        <text class="text-secondary" x="{padding + 40}" y="{stats_y + 50}" 
              text-anchor="middle" font-size="11">
            Current Streak
        </text>
    </g>''')
        
        # Longest streak
        children.append(f'''<g class="animated" style="animation-delay: 0.3s">
        <rect x="{padding + 140}" y="{stats_y - 25}" width="120" height="50" 
              rx="10" fill="url(#gradient-emerald)" opacity="0.15" />
        <text class="text-secondary" x="{padding + 150}" y="{stats_y - 8}" 
              font-size="11">
            Longest Streak
        </text>
        <text class="heading" x="{padding + 150}" y="{stats_y + 16}" 
              font-size="24" font-weight="700" fill="url(#gradient-emerald)">
            {longest_streak} days
        </text>
    </g>''')
        
        # Progress bar
        progress_y = stats_y + 70
        progress_width = width - padding * 2
        progress_height = 8
        progress_percentage = min((current_streak / max(longest_streak, 1)) * 100, 100)
        fill_width = (progress_percentage / 100) * progress_width
        
        children.append(f'''<g class="animated" style="animation-delay: 0.4s">
        <rect x="{padding}" y="{progress_y}" width="{progress_width}" height="{progress_height}" 
              rx="4" fill="{self.theme['colors']['border']}" opacity="0.3" />
        <rect x="{padding}" y="{progress_y}" width="{fill_width}" height="{progress_height}" 
              rx="4" fill="url(#gradient-fire)" />
    </g>''')
        
        svg_content = self.renderer.create_card_container(width, height, children)
        output_path = self.output_dir / output_name
        with open(output_path, 'w') as f:
            f.write(svg_content)
        
        return str(output_path)
    
    def generate_tier_compact(self, metrics: Dict[str, Any],
                             output_name: str = "tier_compact.svg") -> str:
        """
        Gera card compacto com tier/ranking do desenvolvedor.
        """
        width, height = 450, 220
        padding = 28
        
        children = []
        
        # Título
        children.append(f'''<g class="animated">
        <text class="title" x="{padding}" y="{padding + 20}" font-size="20">
            ⭐ Developer Tier
        </text>
    </g>''')
        
        # Calcula tier baseado em métricas
        total_commits = metrics.get('total_commits', 0)
        total_repos = metrics.get('total_repos', 0)
        current_streak = metrics.get('activity_streak', {}).get('current', 0)
        
        score = total_commits * 2 + total_repos * 5 + current_streak * 3
        
        # Define tier
        if score >= 500:
            tier = "Elite"
            tier_icon = "👑"
            tier_color = "purple"
            level = 5
        elif score >= 300:
            tier = "Expert"
            tier_icon = "💎"
            tier_color = "accent"
            level = 4
        elif score >= 150:
            tier = "Advanced"
            tier_icon = "⚡"
            tier_color = "success"
            level = 3
        elif score >= 50:
            tier = "Intermediate"
            tier_icon = "🌟"
            tier_color = "warning"
            level = 2
        else:
            tier = "Beginner"
            tier_icon = "🌱"
            tier_color = "success"
            level = 1
        
        # Badge grande com tier
        badge_y = padding + 70
        
        children.append(f'''<g class="animated scale-in" style="animation-delay: 0.2s">
        <rect x="{padding}" y="{badge_y}" width="200" height="90" 
              rx="{self.theme['radiusLarge']}" 
              fill="url(#gradient-{tier_color})" opacity="0.15" 
              stroke="url(#gradient-{tier_color})" stroke-width="2" />
        <text x="{padding + 100}" y="{badge_y + 40}" 
              text-anchor="middle" font-size="42" font-weight="800">
            {tier_icon}
        </text>
        <text class="heading" x="{padding + 100}" y="{badge_y + 70}" 
              text-anchor="middle" font-size="20" font-weight="700" 
              fill="url(#gradient-{tier_color})">
            {tier}
        </text>
    </g>''')
        
        # Score e level
        info_x = padding + 240
        
        children.append(f'''<g class="animated" style="animation-delay: 0.3s">
        <text class="text-secondary" x="{info_x}" y="{badge_y + 20}" font-size="11">
            Developer Score
        </text>
        <text class="heading" x="{info_x}" y="{badge_y + 48}" 
              font-size="32" font-weight="700">
            {score}
        </text>
        <text class="text-secondary" x="{info_x}" y="{badge_y + 70}" font-size="12">
            Level {level}/5
        </text>
    </g>''')
        
        # Progress bar do level
        progress_y = badge_y + 100
        progress_width = width - padding * 2
        progress_height = 6
        progress_percentage = (level / 5) * 100
        fill_width = (progress_percentage / 100) * progress_width
        
        children.append(f'''<g class="animated" style="animation-delay: 0.4s">
        <rect x="{padding}" y="{progress_y}" width="{progress_width}" height="{progress_height}" 
              rx="3" fill="{self.theme['colors']['border']}" opacity="0.3" />
        <rect x="{padding}" y="{progress_y}" width="{fill_width}" height="{progress_height}" 
              rx="3" fill="url(#gradient-{tier_color})" />
    </g>''')
        
        svg_content = self.renderer.create_card_container(width, height, children)
        output_path = self.output_dir / output_name
        with open(output_path, 'w') as f:
            f.write(svg_content)
        
        return str(output_path)
    
    def generate_repo_card(self, repo: Dict[str, Any],
                          output_name: str = "repo_card.svg") -> str:
        """
        Gera card de repositório clicável.
        """
        width, height = 450, 140
        padding = 24
        
        children = []
        
        # Info do repo
        name = repo.get('name', 'Repository')
        description = repo.get('description', 'No description')[:60] + ('...' if len(repo.get('description', '')) > 60 else '')
        language = repo.get('language', 'Unknown')
        stars = repo.get('stars', 0)
        forks = repo.get('forks', 0)
        url = repo.get('html_url', '#')
        
        # Título (nome do repo)
        children.append(f'''<g class="animated">
        <text class="heading" x="{padding}" y="{padding + 20}" font-size="18" 
              font-weight="700" fill="url(#gradient-accent)">
            📦 {name}
        </text>
    </g>''')
        
        # Descrição
        children.append(f'''<g class="animated" style="animation-delay: 0.1s">
        <text class="text-secondary" x="{padding}" y="{padding + 48}" font-size="12">
            {description}
        </text>
    </g>''')
        
        # Stats (language, stars, forks)
        stats_y = padding + 85
        
        lang_color = self.theme.get('languageColors', {}).get(language, self.theme['colors']['accent'])
        
        children.append(f'''<g class="animated" style="animation-delay: 0.2s">
        <circle cx="{padding}" cy="{stats_y}" r="6" fill="{lang_color}" />
        <text class="text" x="{padding + 14}" y="{stats_y + 4}" font-size="12">
            {language}
        </text>
        
        <text class="text" x="{padding + 120}" y="{stats_y + 4}" font-size="12">
            ⭐ {stars}
        </text>
        
        <text class="text" x="{padding + 180}" y="{stats_y + 4}" font-size="12">
            🔀 {forks}
        </text>
    </g>''')
        
        svg_content = self.renderer.create_card_container(
            width, height, children, 
            clickable=True, link=url
        )
        output_path = self.output_dir / output_name
        with open(output_path, 'w') as f:
            f.write(svg_content)
        
        return str(output_path)
