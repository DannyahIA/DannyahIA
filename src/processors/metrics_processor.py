"""
Metrics Processor

Este módulo transforma dados brutos em métricas agregadas.

CAMADAS DE DADOS:
1. Dados brutos (API) → vem do collector
2. Dados agregados (métricas) → este módulo processa
3. Histórico → mantém registro ao longo do tempo

Por quê separar processamento de coleta?
- Coleta pode falhar (API indisponível)
- Processamento pode evoluir sem recolher dados
- Facilita testes e debugging
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any
from collections import Counter, defaultdict
import json


class MetricsProcessor:
    """
    Processa dados brutos e gera métricas agregadas.
    """
    
    def __init__(self, repos: List[Dict], commits: List[Dict], 
                 prs: List[Dict], issues: List[Dict]):
        """
        Inicializa com dados brutos coletados.
        
        Args:
            repos: Lista de repositórios
            commits: Lista de commits
            prs: Lista de pull requests
            issues: Lista de issues
        """
        self.repos = repos
        self.commits = commits
        self.prs = prs
        self.issues = issues
    
    def calculate_daily_stats(self) -> Dict[str, Any]:
        """
        Calcula estatísticas diárias de commits.
        
        Por quê isso é útil?
        - Mostra consistência do trabalho
        - Identifica dias mais produtivos
        - Calcula média de commits por dia
        
        Returns:
            Dicionário com commits por dia e médias
        """
        # Agrupa commits por data
        commits_by_date = defaultdict(int)
        
        for commit in self.commits:
            # Extrai apenas a data (sem hora)
            date = datetime.fromisoformat(commit['date']).date().isoformat()
            commits_by_date[date] += 1
        
        # Converte para lista ordenada
        daily_commits = [
            {'date': date, 'count': count}
            for date, count in sorted(commits_by_date.items())
        ]
        
        # Calcula média
        total_days = len(commits_by_date) if commits_by_date else 1
        average = len(self.commits) / total_days
        
        return {
            'commits_per_day': daily_commits,
            'average_commits': round(average, 2),
            'total_days_active': len(commits_by_date)
        }
    
    def calculate_weekly_stats(self) -> Dict[str, Any]:
        """
        Calcula estatísticas semanais (PRs e Issues).
        
        Por quê agrupar por semana?
        - Padrão comum de trabalho (sprint semanal)
        - Bom para relatórios semanais
        - Suaviza variações diárias
        """
        # Agrupa PRs por semana
        prs_by_week = defaultdict(int)
        for pr in self.prs:
            date = datetime.fromisoformat(pr['created_at'])
            # isocalendar() retorna (ano, semana, dia)
            week = f"{date.year}-W{date.isocalendar()[1]:02d}"
            prs_by_week[week] += 1
        
        # Agrupa issues fechadas por semana
        issues_closed_by_week = defaultdict(int)
        for issue in self.issues:
            if issue['closed_at']:
                date = datetime.fromisoformat(issue['closed_at'])
                week = f"{date.year}-W{date.isocalendar()[1]:02d}"
                issues_closed_by_week[week] += 1
        
        return {
            'prs_per_week': [
                {'week': week, 'count': count}
                for week, count in sorted(prs_by_week.items())
            ],
            'issues_closed_per_week': [
                {'week': week, 'count': count}
                for week, count in sorted(issues_closed_by_week.items())
            ]
        }
    
    def calculate_monthly_stats(self) -> Dict[str, Any]:
        """
        Calcula estatísticas do mês atual.
        
        Por quê separar stats mensais?
        - Resumos mensais precisam desses dados
        - Facilita comparação mês a mês
        - Evita recalcular ao gerar relatório mensal
        """
        now = datetime.now(timezone.utc)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Filtra commits deste mês
        commits_this_month = [
            c for c in self.commits
            if datetime.fromisoformat(c['date']) >= month_start
        ]
        
        # Filtra PRs deste mês
        prs_this_month = [
            pr for pr in self.prs
            if datetime.fromisoformat(pr['created_at']) >= month_start
        ]
        
        # Filtra issues deste mês
        issues_this_month = [
            i for i in self.issues
            if datetime.fromisoformat(i['created_at']) >= month_start
        ]
        
        return {
            'commits_this_month': len(commits_this_month),
            'prs_this_month': len(prs_this_month),
            'issues_this_month': len(issues_this_month),
            'month': now.strftime('%Y-%m')
        }
    
    def calculate_top_languages(self) -> Dict[str, int]:
        """
        Identifica as linguagens mais usadas.
        
        Por quê isso importa?
        - Mostra stack tecnológico
        - Útil para badges e perfil
        - Indica áreas de expertise
        
        Returns:
            Dicionário {linguagem: número de repos}
        """
        languages = Counter()
        
        for repo in self.repos:
            lang = repo.get('language')
            if lang:  # Ignora repos sem linguagem definida
                languages[lang] += 1
        
        # Retorna top 10 linguagens
        return dict(languages.most_common(10))
    
    def calculate_activity_streak(self) -> Dict[str, int]:
        """
        Calcula sequência de dias com atividade.
        
        Por quê streak é motivador?
        - Gamifica a consistência
        - Incentiva commits diários
        - Mostra dedicação
        
        Returns:
            Sequência atual e mais longa
        """
        if not self.commits:
            return {'current': 0, 'longest': 0}
        
        # Ordena commits por data
        dates = sorted([
            datetime.fromisoformat(c['date']).date()
            for c in self.commits
        ])
        
        # Remove duplicatas (vários commits no mesmo dia)
        unique_dates = sorted(set(dates))
        
        # Calcula streaks
        current_streak = 0
        longest_streak = 0
        temp_streak = 1
        
        today = datetime.now(timezone.utc).date()
        
        # Verifica se há atividade hoje ou ontem (streak atual)
        if unique_dates and (today - unique_dates[-1]).days <= 1:
            current_streak = 1
            
            # Conta dias consecutivos anteriores
            for i in range(len(unique_dates) - 1, 0, -1):
                diff = (unique_dates[i] - unique_dates[i-1]).days
                if diff == 1:
                    current_streak += 1
                else:
                    break
        
        # Calcula maior streak histórico
        for i in range(1, len(unique_dates)):
            diff = (unique_dates[i] - unique_dates[i-1]).days
            if diff == 1:
                temp_streak += 1
                longest_streak = max(longest_streak, temp_streak)
            else:
                temp_streak = 1
        
        longest_streak = max(longest_streak, temp_streak)
        
        return {
            'current': current_streak,
            'longest': longest_streak
        }
    
    def generate_metrics(self) -> Dict[str, Any]:
        """
        Gera todas as métricas de uma vez.
        
        Por quê um método único?
        - Evita chamar cada cálculo separadamente
        - Garante consistência nos dados
        - Facilita salvar tudo de uma vez
        
        Returns:
            Dicionário completo com todas as métricas
        """
        daily = self.calculate_daily_stats()
        weekly = self.calculate_weekly_stats()
        monthly = self.calculate_monthly_stats()
        languages = self.calculate_top_languages()
        streak = self.calculate_activity_streak()
        
        return {
            'last_update': datetime.now(timezone.utc).isoformat(),
            'total_commits': len(self.commits),
            'total_prs': len(self.prs),
            'total_issues': len(self.issues),
            'total_repos': len(self.repos),
            'daily_stats': daily,
            'weekly_stats': weekly,
            'monthly_stats': monthly,
            'top_languages': languages,
            'activity_streak': streak
        }
