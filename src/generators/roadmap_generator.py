"""
Study Roadmap Generator - Sistema de roadmap dinâmico de estudos

Gera visualização de progresso de estudos com:
- Tracks de tecnologias (Frontend, Backend, DevOps, etc)
- Progresso por skill
- Metas e milestones
- Atualização via GitHub Actions
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime


class RoadmapGenerator:
    """Gerador de roadmap de estudos interativo."""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.theme = self._load_theme()
        self.roadmap_config = self._load_roadmap_config()
        self.output_dir = self.base_path / "assets"
        self.output_dir.mkdir(exist_ok=True)
        
    def _load_theme(self, theme_name: str = "dark") -> Dict[str, Any]:
        theme_path = self.base_path / "themes" / f"{theme_name}.json"
        with open(theme_path, 'r') as f:
            return json.load(f)
    
    def _load_roadmap_config(self) -> Dict[str, Any]:
        """Carrega configuração do roadmap."""
        config_path = self.base_path / "data" / "roadmap.json"
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        return self._create_default_roadmap()
    
    def _create_default_roadmap(self) -> Dict[str, Any]:
        """Cria roadmap padrão."""
        return {
            "tracks": [
                {
                    "name": "Frontend Development",
                    "icon": "🎨",
                    "color": "#61dafb",
                    "skills": [
                        {"name": "HTML/CSS", "level": 80, "target": 90},
                        {"name": "JavaScript", "level": 70, "target": 85},
                        {"name": "React", "level": 60, "target": 80},
                        {"name": "TypeScript", "level": 50, "target": 75},
                    ]
                },
                {
                    "name": "Backend Development",
                    "icon": "⚙️",
                    "color": "#3572A5",
                    "skills": [
                        {"name": "Python", "level": 75, "target": 90},
                        {"name": "Node.js", "level": 55, "target": 75},
                        {"name": "Databases", "level": 60, "target": 80},
                        {"name": "APIs", "level": 70, "target": 85},
                    ]
                },
                {
                    "name": "DevOps & Tools",
                    "icon": "🚀",
                    "color": "#2088FF",
                    "skills": [
                        {"name": "Git/GitHub", "level": 80, "target": 90},
                        {"name": "Docker", "level": 40, "target": 70},
                        {"name": "CI/CD", "level": 50, "target": 75},
                        {"name": "Linux", "level": 65, "target": 80},
                    ]
                }
            ],
            "goals": [
                {
                    "title": "Master React Ecosystem",
                    "progress": 65,
                    "deadline": "2026-06-30",
                    "priority": "high"
                },
                {
                    "title": "Build 5 Full-Stack Projects",
                    "progress": 40,
                    "deadline": "2026-12-31",
                    "priority": "medium"
                },
                {
                    "title": "Contribute to Open Source",
                    "progress": 30,
                    "deadline": "2026-08-31",
                    "priority": "high"
                }
            ]
        }
    
    def _create_styles(self) -> str:
        """Estilos para roadmap."""
        return f"""
        * {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica', 'Arial', sans-serif;
        }}
        text {{ fill: {self.theme['colors']['text']}; }}
        .title {{ 
            font-size: 22px; 
            font-weight: 700; 
            fill: {self.theme['colors']['accent']}; 
        }}
        .value {{
            font-size: 24px;
            font-weight: 700;
        }}
        .track-title {{
            font-size: 15px;
            font-weight: 600;
        }}
        .skill-name {{
            font-size: 12px;
            font-weight: 500;
        }}
        .skill-level {{
            font-size: 11px;
            font-weight: 600;
        }}
        .label {{
            font-size: 11px;
            opacity: 0.7;
        }}
        @keyframes fillProgress {{
            from {{ width: 0; }}
        }}
        .progress-bar {{
            animation: fillProgress 1s ease-out;
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        .animated {{ animation: fadeIn 0.6s ease-out; }}
        """
    
    def generate_skills_overview(self, output_name: str = "skills_roadmap.svg") -> str:
        """Gera overview de skills com progresso."""
        width, height = 900, 450
        
        tracks = self.roadmap_config.get('tracks', [])
        
        svg_parts = [f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
    <style>{self._create_styles()}</style>
    <rect width="{width}" height="{height}" fill="{self.theme['colors']['card']}" rx="12"/>
    <text class="title animated" x="30" y="40">🎯 Skills & Learning Roadmap</text>
    <text class="label" x="30" y="65">Track your progress across different tech stacks</text>
''']
        
        # Dividir em colunas
        col_width = 280
        x_start = 30
        y_start = 100
        
        for i, track in enumerate(tracks[:3]):  # Máximo 3 tracks
            x = x_start + (i * col_width)
            
            # Header do track
            svg_parts.append(f'''
    <g class="animated" style="animation-delay: {i * 0.15}s">
        <rect x="{x}" y="{y_start}" width="{col_width - 20}" height="300" rx="10" 
              fill="{track['color']}" opacity="0.08"/>
        <text class="track-title" x="{x + 15}" y="{y_start + 30}" fill="{track['color']}">
            {track['icon']} {track['name']}
        </text>
''')
            
            # Skills do track
            skill_y = y_start + 60
            for skill in track['skills']:
                level = skill['level']
                target = skill['target']
                bar_width = (level / 100) * (col_width - 60)
                target_x = x + 20 + (target / 100) * (col_width - 60)
                
                svg_parts.append(f'''
        <g>
            <text class="skill-name" x="{x + 20}" y="{skill_y}">{skill['name']}</text>
            <rect x="{x + 20}" y="{skill_y + 8}" width="{col_width - 60}" height="8" 
                  rx="4" fill="{self.theme['colors']['border']}" opacity="0.3"/>
            <rect class="progress-bar" x="{x + 20}" y="{skill_y + 8}" width="{bar_width}" height="8" 
                  rx="4" fill="{track['color']}" opacity="0.9"/>
            <line x1="{target_x}" y1="{skill_y + 4}" x2="{target_x}" y2="{skill_y + 20}" 
                  stroke="{self.theme['colors']['warning']}" stroke-width="2" stroke-dasharray="3,3" opacity="0.6"/>
            <text class="skill-level" x="{x + col_width - 50}" y="{skill_y + 2}" fill="{track['color']}">{level}%</text>
        </g>
''')
                skill_y += 45
            
            svg_parts.append('    </g>')
        
        svg_parts.append('</svg>')
        
        output_path = self.output_dir / output_name
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(svg_parts))
        
        return str(output_path)
    
    def generate_goals_tracker(self, output_name: str = "goals_tracker.svg") -> str:
        """Gera tracker de metas e objetivos aprimorado."""
        width, height = 900, 500
        
        goals = self.roadmap_config.get('goals', [])
        
        priority_colors = {
            "high": self.theme['colors']['danger'],
            "medium": self.theme['colors']['warning'],
            "low": self.theme['colors']['success']
        }
        
        priority_icons = {
            "high": "🔥",
            "medium": "⚡",
            "low": "✨"
        }
        
        svg_parts = [f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
    <style>{self._create_styles()}</style>
    <rect width="{width}" height="{height}" fill="{self.theme['colors']['card']}" rx="12"/>
    
    <!-- Header com estatísticas -->
    <text class="title animated" x="30" y="40">🎯 Goals &amp; Milestones</text>
''']
        
        # Calcular estatísticas gerais
        total_goals = len(goals)
        completed_goals = sum(1 for g in goals if g['progress'] >= 100)
        avg_progress = sum(g['progress'] for g in goals) / total_goals if total_goals > 0 else 0
        high_priority = sum(1 for g in goals if g['priority'] == 'high')
        
        # Cards de estatísticas no topo
        stats_y = 75
        svg_parts.append(f'''
    <!-- Estatísticas gerais -->
    <g class="animated" style="animation-delay: 0.1s">
        <rect x="30" y="{stats_y}" width="200" height="60" fill="{self.theme['colors']['background']}" rx="8" opacity="0.5"/>
        <text class="label" x="45" y="{stats_y + 20}">📊 Total Goals</text>
        <text class="value" x="45" y="{stats_y + 45}" fill="{self.theme['colors']['accent']}">{total_goals}</text>
    </g>
    
    <g class="animated" style="animation-delay: 0.2s">
        <rect x="245" y="{stats_y}" width="200" height="60" fill="{self.theme['colors']['background']}" rx="8" opacity="0.5"/>
        <text class="label" x="260" y="{stats_y + 20}">✅ Completed</text>
        <text class="value" x="260" y="{stats_y + 45}" fill="{self.theme['colors']['success']}">{completed_goals}</text>
    </g>
    
    <g class="animated" style="animation-delay: 0.3s">
        <rect x="460" y="{stats_y}" width="200" height="60" fill="{self.theme['colors']['background']}" rx="8" opacity="0.5"/>
        <text class="label" x="475" y="{stats_y + 20}">📈 Avg Progress</text>
        <text class="value" x="475" y="{stats_y + 45}" fill="{self.theme['colors']['accent']}">{avg_progress:.0f}%</text>
    </g>
    
    <g class="animated" style="animation-delay: 0.4s">
        <rect x="675" y="{stats_y}" width="195" height="60" fill="{self.theme['colors']['background']}" rx="8" opacity="0.5"/>
        <text class="label" x="690" y="{stats_y + 20}">🔥 High Priority</text>
        <text class="value" x="690" y="{stats_y + 45}" fill="{self.theme['colors']['danger']}">{high_priority}</text>
    </g>
''')
        
        # Lista de goals
        svg_parts.append(f'''
    <line x1="30" y1="160" x2="870" y2="160" stroke="{self.theme['colors']['border']}" stroke-width="1" opacity="0.3"/>
''')
        
        y_pos = 195
        for i, goal in enumerate(goals[:4]):  # Máximo 4 goals
            progress = min(goal['progress'], 100)
            bar_width = (progress / 100) * 740
            color = priority_colors.get(goal['priority'], self.theme['colors']['accent'])
            priority_icon = priority_icons.get(goal['priority'], '📌')
            
            # Calcular dias restantes
            try:
                deadline = datetime.strptime(goal['deadline'], '%Y-%m-%d')
                days_left = (deadline - datetime.now()).days
                
                if days_left < 0:
                    time_text = f"⚠️ {abs(days_left)} days overdue"
                    time_color = self.theme['colors']['danger']
                elif days_left < 7:
                    time_text = f"⏰ {days_left} days left"
                    time_color = self.theme['colors']['warning']
                else:
                    time_text = f"📅 {days_left} days left"
                    time_color = self.theme['colors']['textSecondary']
            except:
                time_text = "No deadline"
                time_color = self.theme['colors']['textSecondary']
                days_left = 999
            
            # Status badge
            if progress >= 100:
                status = "✓ COMPLETED"
                status_color = self.theme['colors']['success']
            elif progress >= 75:
                status = "Nearly done"
                status_color = self.theme['colors']['success']
            elif progress >= 50:
                status = "In progress"
                status_color = self.theme['colors']['accent']
            elif progress >= 25:
                status = "Started"
                status_color = self.theme['colors']['warning']
            else:
                status = "Planning"
                status_color = self.theme['colors']['textSecondary']
            
            svg_parts.append(f'''
    <g class="animated" style="animation-delay: {0.5 + i * 0.1}s">
        <!-- Card de fundo -->
        <rect x="30" y="{y_pos - 20}" width="840" height="65" fill="{self.theme['colors']['backgroundSecondary']}" 
              rx="10" stroke="{color}" stroke-width="2" stroke-opacity="0.3" fill-opacity="0.5"/>
        
        <!-- Ícone de prioridade -->
        <text x="45" y="{y_pos + 5}" style="font-size: 20px">{priority_icon}</text>
        
        <!-- Título do goal -->
        <text class="skill-name" x="75" y="{y_pos + 5}">{goal['title']}</text>
        
        <!-- Status badge -->
        <rect x="650" y="{y_pos - 12}" width="90" height="22" fill="{status_color}" rx="11" opacity="0.2"/>
        <text x="695" y="{y_pos + 3}" text-anchor="middle" 
              style="font-size: 10px; font-weight: 700; fill: {status_color}">{status}</text>
        
        <!-- Porcentagem grande -->
        <text x="850" y="{y_pos + 5}" text-anchor="end" 
              style="font-size: 18px; font-weight: 700; fill: {color}">{progress}%</text>
        
        <!-- Informações adicionais -->
        <text class="label" x="75" y="{y_pos + 22}" fill="{time_color}">
            {time_text} • Priority: {goal['priority'].upper()}
        </text>
        
        <!-- Barra de progresso -->
        <rect x="75" y="{y_pos + 30}" width="740" height="8" rx="4" 
              fill="{self.theme['colors']['border']}" opacity="0.3"/>
        <rect class="progress-bar" x="75" y="{y_pos + 30}" width="{bar_width}" height="8" 
              rx="4" fill="url(#goal-gradient-{i})" opacity="0.9">
            <animate attributeName="width" from="0" to="{bar_width}" dur="1.5s" begin="{0.5 + i * 0.1}s" fill="freeze"/>
        </rect>
        
        <!-- Gradiente da barra -->
        <defs>
            <linearGradient id="goal-gradient-{i}" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" style="stop-color:{color};stop-opacity:0.6" />
                <stop offset="100%" style="stop-color:{color};stop-opacity:0.9" />
            </linearGradient>
        </defs>
    </g>
''')
            y_pos += 80
        
        svg_parts.append('</svg>')
        
        output_path = self.output_dir / output_name
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(svg_parts))
        
        return str(output_path)
    
    def generate_learning_stats(self, metrics: Dict[str, Any],
                               output_name: str = "learning_stats.svg") -> str:
        """Gera roadmap de tópicos de estudo em duas colunas."""
        width, height = 1200, 500
        
        # Obter todos os skills de todas as tracks
        all_skills = []
        for track in self.roadmap_config.get('tracks', []):
            track_name = track['name']
            track_icon = track['icon']
            track_color = track['color']
            
            for skill in track.get('skills', []):
                all_skills.append({
                    'name': skill['name'],
                    'level': skill['level'],
                    'target': skill['target'],
                    'track': track_name,
                    'icon': track_icon,
                    'color': track_color,
                    'notes': skill.get('notes', '')
                })
        
        # Ordenar por progresso (level) descendente
        all_skills.sort(key=lambda x: x['level'], reverse=True)
        
        # Calcular estatísticas gerais
        total_skills = len(all_skills)
        avg_level = sum(s['level'] for s in all_skills) / total_skills if total_skills > 0 else 0
        mastered = sum(1 for s in all_skills if s['level'] >= 80)
        in_progress = sum(1 for s in all_skills if 50 <= s['level'] < 80)
        
        svg_parts = [f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
    <style>{self._create_styles()}</style>
    <rect width="{width}" height="{height}" fill="{self.theme['colors']['card']}" rx="12"/>
    
    <!-- Header -->
    <text class="title animated" x="30" y="40">📚 Learning Roadmap</text>
    <text class="label" x="30" y="65">Current skill levels and learning paths</text>
''']
        
        # Cards de estatísticas no topo
        stats_y = 90
        svg_parts.append(f'''
    <!-- Estatísticas gerais -->
    <g class="animated" style="animation-delay: 0.1s">
        <rect x="30" y="{stats_y}" width="270" height="55" fill="{self.theme['colors']['background']}" rx="8" opacity="0.5"/>
        <text class="label" x="45" y="{stats_y + 20}">📊 Total Skills</text>
        <text class="value" x="45" y="{stats_y + 42}" fill="{self.theme['colors']['accent']}">{total_skills}</text>
        <text class="label" x="150" y="{stats_y + 20}">✨ Avg Level</text>
        <text class="value" x="150" y="{stats_y + 42}" fill="{self.theme['colors']['accent']}">{avg_level:.0f}%</text>
    </g>
    
    <g class="animated" style="animation-delay: 0.2s">
        <rect x="315" y="{stats_y}" width="270" height="55" fill="{self.theme['colors']['background']}" rx="8" opacity="0.5"/>
        <text class="label" x="330" y="{stats_y + 20}">🎯 Mastered</text>
        <text class="value" x="330" y="{stats_y + 42}" fill="{self.theme['colors']['success']}">{mastered}</text>
        <text class="label" x="435" y="{stats_y + 20}">🔄 In Progress</text>
        <text class="value" x="435" y="{stats_y + 42}" fill="{self.theme['colors']['warning']}">{in_progress}</text>
    </g>
    
    <g class="animated" style="animation-delay: 0.3s">
        <rect x="600" y="{stats_y}" width="570" height="55" fill="{self.theme['colors']['background']}" rx="8" opacity="0.5"/>
        <text class="label" x="615" y="{stats_y + 20}">🏆 Top Skills</text>
        <text class="label" x="615" y="{stats_y + 42}" fill="{self.theme['colors']['text']}">{', '.join([s['name'] for s in all_skills[:3]])}</text>
    </g>
''')
        
        # Linha divisória
        svg_parts.append(f'''
    <line x1="30" y1="170" x2="1170" y2="170" stroke="{self.theme['colors']['border']}" stroke-width="1" opacity="0.3"/>
''')
        
        # Duas colunas de skills
        col_width = 570
        skills_per_col = 6
        left_skills = all_skills[:skills_per_col]
        right_skills = all_skills[skills_per_col:skills_per_col*2]
        
        # Coluna esquerda
        y_pos = 210
        for i, skill in enumerate(left_skills):
            progress = skill['level']
            target = skill['target']
            bar_width = (progress / 100) * 480
            color = skill['color']
            
            # Calcular gap até o target
            gap = target - progress
            gap_text = f"+{gap}% to target" if gap > 0 else "Target reached!"
            gap_color = self.theme['colors']['warning'] if gap > 0 else self.theme['colors']['success']
            
            svg_parts.append(f'''
    <g class="animated" style="animation-delay: {0.4 + i * 0.05}s">
        <!-- Ícone e nome -->
        <text x="40" y="{y_pos}" style="font-size: 16px">{skill['icon']}</text>
        <text class="skill-name" x="65" y="{y_pos}" style="font-size: 13px; font-weight: 600">{skill['name']}</text>
        
        <!-- Porcentagem -->
        <text x="540" y="{y_pos}" text-anchor="end" style="font-size: 14px; font-weight: 700; fill: {color}">{progress}%</text>
        
        <!-- Barra de progresso -->
        <rect x="40" y="{y_pos + 8}" width="480" height="6" rx="3" 
              fill="{self.theme['colors']['border']}" opacity="0.3"/>
        <rect x="40" y="{y_pos + 8}" width="{bar_width}" height="6" rx="3" fill="{color}" opacity="0.9">
            <animate attributeName="width" from="0" to="{bar_width}" dur="1s" begin="{0.4 + i * 0.05}s" fill="freeze"/>
        </rect>
        
        <!-- Target marker -->
        <circle cx="{40 + (target / 100 * 480)}" cy="{y_pos + 11}" r="3" fill="{color}" opacity="0.5"/>
        
        <!-- Gap info -->
        <text x="40" y="{y_pos + 26}" class="label" fill="{gap_color}" style="font-size: 9px">{gap_text}</text>
    </g>
''')
            y_pos += 42
        
        # Coluna direita
        y_pos = 210
        for i, skill in enumerate(right_skills):
            progress = skill['level']
            target = skill['target']
            bar_width = (progress / 100) * 480
            color = skill['color']
            
            # Calcular gap até o target
            gap = target - progress
            gap_text = f"+{gap}% to target" if gap > 0 else "Target reached!"
            gap_color = self.theme['colors']['warning'] if gap > 0 else self.theme['colors']['success']
            
            svg_parts.append(f'''
    <g class="animated" style="animation-delay: {0.4 + (i + skills_per_col) * 0.05}s">
        <!-- Ícone e nome -->
        <text x="640" y="{y_pos}" style="font-size: 16px">{skill['icon']}</text>
        <text class="skill-name" x="665" y="{y_pos}" style="font-size: 13px; font-weight: 600">{skill['name']}</text>
        
        <!-- Porcentagem -->
        <text x="1140" y="{y_pos}" text-anchor="end" style="font-size: 14px; font-weight: 700; fill: {color}">{progress}%</text>
        
        <!-- Barra de progresso -->
        <rect x="640" y="{y_pos + 8}" width="480" height="6" rx="3" 
              fill="{self.theme['colors']['border']}" opacity="0.3"/>
        <rect x="640" y="{y_pos + 8}" width="{bar_width}" height="6" rx="3" fill="{color}" opacity="0.9">
            <animate attributeName="width" from="0" to="{bar_width}" dur="1s" begin="{0.4 + (i + skills_per_col) * 0.05}s" fill="freeze"/>
        </rect>
        
        <!-- Target marker -->
        <circle cx="{640 + (target / 100 * 480)}" cy="{y_pos + 11}" r="3" fill="{color}" opacity="0.5"/>
        
        <!-- Gap info -->
        <text x="640" y="{y_pos + 26}" class="label" fill="{gap_color}" style="font-size: 9px">{gap_text}</text>
    </g>
''')
            y_pos += 42
        
        svg_parts.append('</svg>')
        
        output_path = self.output_dir / output_name
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(svg_parts))
        
        return str(output_path)
