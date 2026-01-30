#!/usr/bin/env python3
"""
Daily Metrics Collection Script

Coleta dados reais do GitHub e atualiza os arquivos JSON:
- data/metrics.json - Métricas atuais
- data/history.json - Histórico mensal
- data/daily_activity.json - Atividade diária
- data/projects.json - Projetos destacados

Uso:
    python3 src/scripts/daily_metrics.py

Requer:
    - GITHUB_TOKEN no ambiente ou arquivo .env
    - PyGithub instalado (pip install PyGithub python-dotenv)
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List
from collections import defaultdict

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from src.collectors.github_collector import GitHubCollector
except ImportError:
    print("❌ Erro: Não foi possível importar GitHubCollector")
    print("   Verifique se o arquivo src/collectors/github_collector.py existe")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv não instalado, usando apenas variáveis de ambiente do sistema")


def get_github_token() -> str:
    """Obtém o token do GitHub das variáveis de ambiente."""
    token = os.getenv('GH_TOKEN')
    
    if not token:
        print("❌ Erro: GH_TOKEN não encontrado!")
        print("\n💡 Como configurar:")
        print("   1. Crie um token em: https://github.com/settings/tokens")
        print("   2. Configure no repositório: Settings → Secrets → GH_TOKEN")
        print("   3. Para teste local:")
        print("      export GH_TOKEN='seu_token_aqui'")
        sys.exit(1)
    
    return token


def calculate_activity_streak(commits_by_date: Dict[str, int]) -> Dict[str, int]:
    """Calcula streak de atividade (dias consecutivos com commits)."""
    if not commits_by_date:
        return {'current': 0, 'longest': 0}
    
    # Ordenar datas
    sorted_dates = sorted(commits_by_date.keys(), reverse=True)
    
    current_streak = 0
    longest_streak = 0
    temp_streak = 0
    
    # Verificar streak atual (contando de hoje para trás)
    today = datetime.now().date()
    check_date = today
    
    for i in range(365):  # Checar último ano
        date_str = check_date.strftime('%Y-%m-%d')
        
        if date_str in commits_by_date and commits_by_date[date_str] > 0:
            if current_streak == temp_streak:  # Ainda no streak atual
                current_streak += 1
            temp_streak += 1
            longest_streak = max(longest_streak, temp_streak)
        else:
            if current_streak == temp_streak:  # Quebrou o streak atual
                temp_streak = 0
            else:
                temp_streak = 0
        
        check_date -= timedelta(days=1)
    
    return {'current': current_streak, 'longest': longest_streak}


def collect_metrics(collector: GitHubCollector) -> Dict[str, Any]:
    """Coleta todas as métricas necessárias do GitHub."""
    print("📊 Coletando métricas do GitHub...")
    
    # Informações do perfil
    print("   → Informações do perfil...")
    profile = collector.collect_profile_info()
    
    # Repositórios
    print("   → Repositórios...")
    repos = collector.collect_all_repos()
    
    # Coletar commits de TODOS os tempos (não só 30 dias) para métricas gerais
    print("   → Commits (total histórico)...")
    all_commits = []
    
    # Para métricas, coletar commits dos últimos 6 meses para ter um número realista
    since_6_months = datetime.now(timezone.utc) - timedelta(days=180)
    commits_recent = collector.collect_commits(since=since_6_months)
    
    print(f"      ✓ {len(commits_recent)} commits nos últimos 6 meses")
    
    # Pull Requests (últimos 6 meses)
    print("   → Pull Requests...")
    prs = collector.collect_pull_requests(since=since_6_months)
    print(f"      ✓ {len(prs)} PRs encontrados")
    
    # Issues (últimos 6 meses)
    print("   → Issues...")
    issues = collector.collect_issues(since=since_6_months)
    print(f"      ✓ {len(issues)} issues encontrados")
    
    # Processar commits por dia para calcular streak
    commits_by_date = defaultdict(int)
    for commit in commits_recent:
        date = commit['date'][:10]  # YYYY-MM-DD
        commits_by_date[date] += 1
    
    # Calcular streak
    print("   → Calculando streak...")
    streak = calculate_activity_streak(commits_by_date)
    
    # Linguagens - coletar de TODOS os repositórios com detalhes
    print("   → Analisando linguagens...")
    languages = {}
    language_bytes = {}
    
    for repo in repos:
        try:
            # Obter o objeto repositório para acessar linguagens detalhadas
            repo_obj = collector.github.get_repo(repo['full_name'])
            
            # get_languages() retorna dict com {linguagem: bytes}
            repo_languages = repo_obj.get_languages()
            
            for lang, bytes_count in repo_languages.items():
                languages[lang] = languages.get(lang, 0) + 1
                language_bytes[lang] = language_bytes.get(lang, 0) + bytes_count
                
        except Exception as e:
            # Fallback para o método anterior
            lang = repo.get('language')
            if lang:
                languages[lang] = languages.get(lang, 0) + 1
                language_bytes[lang] = language_bytes.get(lang, 0) + repo.get('size', 0) * 1024
    
    # Ordenar linguagens por bytes (uso real)
    top_languages = dict(sorted(
        languages.items(), 
        key=lambda x: language_bytes.get(x[0], 0), 
        reverse=True
    )[:12])
    
    print(f"      ✓ {len(languages)} linguagens detectadas")
    for lang, count in list(top_languages.items())[:5]:
        print(f"         - {lang}: {count} repos ({language_bytes.get(lang, 0) / 1024 / 1024:.1f} MB)")
    
    # Total de stars e forks recebidos
    total_stars = sum(r.get('stars', 0) for r in repos)
    total_forks = sum(r.get('forks', 0) for r in repos)
    
    print(f"   → Stars totais: {total_stars}")
    print(f"   → Forks totais: {total_forks}")
    
    # Colaboradores únicos - tentar coletar de forma mais precisa
    all_contributors = set()
    for repo in repos[:10]:  # Limitar a 10 repos para não estourar rate limit
        try:
            repo_obj = collector.github.get_repo(repo['full_name'])
            contributors = list(repo_obj.get_contributors())
            for contrib in contributors:
                all_contributors.add(contrib.login)
        except:
            pass
    
    contributors_count = max(1, len(all_contributors))
    print(f"   → Contributors únicos: {contributors_count}")
    
    # Montar métricas
    metrics = {
        'username': profile['login'],
        'name': profile['name'] or profile['login'],
        'total_commits': len(commits_recent),
        'total_repos': len(repos),
        'total_prs': len(prs),
        'total_issues': len(issues),
        'total_stars': total_stars,
        'total_forks': total_forks,
        'contributors': contributors_count,
        'activity_streak': streak,
        'languages': top_languages,
        'language_bytes': language_bytes,
        'last_updated': datetime.now().isoformat()
    }
    
    return metrics


def collect_daily_activity(collector: GitHubCollector) -> Dict[str, Any]:
    """Coleta atividade diária de todo o mês atual."""
    print("📅 Coletando atividade diária...")
    
    # Coletar do primeiro dia do mês atual até agora
    now = datetime.now(timezone.utc)
    first_day_of_month = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
    
    print(f"   → Período: {first_day_of_month.date()} até {now.date()}")
    
    # Coletar dados
    commits = collector.collect_commits(since=first_day_of_month, until=now)
    prs = collector.collect_pull_requests(since=first_day_of_month)
    issues = collector.collect_issues(since=first_day_of_month)
    
    print(f"   → Total coletado: {len(commits)} commits, {len(prs)} PRs, {len(issues)} issues")
    
    # Organizar por data
    activity_by_date = defaultdict(lambda: {'commits': 0, 'prs': 0, 'issues': 0, 'reviews': 0})
    
    # Contar commits por dia
    for commit in commits:
        date = commit['date'][:10]
        activity_by_date[date]['commits'] += 1
    
    # Contar PRs por dia de criação
    for pr in prs:
        date = pr['created_at'][:10]
        activity_by_date[date]['prs'] += 1
    
    # Contar issues por dia de criação
    for issue in issues:
        date = issue['created_at'][:10]
        activity_by_date[date]['issues'] += 1
    
    # Preencher todos os dias do mês (incluindo dias sem atividade)
    daily_stats = defaultdict(list)
    current_date = first_day_of_month.date()
    end_date = now.date()
    
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        month = date_str[:7]  # YYYY-MM
        
        stats = activity_by_date.get(date_str, {'commits': 0, 'prs': 0, 'issues': 0, 'reviews': 0})
        
        # Adicionar apenas se houver alguma atividade
        if stats['commits'] > 0 or stats['prs'] > 0 or stats['issues'] > 0:
            daily_stats[month].append({
                'date': date_str,
                'commits': stats['commits'],
                'prs': stats['prs'],
                'issues': stats['issues'],
                'reviews': stats['reviews']
            })
        
        current_date += timedelta(days=1)
    
    return {
        'daily_stats': dict(daily_stats),
        'metadata': {
            'last_updated': datetime.now().isoformat(),
            'days_collected': len(activity_by_date),
            'period_start': first_day_of_month.date().isoformat(),
            'period_end': now.date().isoformat()
        }
    }


def collect_featured_projects(collector: GitHubCollector) -> Dict[str, Any]:
    """Coleta os projetos mais relevantes com dados completos."""
    print("🚀 Coletando projetos destacados...")
    
    repos = collector.collect_all_repos()
    
    # Filtrar apenas repos públicos e ordenar por relevância
    public_repos = [r for r in repos if not r['private']]
    
    # Calcular score de relevância
    for repo in public_repos:
        score = (
            repo.get('stars', 0) * 3 +
            repo.get('forks', 0) * 2 +
            (1 if repo.get('language') else 0)
        )
        repo['_score'] = score
    
    # Top 6 projetos
    top_repos = sorted(public_repos, key=lambda r: r['_score'], reverse=True)[:6]
    
    # Formatar para o JSON de projetos com dados detalhados
    featured = []
    for repo in top_repos:
        print(f"   → Processando {repo['name']}...")
        
        # Coletar commits, PRs e contributors do repositório
        try:
            # Obter o objeto repositório
            repo_obj = collector.github.get_repo(repo['full_name'])
            
            # Contar commits do autor
            try:
                commits = list(repo_obj.get_commits(author=collector.user.login))
                commit_count = len(commits)
            except:
                commit_count = 0
            
            # Contar PRs
            try:
                prs = list(repo_obj.get_pulls(state='all'))
                pr_count = len([pr for pr in prs if pr.user.login == collector.user.login])
            except:
                pr_count = 0
            
            # Contar contributors
            try:
                contributors = list(repo_obj.get_contributors())
                contributor_count = len(contributors)
            except:
                contributor_count = 1
            
            # Obter topics (tags)
            try:
                topics = repo_obj.get_topics()
            except:
                topics = []
                
        except Exception as e:
            print(f"      ⚠️  Erro ao coletar detalhes: {e}")
            commit_count = 0
            pr_count = 0
            contributor_count = 1
            topics = []
        
        featured.append({
            'name': repo['name'],
            'description': repo.get('description', 'No description available'),
            'language': repo.get('language', 'Unknown'),
            'stars': repo.get('stars', 0),
            'forks': repo.get('forks', 0),
            'commits': commit_count,
            'prs': pr_count,
            'contributors': contributor_count,
            'created': repo['created_at'][:10],
            'last_updated': repo['updated_at'][:10],
            'topics': topics,
            'status': 'active' if repo.get('pushed_at') else 'archived',
            'url': repo['html_url']
        })
    
    return {
        'featured_projects': featured,
        'metadata': {
            'last_updated': datetime.now().isoformat(),
            'total_repos': len(public_repos)
        }
    }


def update_history(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Atualiza histórico mensal de métricas."""
    history_path = Path('data/history.json')
    
    # Carregar histórico existente
    if history_path.exists():
        with open(history_path, 'r') as f:
            history = json.load(f)
    else:
        history = {'monthly_snapshots': []}
    
    # Garantir que existe a estrutura correta
    if 'monthly_snapshots' not in history:
        history['monthly_snapshots'] = []
    
    # Criar snapshot do mês atual
    current_month = datetime.now().strftime('%Y-%m')
    
    # Para histórico, queremos métricas ACUMULADAS, não do período
    snapshot = {
        'month': current_month,
        'total_commits': metrics['total_commits'],
        'total_repos': metrics['total_repos'],
        'total_prs': metrics['total_prs'],
        'total_stars': metrics['total_stars'],
        'total_issues': metrics.get('total_issues', 0),
        'languages': metrics.get('languages', {}),
        'recorded_at': datetime.now().isoformat()
    }
    
    # Atualizar ou adicionar snapshot
    snapshots = history['monthly_snapshots']
    updated = False
    
    for i, snap in enumerate(snapshots):
        # Verificar se o snap tem a chave 'month'
        if isinstance(snap, dict) and 'month' in snap and snap['month'] == current_month:
            snapshots[i] = snapshot
            updated = True
            break
    
    if not updated:
        snapshots.append(snapshot)
    
    # Filtrar apenas snapshots válidos (que têm 'month')
    valid_snapshots = [s for s in snapshots if isinstance(s, dict) and 'month' in s]
    
    # Manter apenas últimos 12 meses
    history['monthly_snapshots'] = sorted(
        valid_snapshots,
        key=lambda s: s['month'],
        reverse=True
    )[:12]
    
    return history


