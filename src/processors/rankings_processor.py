"""
Rankings Processor

Este módulo gera rankings dos projetos baseado em diferentes critérios.

Por quê rankings são úteis?
- Destacam projetos mais importantes
- Ajudam a priorizar no README
- Mostram evolução dos projetos
"""

from datetime import datetime, timezone
from typing import Dict, List, Any
from collections import defaultdict


class RankingsProcessor:
    """
    Gera rankings de projetos baseado em várias métricas.
    """
    
    def __init__(self, repos: List[Dict], commits: List[Dict], 
                 prs: List[Dict], issues: List[Dict]):
        """
        Inicializa com dados brutos.
        """
        self.repos = repos
        self.commits = commits
        self.prs = prs
        self.issues = issues
    
    def rank_by_activity(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Ranqueia projetos por atividade total.
        
        Atividade = commits + PRs + issues
        
        Por quê somar tudo?
        - Captura envolvimento geral no projeto
        - Projetos ativos têm mais movimento
        - Útil para mostrar "projetos principais"
        
        Args:
            limit: Quantos projetos retornar
            
        Returns:
            Lista ordenada de projetos com score de atividade
        """
        activity_scores = defaultdict(lambda: {'commits': 0, 'prs': 0, 'issues': 0})
        
        # Conta commits por repo
        for commit in self.commits:
            activity_scores[commit['repo']]['commits'] += 1
        
        # Conta PRs por repo
        for pr in self.prs:
            activity_scores[pr['repo']]['prs'] += 1
        
        # Conta issues por repo
        for issue in self.issues:
            activity_scores[issue['repo']]['issues'] += 1
        
        # Calcula score total e monta lista
        ranked = []
        for repo in self.repos:
            name = repo['name']
            scores = activity_scores[name]
            total_score = scores['commits'] + scores['prs'] + scores['issues']
            
            if total_score > 0:  # Só inclui repos com atividade
                ranked.append({
                    'name': name,
                    'full_name': repo['full_name'],
                    'html_url': repo.get('html_url', ''),
                    'language': repo['language'],
                    'score': total_score,
                    'breakdown': scores,
                    'stars': repo['stars'],
                    'private': repo['private']
                })
        
        # Ordena por score (maior primeiro)
        ranked.sort(key=lambda x: x['score'], reverse=True)
        
        return ranked[:limit]
    
    def rank_by_stars(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Ranqueia projetos por número de estrelas.
        
        Por quê stars importam?
        - Indicam popularidade
        - Mostram reconhecimento da comunidade
        - Útil para destacar projetos públicos de sucesso
        """
        # Filtra apenas repos com stars
        starred = [
            {
                'name': repo['name'],
                'full_name': repo['full_name'],
                'language': repo['language'],
                'stars': repo['stars'],
                'forks': repo['forks'],
                'description': repo['description']
            }
            for repo in self.repos
            if repo['stars'] > 0
        ]
        
        # Ordena por stars
        starred.sort(key=lambda x: x['stars'], reverse=True)
        
        return starred[:limit]
    
    def rank_by_recent_activity(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Ranqueia por atividade recente (último push).
        
        Por quê atividade recente?
        - Mostra projetos atualmente em desenvolvimento
        - Útil para seção "Trabalhando em..."
        - Indica projetos não abandonados
        """
        recent = []
        
        for repo in self.repos:
            if repo['pushed_at']:
                pushed = datetime.fromisoformat(repo['pushed_at'])
                now = datetime.now(timezone.utc)
                # Remove timezone info de ambos para comparação
                if pushed.tzinfo is not None:
                    pushed_naive = pushed.replace(tzinfo=None)
                    now_naive = now.replace(tzinfo=None)
                else:
                    pushed_naive = pushed
                    now_naive = now.replace(tzinfo=None)
                    
                recent.append({
                    'name': repo['name'],
                    'full_name': repo['full_name'],
                    'language': repo['language'],
                    'last_push': repo['pushed_at'],
                    'days_ago': (now_naive - pushed_naive).days,
                    'private': repo['private']
                })
        
        # Ordena por data mais recente
        recent.sort(key=lambda x: x['last_push'], reverse=True)
        
        return recent[:limit]
    
    def rank_by_commits(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Ranqueia projetos apenas por número de commits.
        
        Por quê apenas commits?
        - Mostra onde você mais codifica
        - Indica projetos com mais desenvolvimento ativo
        - Complementa outros rankings
        """
        commits_by_repo = defaultdict(int)
        
        for commit in self.commits:
            commits_by_repo[commit['repo']] += 1
        
        ranked = []
        for repo in self.repos:
            count = commits_by_repo[repo['name']]
            if count > 0:
                ranked.append({
                    'name': repo['name'],
                    'full_name': repo['full_name'],
                    'language': repo['language'],
                    'commits': count,
                    'private': repo['private']
                })
        
        ranked.sort(key=lambda x: x['commits'], reverse=True)
        
        return ranked[:limit]
    
    def rank_by_language(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Agrupa e ranqueia projetos por linguagem.
        
        Por quê por linguagem?
        - Organiza portfolio por tecnologia
        - Útil para mostrar expertise específica
        - Facilita encontrar projetos de uma stack
        
        Returns:
            Dicionário {linguagem: [projetos ranqueados]}
        """
        by_language = defaultdict(list)
        
        # Calcula atividade de cada projeto
        activity_scores = defaultdict(int)
        for commit in self.commits:
            activity_scores[commit['repo']] += 1
        for pr in self.prs:
            activity_scores[pr['repo']] += 1
        for issue in self.issues:
            activity_scores[issue['repo']] += 1
        
        # Agrupa por linguagem
        for repo in self.repos:
            lang = repo['language']
            if lang:  # Ignora repos sem linguagem
                by_language[lang].append({
                    'name': repo['name'],
                    'full_name': repo['full_name'],
                    'stars': repo['stars'],
                    'activity': activity_scores[repo['name']],
                    'private': repo['private']
                })
        
        # Ordena projetos dentro de cada linguagem por atividade
        for lang in by_language:
            by_language[lang].sort(key=lambda x: x['activity'], reverse=True)
        
        return dict(by_language)
    
    def generate_rankings(self) -> Dict[str, Any]:
        """
        Gera todos os rankings de uma vez.
        
        Por quê múltiplos rankings?
        - Diferentes perspectivas dos projetos
        - Flexibilidade no README (escolher qual mostrar)
        - Dados para análises futuras
        
        Returns:
            Dicionário com todos os rankings
        """
        return {
            'last_update': datetime.now(timezone.utc).isoformat(),
            'top_projects': self.rank_by_activity(limit=10),
            'most_active': self.rank_by_commits(limit=10),
            'most_stars': self.rank_by_stars(limit=10),
            'most_recent': self.rank_by_recent_activity(limit=10),
            'by_language': self.rank_by_language()
        }
