"""
Activity Calendar Generator - Calendário de atividade estilo GitHub aprimorado

Cria visualização completa de atividade com:
- Calendário dos últimos 30 dias
- Todas as células (mesmo dias sem commits)
- Destaque para dia mais produtivo
- Estatísticas contextuais
- Visual profissional
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta


class ActivityCalendarGenerator:
    """Gerador de calendário de atividade profissional."""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.theme = self._load_theme()
        self.output_dir = self.base_path / "assets"
        self.output_dir.mkdir(exist_ok=True)
        
    def _load_theme(self, theme_name: str = "dark") -> Dict[str, Any]:
        theme_path = self.base_path / "themes" / f"{theme_name}.json"
        with open(theme_path, 'r') as f:
            return json.load(f)
    
    def _create_styles(self) -> str:
        """Estilos CSS para calendário."""
        return f"""
        * {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica', 'Arial', sans-serif;
        }}
        text {{ fill: {self.theme['colors']['text']}; }}
        .title {{ 
            font-size: 24px; 
            font-weight: 700; 
            fill: {self.theme['colors']['accent']}; 
        }}
        .subtitle {{ 
            font-size: 13px; 
            fill: {self.theme['colors']['textSecondary']}; 
        }}
        .label {{
            font-size: 11px;
            fill: {self.theme['colors']['textSecondary']};
        }}
        .label-small {{
            font-size: 9px;
            fill: {self.theme['colors']['textMuted']};
        }}
        .metric-value {{
            font-size: 32px;
            font-weight: 700;
        }}
        .metric-label {{
            font-size: 12px;
            font-weight: 500;
        }}
        .day-label {{
            font-size: 10px;
            fill: {self.theme['colors']['textMuted']};
        }}
        .stat-box {{
            font-size: 14px;
            font-weight: 600;
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        @keyframes slideUp {{
            from {{ transform: translateY(10px); opacity: 0; }}
            to {{ transform: translateY(0); opacity: 1; }}
        }}
        @keyframes highlight {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.7; }}
        }}
        .animated {{ animation: fadeIn 0.6s ease-out; }}
        .slide-up {{ animation: slideUp 0.5s ease-out; }}
        .highlight {{ animation: highlight 2s ease-in-out infinite; }}
        """
    
    def _get_activity_level_color(self, count: int, max_count: int) -> Tuple[str, float]:
        """
        Retorna cor e opacidade baseado no nível de atividade.
        Escala: None, Low, Medium, High, Peak
        """
        if count == 0:
            return self.theme['colors']['border'], 0.2
        
        if max_count == 0:
            return self.theme['colors']['success'], 0.3
        
        ratio = count / max_count
        
        if ratio >= 0.8:  # Peak (80-100%)
            return self.theme['colors']['success'], 1.0
        elif ratio >= 0.5:  # High (50-80%)
            return self.theme['colors']['success'], 0.7
        elif ratio >= 0.25:  # Medium (25-50%)
            return self.theme['colors']['accent'], 0.6
        else:  # Low (1-25%)
            return self.theme['colors']['accent'], 0.4
    
    def generate_activity_calendar(self, metrics: Dict[str, Any],
                                   output_name: str = "activity_calendar.svg") -> str:
        """Gera calendário de atividade completo."""
        width, height = 1200, 380
        
        daily_stats = metrics.get('daily_stats', {}).get('commits_per_day', [])
        
        # Últimos 30 dias
        today = datetime.now()
        days_data = []
        
        # Criar mapa de commits por data
        commits_map = {}
        for day in daily_stats:
            date_str = day.get('date', '')
            if date_str:
                commits_map[date_str] = day.get('count', 0)
        
        # Gerar últimos 30 dias (completo, com zeros)
        for i in range(29, -1, -1):
            date = today - timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            count = commits_map.get(date_str, 0)
            days_data.append({
                'date': date,
                'date_str': date_str,
                'count': count,
                'day_of_week': date.strftime('%a'),
                'day_num': date.day
            })
        
        # Estatísticas
        total_commits = sum(d['count'] for d in days_data)
        max_count = max((d['count'] for d in days_data), default=0)
        avg_per_day = total_commits / 30 if days_data else 0
        active_days = sum(1 for d in days_data if d['count'] > 0)
        
        # Encontrar dia mais produtivo
        most_productive = max(days_data, key=lambda x: x['count']) if days_data else None
        
        # Comparar com período anterior
        previous_days = daily_stats[-60:-30] if len(daily_stats) >= 60 else []
        prev_total = sum(day.get('count', 0) for day in previous_days)
        
        if prev_total > 0:
            change = ((total_commits - prev_total) / prev_total) * 100
            if change > 0:
                trend_arrow = "↑"
                trend_class = "trend-up"
                trend_text = f"+{change:.0f}%"
            elif change < 0:
                trend_arrow = "↓"
                trend_class = "trend-down"
                trend_text = f"{change:.0f}%"
            else:
                trend_arrow = "●"
                trend_class = "trend-neutral"
                trend_text = "±0%"
        else:
            trend_arrow = "●"
            trend_class = "trend-neutral"
            trend_text = "New"
        
        svg_parts = [f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
    <style>
        {self._create_styles()}
        .trend-up {{ fill: {self.theme['colors']['success']}; }}
        .trend-down {{ fill: {self.theme['colors']['danger']}; }}
        .trend-neutral {{ fill: {self.theme['colors']['textSecondary']}; }}
    </style>
    <rect width="{width}" height="{height}" fill="{self.theme['colors']['card']}" rx="12"/>
    
    <!-- Header -->
    <text class="title animated" x="40" y="45">📊 Activity Calendar</text>
    <text class="subtitle animated" x="40" y="70">Last 30 days of contribution activity</text>
''']
        
        # Card de métricas completo (lado esquerdo - 35% do espaço)
        metrics_x = 40
        metrics_y = 110
        metrics_width = 360  # 35% do espaço disponível
        metrics_height = 240
        
        streak_current = metrics.get('activity_streak', {}).get('current', 0)
        
        svg_parts.append(f'''
    <!-- Complete Metrics Card -->
    <g class="slide-up" style="animation-delay: 0.1s">
        <rect x="{metrics_x}" y="{metrics_y}" width="{metrics_width}" height="{metrics_height}" rx="12" 
              fill="{self.theme['colors']['background']}" opacity="0.6"
              stroke="{self.theme['colors']['border']}" stroke-width="1" stroke-opacity="0.3"/>
        
        <!-- Total Commits -->
        <text class="label" x="{metrics_x + 24}" y="{metrics_y + 30}">Total Commits</text>
        <text class="metric-value" x="{metrics_x + 24}" y="{metrics_y + 70}" 
              fill="{self.theme['colors']['accent']}">{total_commits}</text>
        <text class="{trend_class}" x="{metrics_x + 24}" y="{metrics_y + 90}" 
              style="font-size: 13px; font-weight: 600">{trend_arrow} {trend_text} vs prev</text>
        
        <!-- Divider -->
        <line x1="{metrics_x + 24}" y1="{metrics_y + 110}" x2="{metrics_x + metrics_width - 24}" y2="{metrics_y + 110}" 
              stroke="{self.theme['colors']['border']}" stroke-width="1" opacity="0.3"/>
        
        <!-- Most Productive Day -->
        <text class="label-small" x="{metrics_x + 24}" y="{metrics_y + 130}">
            🏆 Most Productive Day
        </text>
        <text class="metric-label" x="{metrics_x + 24}" y="{metrics_y + 150}" 
              fill="{self.theme['colors']['warning']}">
            {most_productive['date'].strftime('%b %d') if most_productive and most_productive['count'] > 0 else 'N/A'} • {most_productive['count'] if most_productive else 0} commits
        </text>
        
        <!-- Performance Stats -->
        <text class="label-small" x="{metrics_x + 24}" y="{metrics_y + 180}">
            � Performance
        </text>
        <text class="label-small" x="{metrics_x + 24}" y="{metrics_y + 200}">
            Active: {active_days}/30 days ({(active_days/30*100):.0f}%)
        </text>
        <text class="label-small" x="{metrics_x + 24}" y="{metrics_y + 215}">
            Streak: � {streak_current} days • Avg: {avg_per_day:.1f}/day
        </text>
    </g>
''')
        
        # Calendário (grid de dias) - 65% do espaço à direita
        calendar_start_x = 440  # Após o card de métricas
        calendar_start_y = 110
        calendar_width = width - calendar_start_x - 40  # Espaço disponível
        cell_size = 42  # Aumentado para ocupar mais espaço
        cell_spacing = 6
        cells_per_row = 10  # 10 colunas
        
        svg_parts.append(f'''
    <!-- Calendar Grid -->
    <g class="animated" style="animation-delay: 0.2s">
        <text class="label" x="{calendar_start_x}" y="{calendar_start_y - 10}">
            {days_data[0]['date'].strftime('%b %d')} - {days_data[-1]['date'].strftime('%b %d, %Y')}
        </text>
''')
        
        for i, day_data in enumerate(days_data):
            row = i // cells_per_row
            col = i % cells_per_row
            
            x = calendar_start_x + col * (cell_size + cell_spacing)
            y = calendar_start_y + 20 + row * (cell_size + cell_spacing + 20)
            
            count = day_data['count']
            color, opacity = self._get_activity_level_color(count, max_count)
            
            # Destaque para dia mais produtivo
            is_peak = (most_productive and day_data['date_str'] == most_productive['date_str'] 
                      and count > 0)
            
            stroke_color = self.theme['colors']['warning'] if is_peak else color
            stroke_width = 2.5 if is_peak else 1
            extra_class = " highlight" if is_peak else ""
            
            # Célula do dia
            svg_parts.append(f'''
        <g>
            <rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" 
                  rx="6" fill="{color}" opacity="{opacity}" 
                  stroke="{stroke_color}" stroke-width="{stroke_width}" class="slide-up{extra_class}"
                  style="animation-delay: {0.2 + i * 0.01}s">
                <title>{day_data['date'].strftime('%B %d, %Y')}: {count} commits</title>
            </rect>
            <text class="day-label" x="{x + cell_size/2}" y="{y + cell_size + 12}" 
                  text-anchor="middle">{day_data['day_num']}</text>
        </g>
''')
        
        svg_parts.append('    </g>')
        
        # Legenda de intensidade (abaixo do calendário)
        legend_y = calendar_start_y + 20 + 3 * (cell_size + cell_spacing + 20) + 20
        
        svg_parts.append(f'''
    <!-- Intensity Legend -->
    <g class="animated" style="animation-delay: 0.5s">
        <text class="label-small" x="{calendar_start_x}" y="{legend_y}">Less</text>
''')
        
        legend_colors = [
            (self.theme['colors']['border'], 0.2, "0"),
            (self.theme['colors']['accent'], 0.4, "1-{:.0f}".format(max_count * 0.25)),
            (self.theme['colors']['accent'], 0.6, "{:.0f}-{:.0f}".format(max_count * 0.25, max_count * 0.5)),
            (self.theme['colors']['success'], 0.7, "{:.0f}-{:.0f}".format(max_count * 0.5, max_count * 0.8)),
            (self.theme['colors']['success'], 1.0, "{:.0f}+".format(max_count * 0.8)),
        ]
        
        legend_cell_x = calendar_start_x + 35
        for i, (color, opacity, label) in enumerate(legend_colors):
            svg_parts.append(f'''
        <rect x="{legend_cell_x + i * 20}" y="{legend_y - 12}" width="16" height="16" 
              rx="4" fill="{color}" opacity="{opacity}"/>
''')
        
        svg_parts.append(f'''
        <text class="label-small" x="{legend_cell_x + len(legend_colors) * 20 + 5}" y="{legend_y}">More</text>
    </g>
''')
        
        svg_parts.append('</svg>')
        
        output_path = self.output_dir / output_name
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(svg_parts))
        
        return str(output_path)