def save_json(data: Dict[str, Any], filename: str):
    """Salva dados em arquivo JSON."""
    filepath = Path('data') / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"   ✓ {filename} salvo ({filepath.stat().st_size / 1024:.1f} KB)")


def main():
    print("🤖 " + "=" * 60)
    print("   GITHUB METRICS COLLECTION")
    print("   Collecting real data from GitHub API")
    print("=" * 62)
    print()
    
    # Obter token
    token = get_github_token()
    
    # Detectar username (múltiplas estratégias)
    username = None
    
    # Estratégia 1: Variável de ambiente explícita
    if os.getenv('GITHUB_USERNAME'):
        username = os.getenv('GITHUB_USERNAME')
        print(f"👤 Username detectado (GITHUB_USERNAME): {username}")
    
    # Estratégia 2: GitHub Actions - GITHUB_REPOSITORY_OWNER
    elif os.getenv('GITHUB_REPOSITORY_OWNER'):
        username = os.getenv('GITHUB_REPOSITORY_OWNER')
        print(f"👤 Username detectado (GITHUB_REPOSITORY_OWNER): {username}")
    
    # Estratégia 3: GitHub Actions - GITHUB_ACTOR
    elif os.getenv('GITHUB_ACTOR'):
        username = os.getenv('GITHUB_ACTOR')
        print(f"👤 Username detectado (GITHUB_ACTOR): {username}")
    
    # Estratégia 4: Extrair do GITHUB_REPOSITORY (formato: owner/repo)
    elif os.getenv('GITHUB_REPOSITORY'):
        repo_full = os.getenv('GITHUB_REPOSITORY')
        username = repo_full.split('/')[0]
        print(f"👤 Username detectado (GITHUB_REPOSITORY): {username}")
    
    # Fallback: Tentar usuário autenticado (pode falhar com GH_TOKEN limitado)
    else:
        print("⚠️  Username não detectado, tentando usar usuário autenticado...")
        print("💡 Dica: Defina GITHUB_USERNAME='DannyahIA' nas variáveis de ambiente")
    
    # Inicializar coletor
    print("🔑 Autenticando no GitHub...")
    try:
        collector = GitHubCollector(token, username)
        print(f"   ✓ Autenticado como: {collector.user.login}")
        
        # Verificar rate limit
        rate_info = collector.get_rate_limit_info()
        remaining = rate_info['core']['remaining']
        print(f"   ✓ Rate limit: {remaining} requests restantes")
        print()
    except Exception as e:
        print(f"❌ Erro ao autenticar: {e}")
        sys.exit(1)
    
    try:
        # Coletar métricas principais
        metrics = collect_metrics(collector)
        save_json(metrics, 'metrics.json')
        
        # Coletar atividade diária
        daily_activity = collect_daily_activity(collector)
        save_json(daily_activity, 'daily_activity.json')
        
        # Coletar projetos destacados
        featured_projects = collect_featured_projects(collector)
        save_json(featured_projects, 'projects.json')
        
        # Atualizar histórico
        print("📊 Atualizando histórico...")
        history = update_history(metrics)
        save_json(history, 'history.json')
        
        print()
        print("=" * 62)
        print("✨ Coleta concluída com sucesso!")
        print()
        print("📁 Arquivos atualizados:")
        print("   ✓ data/metrics.json")
        print("   ✓ data/daily_activity.json")
        print("   ✓ data/projects.json")
        print("   ✓ data/history.json")
        print()
        print("🎯 Próximo passo:")
        print("   python3 src/scripts/generate_complete_dashboard.py")
        print("=" * 62)
        
    except Exception as e:
        print(f"\n❌ Erro durante a coleta: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
