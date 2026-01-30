"""
Advanced SVG Renderer - Gerador de SVGs modernos e profissionais

Este módulo cria SVGs com:
- Gradientes e sombras
- Animações CSS avançadas
- Hover effects e        .glass-card {
            fill: rgba(255, 255, 255, 0.05);
            stroke: {self.theme['colors']['border']};
            stroke-width: 1;
            opacity: 0.95;
        }tividade
- Links clicáveis
- Glassmorphism e design moderno
- Tooltips e badges
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import math


class AdvancedSVGRenderer:
    """
    Renderizador avançado de SVGs com design moderno e profissional.
    """
    
    def __init__(self, base_path: str = "."):
        """
        Inicializa o renderizador.
        
        Args:
            base_path: Caminho base do projeto
        """
        self.base_path = Path(base_path)
        self.theme = self._load_theme()
        self.output_dir = self.base_path / "assets"
        self.output_dir.mkdir(exist_ok=True)
        
    def _load_theme(self, theme_name: str = "dark") -> Dict[str, Any]:
        """Carrega tema."""
        theme_path = self.base_path / "themes" / f"{theme_name}.json"
        with open(theme_path, 'r') as f:
            return json.load(f)
    
    def _create_defs(self) -> str:
        """Cria definições SVG reutilizáveis (gradientes, filtros, etc)."""
        gradients_svg = []
        
        # Cria gradientes do tema
        for name, gradient in self.theme.get('gradients', {}).items():
            gradient_id = f"gradient-{name}"
            
            # Parse linear-gradient CSS
            if 'linear-gradient' in gradient:
                # Extrai ângulo e cores
                parts = gradient.replace('linear-gradient(', '').replace(')', '').split(',')
                angle = parts[0].strip()
                colors = [p.strip() for p in parts[1:]]
                
                # Converte ângulo para coordenadas SVG
                angle_deg = int(angle.replace('deg', ''))
                x1, y1, x2, y2 = self._angle_to_coords(angle_deg)
                
                stops = []
                for i, color_stop in enumerate(colors):
                    # Verifica se é rgba e pula gradientes complexos
                    if 'rgba' in color_stop.lower():
                        # Para gradientes rgba, usa uma cor sólida simplificada
                        if i == 0:
                            stops.append(f'<stop offset="0%" stop-color="rgba(255,255,255,0.1)" />')
                        else:
                            stops.append(f'<stop offset="100%" stop-color="rgba(255,255,255,0.05)" />')
                    else:
                        parts = color_stop.rsplit(' ', 1)
                        color = parts[0]
                        offset = parts[1] if len(parts) > 1 else f"{i * 100 / (len(colors) - 1) if len(colors) > 1 else 0}%"
                        stops.append(f'<stop offset="{offset}" stop-color="{color}" />')
                
                gradients_svg.append(f'''
        <linearGradient id="{gradient_id}" x1="{x1}%" y1="{y1}%" x2="{x2}%" y2="{y2}%">
            {chr(10).join(stops)}
        </linearGradient>''')
        
        # Filtros para sombras e efeitos
        filters = f'''
        <!-- Sombra suave -->
        <filter id="shadow-soft">
            <feGaussianBlur in="SourceAlpha" stdDeviation="4"/>
            <feOffset dx="0" dy="4" result="offsetblur"/>
            <feComponentTransfer>
                <feFuncA type="linear" slope="0.3"/>
            </feComponentTransfer>
            <feMerge>
                <feMergeNode/>
                <feMergeNode in="SourceGraphic"/>
            </feMerge>
        </filter>
        
        <!-- Sombra forte -->
        <filter id="shadow-strong">
            <feGaussianBlur in="SourceAlpha" stdDeviation="8"/>
            <feOffset dx="0" dy="8" result="offsetblur"/>
            <feComponentTransfer>
                <feFuncA type="linear" slope="0.4"/>
            </feComponentTransfer>
            <feMerge>
                <feMergeNode/>
                <feMergeNode in="SourceGraphic"/>
            </feMerge>
        </filter>
        
        <!-- Efeito de brilho -->
        <filter id="glow">
            <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
            <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
            </feMerge>
        </filter>
        
        <!-- Glassmorphism blur -->
        <filter id="glass-blur">
            <feGaussianBlur in="SourceGraphic" stdDeviation="10" />
        </filter>'''
        
        return f'''<defs>
        {chr(10).join(gradients_svg)}
        {filters}
    </defs>'''
    
    def _angle_to_coords(self, angle: int) -> Tuple[float, float, float, float]:
        """Converte ângulo CSS para coordenadas SVG linearGradient."""
        # Normaliza ângulo para 0-360
        angle = angle % 360
        
        # Converte para radianos
        rad = math.radians(angle - 90)
        
        # Calcula pontos finais
        x1 = 50 + 50 * math.cos(rad + math.pi)
        y1 = 50 + 50 * math.sin(rad + math.pi)
        x2 = 50 + 50 * math.cos(rad)
        y2 = 50 + 50 * math.sin(rad)
        
        return (x1, y1, x2, y2)
    
    def _create_styles(self) -> str:
        """Cria estilos CSS para o SVG."""
        return f'''<style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        * {{
            font-family: {self.theme['font']};
        }}
        
        .card {{
            fill: {self.theme['colors']['card']};
            transition: all {self.theme['animations']['duration']} {self.theme['animations']['easing']};
        }}
        
        .card:hover {{
            fill: {self.theme['colors']['cardHover']};
            filter: url(#shadow-strong);
        }}
        
        .glass-card {{
            fill: url(#gradient-glass);
            stroke: {self.theme['colors']['border']};
            stroke-width: 1;
            opacity: 0.95;
            backdrop-filter: blur(10px);
        }}
        
        .text {{
            fill: {self.theme['colors']['text']};
            font-size: {self.theme['sizes']['body']}px;
        }}
        
        .text-secondary {{
            fill: {self.theme['colors']['textSecondary']};
            font-size: {self.theme['sizes']['small']}px;
        }}
        
        .text-muted {{
            fill: {self.theme['colors']['textMuted']};
        }}
        
        .title {{
            fill: {self.theme['colors']['text']};
            font-size: {self.theme['sizes']['title']}px;
            font-weight: 700;
        }}
        
        .heading {{
            fill: {self.theme['colors']['text']};
            font-size: {self.theme['sizes']['heading']}px;
            font-weight: 600;
        }}
        
        .accent {{
            fill: {self.theme['colors']['accent']};
        }}
        
        .accent-gradient {{
            fill: url(#gradient-accent);
        }}
        
        .success {{
            fill: {self.theme['colors']['success']};
        }}
        
        .warning {{
            fill: {self.theme['colors']['warning']};
        }}
        
        .error {{
            fill: {self.theme['colors']['error']};
        }}
        
        /* Animações */
        @keyframes fadeIn {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        @keyframes slideInLeft {{
            from {{
                opacity: 0;
                transform: translateX(-30px);
            }}
            to {{
                opacity: 1;
                transform: translateX(0);
            }}
        }}
        
        @keyframes slideInRight {{
            from {{
                opacity: 0;
                transform: translateX(30px);
            }}
            to {{
                opacity: 1;
                transform: translateX(0);
            }}
        }}
        
        @keyframes scaleIn {{
            from {{
                opacity: 0;
                transform: scale(0.8);
            }}
            to {{
                opacity: 1;
                transform: scale(1);
            }}
        }}
        
        @keyframes pulse {{
            0%, 100% {{
                opacity: 1;
            }}
            50% {{
                opacity: 0.7;
            }}
        }}
        
        @keyframes spin {{
            from {{
                transform: rotate(0deg);
            }}
            to {{
                transform: rotate(360deg);
            }}
        }}
        
        @keyframes progress {{
            from {{
                stroke-dashoffset: 251.2;
            }}
            to {{
                stroke-dashoffset: 0;
            }}
        }}
        
        .animated {{
            animation: fadeIn {self.theme['animations']['durationSlow']} {self.theme['animations']['easing']} forwards;
        }}
        
        .slide-left {{
            animation: slideInLeft {self.theme['animations']['durationSlow']} {self.theme['animations']['easing']} forwards;
        }}
        
        .slide-right {{
            animation: slideInRight {self.theme['animations']['durationSlow']} {self.theme['animations']['easing']} forwards;
        }}
        
        .scale-in {{
            animation: scaleIn {self.theme['animations']['durationSlow']} {self.theme['animations']['easingBounce']} forwards;
        }}
        
        .pulse {{
            animation: pulse 2s ease-in-out infinite;
        }}
        
        /* Interatividade */
        .interactive {{
            cursor: pointer;
            transition: all {self.theme['animations']['duration']} {self.theme['animations']['easing']};
        }}
        
        .interactive:hover {{
            transform: translateY(-2px);
            filter: url(#shadow-strong);
        }}
        
        .bar {{
            transition: all {self.theme['animations']['duration']} {self.theme['animations']['easing']};
        }}
        
        .bar:hover {{
            opacity: 0.8;
            filter: url(#glow);
            cursor: pointer;
        }}
        
        .clickable {{
            cursor: pointer;
        }}
        
        .clickable:hover {{
            opacity: 0.85;
        }}
        
        /* Badges */
        .badge {{
            fill: {self.theme['colors']['accent']};
            opacity: 0.2;
        }}
        
        .badge-text {{
            fill: {self.theme['colors']['accent']};
            font-size: {self.theme['sizes']['small']}px;
            font-weight: 600;
        }}
        
        /* Progress rings */
        .progress-ring {{
            stroke: {self.theme['colors']['border']};
            stroke-width: 8;
            fill: none;
        }}
        
        .progress-ring-fill {{
            stroke: url(#gradient-accent);
            stroke-width: 8;
            fill: none;
            stroke-linecap: round;
            stroke-dasharray: 251.2;
            animation: progress 2s {self.theme['animations']['easing']} forwards;
        }}
        
        /* Tooltips */
        .tooltip {{
            opacity: 0;
            pointer-events: none;
            transition: opacity {self.theme['animations']['duration']} {self.theme['animations']['easing']};
        }}
        
        .interactive:hover .tooltip {{
            opacity: 1;
        }}
    </style>'''
    
    def create_card_container(self, width: int, height: int, children: List[str], 
                            glass: bool = False, clickable: bool = False,
                            link: Optional[str] = None) -> str:
        """
        Cria um container de card moderno.
        
        Args:
            width: Largura do SVG
            height: Altura do SVG
            children: Lista de elementos SVG filhos
            glass: Usar efeito glassmorphism
            clickable: Tornar clicável
            link: URL para redirecionar ao clicar
            
        Returns:
            String SVG completa
        """
        defs = self._create_defs()
        styles = self._create_styles()
        children_svg = '\n    '.join(children)
        
        card_class = "glass-card" if glass else "card"
        interactive_class = " interactive clickable" if clickable else ""
        
        card_rect = f'''<rect class="{card_class}{interactive_class}" x="0" y="0" 
            width="{width}" height="{height}" 
            rx="{self.theme['radiusLarge']}" 
            ry="{self.theme['radiusLarge']}" 
            filter="url(#shadow-soft)" />'''
        
        if link:
            card_rect = f'''<a href="{link}" target="_blank">
        {card_rect}
    </a>'''
        
        return f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
    {defs}
    {styles}
    <rect width="{width}" height="{height}" fill="{self.theme['colors']['background']}" />
    {card_rect}
    {children_svg}
</svg>'''
    
    def create_badge(self, text: str, x: int, y: int, color: str = "accent") -> str:
        """Cria um badge elegante."""
        padding = 8
        width = len(text) * 7 + padding * 2
        height = 24
        
        badge_color = self.theme['colors'].get(color, self.theme['colors']['accent'])
        
        return f'''<g class="animated">
        <rect class="badge" x="{x}" y="{y}" width="{width}" height="{height}" 
              rx="12" ry="12" fill="{badge_color}" />
        <text class="badge-text" x="{x + width/2}" y="{y + 16}" 
              text-anchor="middle" fill="{badge_color}">{text}</text>
    </g>'''
    
    def create_progress_ring(self, cx: int, cy: int, radius: int, 
                           percentage: float, label: str = "") -> str:
        """Cria um anel de progresso circular animado."""
        circumference = 2 * math.pi * radius
        offset = circumference - (percentage / 100) * circumference
        
        return f'''<g class="scale-in">
        <circle class="progress-ring" cx="{cx}" cy="{cy}" r="{radius}" 
                transform="rotate(-90 {cx} {cy})" />
        <circle class="progress-ring-fill" cx="{cx}" cy="{cy}" r="{radius}" 
                transform="rotate(-90 {cx} {cy})" 
                stroke-dashoffset="{offset}" />
        <text class="heading accent" x="{cx}" y="{cy}" text-anchor="middle" 
              dominant-baseline="middle">{int(percentage)}%</text>
        <text class="text-secondary" x="{cx}" y="{cy + 20}" text-anchor="middle" 
              font-size="10">{label}</text>
    </g>'''
    
    def create_stat_box(self, x: int, y: int, width: int, height: int,
                       label: str, value: str, icon: str = "",
                       gradient: str = "accent", delay: float = 0) -> str:
        """Cria uma caixa de estatística moderna."""
        return f'''<g class="animated interactive" style="animation-delay: {delay}s">
        <rect x="{x}" y="{y}" width="{width}" height="{height}" 
              rx="{self.theme['radius']}" fill="url(#gradient-{gradient})" opacity="0.15" />
        <text class="text-secondary" x="{x + 16}" y="{y + 24}" 
              font-size="12">{label}</text>
        <text class="heading" x="{x + 16}" y="{y + 52}" 
              font-size="32" font-weight="700">
            <tspan fill="url(#gradient-{gradient})">{icon}</tspan> {value}
        </text>
    </g>'''
    
    def create_tooltip(self, x: int, y: int, text: str) -> str:
        """Cria um tooltip."""
        padding = 8
        width = len(text) * 7 + padding * 2
        height = 28
        
        return f'''<g class="tooltip">
        <rect x="{x - width/2}" y="{y - height - 8}" width="{width}" height="{height}" 
              rx="6" fill="{self.theme['colors']['cardHover']}" 
              stroke="{self.theme['colors']['border']}" stroke-width="1" 
              filter="url(#shadow-soft)" />
        <text class="text" x="{x}" y="{y - height/2 - 4}" text-anchor="middle" 
              font-size="11">{text}</text>
    </g>'''
