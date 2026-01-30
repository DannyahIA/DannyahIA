"""
Career Timeline Generator - Timeline profissional elegante

Cria uma timeline horizontal de 1200px com:
- Experiências profissionais
- Educação
- Certificações
- Controle de privacidade (ocultar datas, duração, etc)
- Visual moderno com animações
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
from dateutil.relativedelta import relativedelta
import html


class CareerTimelineGenerator:
    """Gerador de timeline de carreira."""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.theme = self._load_theme()
        self.career_data = self._load_career_data()
        self.output_dir = self.base_path / "assets"
        self.output_dir.mkdir(exist_ok=True)
        
    def _load_theme(self, theme_name: str = "dark") -> Dict[str, Any]:
        theme_path = self.base_path / "themes" / f"{theme_name}.json"
        with open(theme_path, 'r') as f:
            return json.load(f)
    
    def _load_career_data(self) -> Dict[str, Any]:
        """Carrega dados de carreira."""
        career_path = self.base_path / "data" / "career.json"
        if career_path.exists():
            with open(career_path, 'r') as f:
                return json.load(f)
        return {"professional_timeline": [], "certifications": []}
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string."""
        if date_str.lower() == "present":
            return datetime.now()
        return datetime.strptime(date_str, "%Y-%m")
    
    def _format_date(self, date_str: str, mode: str = "month_year") -> str:
        """Formata data baseado no modo de privacidade."""
        if date_str.lower() == "present":
            return "Present"
        
        date = self._parse_date(date_str)
        
        if mode == "year_only":
            return date.strftime("%Y")
        elif mode == "month_year":
            return date.strftime("%b %Y")
        elif mode == "hidden":
            return "•••"
        
        return date.strftime("%b %Y")
    
    def _escape_xml(self, text: str) -> str:
        """Escapa caracteres especiais XML/HTML."""
        return html.escape(str(text))
    
    def _calculate_total_experience(self, entries: List[Dict]) -> str:
        """
        Calcula experiência total considerando períodos paralelos.
        
        Por exemplo, se você trabalhou em duas empresas simultaneamente,
        conta apenas uma vez esse período.
        """
        if not entries:
            return "0y"
        
        # Coletar todos os períodos
        periods = []
        for entry in entries:
            if entry.get('type') == 'work':
                start = self._parse_date(entry.get('date_start', ''))
                end = self._parse_date(entry.get('date_end', 'present'))
                periods.append((start, end))
        
        if not periods:
            return "0y"
        
        # Ordenar por data de início
        periods.sort(key=lambda x: x[0])
        
        # Mesclar períodos sobrepostos
        merged = [periods[0]]
        for current_start, current_end in periods[1:]:
            last_start, last_end = merged[-1]
            
            # Se o período atual começa antes do último terminar (sobreposição)
            if current_start <= last_end:
                # Estender o período mesclado até o fim mais tardio
                merged[-1] = (last_start, max(last_end, current_end))
            else:
                # Períodos não se sobrepõem, adicionar novo
                merged.append((current_start, current_end))
        
        # Calcular total de meses dos períodos mesclados
        total_months = 0
        for start, end in merged:
            delta = relativedelta(end, start)
            total_months += delta.years * 12 + delta.months
        
        # Converter para anos e meses
        years = total_months // 12
        months = total_months % 12
        
        parts = []
        if years > 0:
            parts.append(f"{years}y")
        if months > 0:
            parts.append(f"{months}m")
        
        return " ".join(parts) if parts else "&lt; 1m"
    
    def _calculate_duration(self, start: str, end: str) -> str:
        """Calcula duração entre datas."""
        start_date = self._parse_date(start)
        end_date = self._parse_date(end)
        
        delta = relativedelta(end_date, start_date)
        
        years = delta.years
        months = delta.months
        
        parts = []
        if years > 0:
            parts.append(f"{years}y")
        if months > 0:
            parts.append(f"{months}m")
        
        return " ".join(parts) if parts else "&lt; 1m"
    
    def _create_styles(self) -> str:
        """Estilos CSS para timeline."""
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
            font-size: 14px; 
            fill: {self.theme['colors']['textSecondary']}; 
        }}
        .entry-title {{
            font-size: 15px;
            font-weight: 600;
            fill: {self.theme['colors']['text']};
        }}
        .entry-company {{
            font-size: 13px;
            font-weight: 500;
        }}
        .entry-date {{
            font-size: 11px;
            fill: {self.theme['colors']['textSecondary']};
        }}
        .entry-desc {{
            font-size: 11px;
            fill: {self.theme['colors']['textMuted']};
        }}
        .label-small {{
            font-size: 9px;
            fill: {self.theme['colors']['textSecondary']};
        }}
        .tech-badge {{
            font-size: 9px;
            font-weight: 600;
            fill: {self.theme['colors']['accent']};
        }}
        .timeline-line {{
            stroke: {self.theme['colors']['border']};
            stroke-width: 3;
        }}
        .timeline-dot {{
            fill: {self.theme['colors']['accent']};
        }}
        .timeline-dot-work {{
            fill: {self.theme['colors']['success']};
        }}
        .timeline-dot-education {{
            fill: {self.theme['colors']['purple']};
        }}
        .timeline-dot-current {{
            fill: {self.theme['colors']['warning']};
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        @keyframes slideIn {{
            from {{ transform: translateX(-20px); opacity: 0; }}
            to {{ transform: translateX(0); opacity: 1; }}
        }}
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}
        .animated {{ animation: fadeIn 0.6s ease-out; }}
        .slide-in {{ animation: slideIn 0.5s ease-out; }}
        .pulse {{ animation: pulse 2s ease-in-out infinite; }}
        .cert-badge {{
            font-size: 11px;
            font-weight: 600;
        }}
        """
    
    def generate_timeline(self, output_name: str = "career_timeline.svg") -> str:
        """Gera timeline profissional completa."""
        timeline_entries = self.career_data.get('professional_timeline', [])
        certifications = self.career_data.get('certifications', [])
        meta = self.career_data.get('meta', {})
        
        # Constantes de layout
        cards_per_row = 4
        card_height = 140
        card_spacing_above = 200  # Espaço para cards acima da timeline
        card_spacing_below = 220  # Espaço para cards abaixo da timeline
        row_spacing = card_spacing_below + 60  # Espaçamento menor para layout intercalado
        header_height = 120  # Espaço para o título
        footer_height = 120  # Espaço para certificações
        
        # Calcular número de linhas
        num_entries = len(timeline_entries)
        num_rows = (num_entries + cards_per_row - 1) // cards_per_row
        
        # Calcular altura total dinamicamente
        # Primeira linha precisa de espaço acima e abaixo
        # Linhas seguintes precisam apenas de espaço adicional
        if num_rows == 0:
            height = 400
        elif num_rows == 1:
            height = header_height + card_spacing_above + card_spacing_below + footer_height
        else:
            # Header + espaço da primeira linha + espaços das linhas adicionais + footer
            height = header_height + (card_spacing_above + card_spacing_below) + (row_spacing * (num_rows - 1)) + footer_height
        
        width = 1200
        
        # Configurações de privacidade
        date_mode = meta.get('show_dates', 'year_only')
        show_duration = meta.get('show_duration', False)
        
        svg_parts = [f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
    <style>{self._create_styles()}</style>
    <rect width="{width}" height="{height}" fill="{self.theme['colors']['card']}" rx="12"/>
    
    <!-- Header -->
    <text class="title animated" x="40" y="45">💼 Professional Journey</text>
    <text class="subtitle animated" x="40" y="70">Career milestones and achievements</text>
''']
        
        if not timeline_entries:
            svg_parts.append('</svg>')
            output_path = self.output_dir / output_name
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(svg_parts))
            return str(output_path)
        
        # Ordenar entries por data de início
        sorted_entries = sorted(
            timeline_entries,
            key=lambda e: self._parse_date(e.get('date_start', ''))
        )
        
        # Dividir entries em linhas
        rows = []
        for i in range(0, len(sorted_entries), cards_per_row):
            rows.append(sorted_entries[i:i + cards_per_row])
        
        # Desenhar cada linha da timeline
        timeline_start_x = 80
        timeline_end_x = width - 80
        base_timeline_y = header_height + card_spacing_above
        
        for row_idx, row_entries in enumerate(rows):
            timeline_y = base_timeline_y + (row_idx * row_spacing)
            
            # Desenhar linha horizontal
            if row_idx == 0:
                # Primeira linha: linha reta
                svg_parts.append(f'''
    <line class="timeline-line animated" x1="{timeline_start_x}" y1="{timeline_y}" 
          x2="{timeline_end_x}" y2="{timeline_y}" stroke-linecap="round"/>
''')
            else:
                # Linhas seguintes: conectar com curva da linha anterior
                prev_timeline_y = base_timeline_y + ((row_idx - 1) * row_spacing)
                curve_start_x = timeline_end_x
                curve_end_x = timeline_start_x
                
                # Curva conectando as linhas (S-curve)
                svg_parts.append(f'''
    <!-- Curva de conexão -->
    <path class="timeline-line animated" 
          d="M {curve_start_x} {prev_timeline_y} 
             C {curve_start_x + 40} {prev_timeline_y}, {curve_start_x + 40} {timeline_y}, {curve_start_x} {timeline_y}
             L {curve_end_x} {timeline_y}"
          fill="none" stroke-linecap="round"/>
    
    <!-- Seta indicando direção da timeline -->
    <polygon points="{curve_end_x},{timeline_y} {curve_end_x + 30},{timeline_y - 16} {curve_end_x + 30},{timeline_y + 16}"
             fill="{self.theme['colors']['border']}" class="animated" opacity="0.7"/>
''')
            
            # Calcular espaçamento entre cards
            card_spacing = (timeline_end_x - timeline_start_x) / max(len(row_entries), 1)
            
            # Desenhar cada card na linha
            for i, entry in enumerate(row_entries):
                x_pos = timeline_start_x + (i * card_spacing) + (card_spacing / 2)
                
                # Alternar posição (em cima/embaixo da linha)
                # Primeira linha: alterna normalmente (0=cima, 1=baixo, 2=cima, 3=baixo)
                # Segunda linha: todos embaixo (intercalando com os de baixo da primeira)
                if row_idx == 0:
                    # Primeira linha: alterna normalmente
                    is_top = i % 2 == 0
                else:
                    # Linhas seguintes: sempre embaixo (intercalando)
                    is_top = False
                
                y_offset = -20 if is_top else 20
                content_y = timeline_y + y_offset + (-180 if is_top else 60)
                
                # Determinar cor do dot e da linha conectora
                entry_type = entry.get('type', 'work')
                is_current = entry.get('date_end', '').lower() == 'present'
                
                if is_current:
                    dot_class = 'timeline-dot-current pulse'
                    dot_radius = 8
                    connector_color = self.theme['colors']['warning']
                elif entry_type == 'work':
                    dot_class = 'timeline-dot-work'
                    dot_radius = 6
                    connector_color = self.theme['colors']['success']
                else:
                    dot_class = 'timeline-dot-education'
                    dot_radius = 6
                    connector_color = self.theme['colors']['purple']
                
                # Linha conectora com cor baseada no tipo
                global_index = row_idx * cards_per_row + i
                connector_end_y = content_y + 140 if is_top else content_y - 10
                svg_parts.append(f'''
    <line class="slide-in" x1="{x_pos}" y1="{timeline_y}" x2="{x_pos}" y2="{connector_end_y}" 
          stroke="{connector_color}" stroke-width="2" stroke-dasharray="4,4" 
          opacity="0.3" style="animation-delay: {global_index * 0.15}s"/>
''')
                
                # Dot na timeline
                svg_parts.append(f'''
    <circle class="{dot_class}" cx="{x_pos}" cy="{timeline_y}" r="{dot_radius}" 
            style="animation-delay: {global_index * 0.15}s"/>
''')
                
                # Card do entry
                card_width = 260
                card_height = 140
                card_x = x_pos - card_width / 2
                card_y = content_y
                
                # Cor do card baseada no tipo
                if entry_type == 'work':
                    border_color = self.theme['colors']['success']
                    type_icon = "💼"
                else:
                    border_color = self.theme['colors']['purple']
                    type_icon = "🎓"
                
                svg_parts.append(f'''
    <g class="slide-in" style="animation-delay: {global_index * 0.15}s">
        <rect x="{card_x}" y="{card_y}" width="{card_width}" height="{card_height}" 
              rx="8" fill="{self.theme['colors']['background']}" 
              stroke="{border_color}" stroke-width="2" opacity="0.95"/>
''')
            
            # Conteúdo do card
                text_x = card_x + 12
                text_y = card_y + 22
                
                # Título
                title = entry.get('title', 'Position')
                if len(title) > 28:
                    title = title[:25] + "..."
                title = self._escape_xml(title)
                svg_parts.append(f'''
        <text class="entry-title" x="{text_x}" y="{text_y}">{type_icon} {title}</text>
''')
                
                # Empresa
                company = entry.get('company', 'Company')
                if len(company) > 30:
                    company = company[:27] + "..."
                company = self._escape_xml(company)
                svg_parts.append(f'''
        <text class="entry-company" x="{text_x}" y="{text_y + 18}" fill="{border_color}">{company}</text>
''')
                
                # Datas
                start_date = self._format_date(entry.get('date_start', ''), date_mode)
                end_date = self._format_date(entry.get('date_end', 'present'), date_mode)
                date_text = f"{start_date} - {end_date}"
                
                if show_duration or entry.get('show_duration', False):
                    duration = self._calculate_duration(entry.get('date_start', ''), entry.get('date_end', 'present'))
                    date_text += f" ({duration})"
                
                date_text = self._escape_xml(date_text)
                svg_parts.append(f'''
        <text class="entry-date" x="{text_x}" y="{text_y + 36}">{date_text}</text>
''')
                
                # Descrição (truncada)
                desc = entry.get('description', '')
                if len(desc) > 38:
                    desc = desc[:35] + "..."
                desc = self._escape_xml(desc)
                svg_parts.append(f'''
        <text class="entry-desc" x="{text_x}" y="{text_y + 52}">{desc}</text>
''')
                
                # Tecnologias (badges)
                techs = entry.get('technologies', [])[:3]  # Máximo 3
                badge_y = text_y + 70
                badge_x = text_x
                
                for tech in techs:
                    tech_escaped = self._escape_xml(tech)
                    tech_width = len(tech) * 6 + 12
                    svg_parts.append(f'''
        <rect x="{badge_x}" y="{badge_y}" width="{tech_width}" height="16" 
                  rx="8" fill="{border_color}" opacity="0.15"/>
        <text class="tech-badge" x="{badge_x + 6}" y="{badge_y + 11}" fill="{border_color}">{tech_escaped}</text>
''')
                    badge_x += tech_width + 6
                
                # Fechar o grupo do card (DEPOIS do loop for tech, MAS DENTRO do loop for entry)
                svg_parts.append('    </g>')
        
        # Certificações (footer)
        if certifications:
            cert_y = height - 100  # Ajustado para nova altura
            svg_parts.append(f'''
    <line x1="80" y1="{cert_y - 10}" x2="{width - 80}" y2="{cert_y - 10}" 
          stroke="{self.theme['colors']['border']}" stroke-width="1" opacity="0.3"/>
    <text class="subtitle animated" x="80" y="{cert_y + 10}">🏆 Certifications</text>
''')
            
            cert_x = 80
            cert_item_y = cert_y + 35
            
            for cert in certifications[:5]:  # Máximo 5 certificações
                if not cert.get('show', True):
                    continue
                
                cert_name = self._escape_xml(cert.get('name', 'Certification'))
                cert_date = self._escape_xml(self._format_date(cert.get('date', ''), 'year_only'))
                
                svg_parts.append(f'''
    <g class="animated">
        <circle cx="{cert_x}" cy="{cert_item_y}" r="4" fill="{self.theme['colors']['warning']}"/>
        <text class="cert-badge" x="{cert_x + 12}" y="{cert_item_y + 4}">{cert_name}</text>
        <text class="entry-date" x="{cert_x + 12}" y="{cert_item_y + 17}">({cert_date})</text>
    </g>
''')
                cert_x += 230  # Reduzido para caber 5
        
        # Adicionar legenda de tempo total no canto (usando nova função que considera períodos paralelos)
        total_experience = self._calculate_total_experience(timeline_entries)
        svg_parts.append(f'''
    <g class="animated">
        <rect x="{width - 220}" y="95" width="180" height="50" rx="8" 
              fill="{self.theme['colors']['background']}" opacity="0.8"/>
        <text class="subtitle" x="{width - 210}" y="115">Total Experience</text>
        <text style="font-size: 20px; font-weight: 700" x="{width - 210}" y="138" 
              fill="{self.theme['colors']['success']}">{total_experience}</text>
    </g>
''')
        
        svg_parts.append('</svg>')
        
        output_path = self.output_dir / output_name
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(svg_parts))
        
        return str(output_path)
    
    def generate_compact_experience(self, output_name: str = "experience_compact.svg") -> str:
        """Gera versão compacta de experiência (para usar com outros cards)."""
        width, height = 450, 240
        
        timeline_entries = self.career_data.get('professional_timeline', [])
        work_entries = [e for e in timeline_entries if e.get('type') == 'work']
        
        # Calcular total de experiência (considerando períodos paralelos)
        total_experience = self._calculate_total_experience(work_entries)
        
        # Extrair apenas o número de anos para display
        years_display = total_experience.split('y')[0] if 'y' in total_experience else '0'
        
        svg_content = f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
    <style>{self._create_styles()}</style>
    <rect width="{width}" height="{height}" fill="{self.theme['colors']['card']}" rx="12"/>
    
    <text class="title animated" x="24" y="35" style="font-size: 20px">💼 Experience</text>
    <text class="subtitle animated" x="24" y="60">Professional background</text>
    
    <!-- Total Experience -->
    <g class="animated" style="animation-delay: 0.2s">
        <circle cx="80" cy="130" r="50" fill="{self.theme['colors']['success']}" opacity="0.15"/>
        <text style="font-size: 32px; font-weight: 700" x="80" y="135" text-anchor="middle" 
              fill="{self.theme['colors']['success']}">{years_display}</text>
        <text class="entry-date" x="80" y="155" text-anchor="middle">years</text>
    </g>
    
    <!-- Recent Positions -->
    <g class="slide-in" style="animation-delay: 0.3s">
        <text class="subtitle" x="160" y="100">Current Position</text>
        <text class="entry-title" x="160" y="125" style="font-size: 13px">{work_entries[0].get('title', 'N/A') if work_entries else 'N/A'}</text>
        <text class="entry-company" x="160" y="145" fill="{self.theme['colors']['success']}">{work_entries[0].get('company', 'N/A') if work_entries else 'N/A'}</text>
    </g>
    
    <g class="slide-in" style="animation-delay: 0.4s">
        <text class="subtitle" x="160" y="170">Total Positions</text>
        <text style="font-size: 24px; font-weight: 700" x="160" y="200" fill="{self.theme['colors']['accent']}">{len(work_entries)}</text>
    </g>
</svg>'''
        
        output_path = self.output_dir / output_name
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        return str(output_path)
