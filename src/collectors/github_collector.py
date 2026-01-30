"""
GitHub Data Collector

This module collects data from the GitHub API.
Why separate it into a module?
- Makes it easier to test in isolation
- Can be reused by different jobs
- Centralizes API access logic
"""

from github import Github
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any
import os


class GitHubCollector:
    """
    Collects data from GitHub using the PyGithub library.

    Why use PyGithub?
    - Abstracts away the complexity of the GitHub REST API
    - Manages authentication and rate limits automatically
    - Supports private repos when authenticated
    """
    
    def __init__(self, token: str, username: str = None):
        """
        Initializes the collector with an access token.
        
        Args:
            token: GitHub Personal Access Token
                   Why is a token needed?
                   - Access to private repos
                   - Higher rate limit (5000 req/hour vs 60/hour)
            username: GitHub username (optional, will try to get authenticated user if not provided)
        """
        self.github = Github(token)
        if username:
            self.user = self.github.get_user(username)
        else:
            self.user = self.github.get_user()
    
    def collect_all_repos(self) -> List[Dict[str, Any]]:
        """
        Collects information from ALL repositories (public + private).
        
        Returns:
            List of dictionaries with repository data
            
        Why return dict instead of objects?
        - Dicts are JSON serializable
        - Makes it easier to save and manipulate later
        """
        repos_data = []
        
        # NamedUser.get_repos() não aceita 'affiliation', apenas pega repos públicos do usuário
        # Para usuário específico, só conseguimos repos públicos
        for repo in self.user.get_repos():
            repos_data.append({
                'name': repo.name,
                'full_name': repo.full_name,
                'private': repo.private,
                'language': repo.language,
                'stars': repo.stargazers_count,
                'forks': repo.forks_count,
                'html_url': repo.html_url,
                'created_at': repo.created_at.isoformat(),
                'updated_at': repo.updated_at.isoformat(),
                'pushed_at': repo.pushed_at.isoformat() if repo.pushed_at else None,
                'size': repo.size,
                'open_issues': repo.open_issues_count,
                'description': repo.description
            })
        
        return repos_data
    
    def collect_commits(self, since: datetime = None, until: datetime = None) -> List[Dict[str, Any]]:
        """
        Collects commits from all repos within a time period.
        
        Args:
            since: Start date (default: 30 days ago)
            until: End date (default: now)
            
        Returns:
            List of commits with metadata
            
        Why filter by date?
        - Avoids processing old data unnecessarily
        - Optimizes API rate limit
        """
        if since is None:
            since = datetime.now(timezone.utc) - timedelta(days=30)
        elif since.tzinfo is None:
            since = since.replace(tzinfo=timezone.utc)
            
        if until is None:
            until = datetime.now(timezone.utc)
        elif until.tzinfo is None:
            until = until.replace(tzinfo=timezone.utc)
        
        commits_data = []
        
        for repo in self.user.get_repos():
            try:
                commits = repo.get_commits(author=self.user.login, since=since, until=until)
                
                for commit in commits:
                    commits_data.append({
                        'repo': repo.name,
                        'sha': commit.sha,
                        'message': commit.commit.message,
                        'date': commit.commit.author.date.isoformat(),
                        'additions': commit.stats.additions if commit.stats else 0,
                        'deletions': commit.stats.deletions if commit.stats else 0,
                        'total_changes': commit.stats.total if commit.stats else 0
                    })
            except Exception as e:
                print(f"   ⚠️  Erro em {repo.name}: {e}")
                continue
        
        return commits_data
    
    def collect_pull_requests(self, since: datetime = None) -> List[Dict[str, Any]]:
        if since is None:
            since = datetime.now(timezone.utc) - timedelta(days=30)
        elif since.tzinfo is None:
            since = since.replace(tzinfo=timezone.utc)
        
        prs_data = []
        
        for repo in self.user.get_repos():
            try:
                prs = repo.get_pulls(state='all', sort='updated', direction='desc')
                
                for pr in prs:
                    if pr.updated_at < since:
                        break
                    
                    prs_data.append({
                        'repo': repo.name,
                        'number': pr.number,
                        'title': pr.title,
                        'state': pr.state,
                        'created_at': pr.created_at.isoformat(),
                        'updated_at': pr.updated_at.isoformat(),
                        'merged_at': pr.merged_at.isoformat() if pr.merged_at else None,
                        'closed_at': pr.closed_at.isoformat() if pr.closed_at else None,
                        'user': pr.user.login,
                        'additions': pr.additions,
                        'deletions': pr.deletions,
                        'changed_files': pr.changed_files,
                        'comments': pr.comments
                    })
            except Exception as e:
                print(f"   ⚠️  Erro em {repo.name}: {e}")
                continue
        
        return prs_data
        
    def collect_issues(self, since: datetime = None) -> List[Dict[str, Any]]:
        """
        Collects Issues (problems/tasks) from repositories.
        
        Why are issues important?
        - Show task management
        - Indicate resolved problems
        - Reveal active project maintenance
        """
        if since is None:
            since = datetime.now(timezone.utc) - timedelta(days=30)
        elif since.tzinfo is None:
            since = since.replace(tzinfo=timezone.utc)
        
        issues_data = []
        
        for repo in self.user.get_repos():
            try:
                issues = repo.get_issues(state='all', since=since)
            
                for issue in issues:
                    # Pull requests also appear as issues, let's filter them out
                    if issue.pull_request is not None:
                        continue
                    
                    issues_data.append({
                        'repo': repo.name,
                        'number': issue.number,
                        'title': issue.title,
                        'state': issue.state,
                        'created_at': issue.created_at.isoformat(),
                        'updated_at': issue.updated_at.isoformat(),
                        'closed_at': issue.closed_at.isoformat() if issue.closed_at else None,
                        'comments': issue.comments,
                        'labels': [label.name for label in issue.labels]
                    })
            except Exception as e:
                print(f"   ⚠️  Erro em {repo.name}: {e}")
                continue
        
        return issues_data
    
    def collect_profile_info(self) -> Dict[str, Any]:
        """
        Collects profile information from GitHub.
        
        Returns:
            Dictionary with profile data
        """
        return {
            'login': self.user.login,
            'name': self.user.name,
            'bio': self.user.bio,
            'company': self.user.company,
            'location': self.user.location,
            'email': self.user.email,
            'blog': self.user.blog,
            'twitter': self.user.twitter_username,
            'followers': self.user.followers,
            'following': self.user.following,
            'public_repos': self.user.public_repos,
            'public_gists': self.user.public_gists,
            'avatar_url': self.user.avatar_url,
            'html_url': self.user.html_url,
            'created_at': self.user.created_at.isoformat(),
            'updated_at': self.user.updated_at.isoformat()
        }
    
    def collect_starred_repos(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Collects starred repositories.
        
        Args:
            limit: Maximum number of starred repos to collect
            
        Returns:
            List of starred repositories
        """
        starred_data = []
        
        try:
            for i, repo in enumerate(self.user.get_starred()):
                if i >= limit:
                    break
                    
                starred_data.append({
                    'name': repo.name,
                    'full_name': repo.full_name,
                    'description': repo.description,
                    'language': repo.language,
                    'stars': repo.stargazers_count,
                    'html_url': repo.html_url
                })
        except Exception as e:
            print(f"Error collecting starred repos: {e}")
        
        return starred_data
    
    def collect_contribution_stats(self) -> Dict[str, Any]:
        """
        Collects comprehensive contribution statistics.
        
        Returns:
            Dictionary with contribution stats
        """
        stats = {
            'total_repos': 0,
            'total_commits': 0,
            'total_prs': 0,
            'total_issues': 0,
            'total_stars_received': 0,
            'total_forks_received': 0,
            'languages': {},
            'repos_by_year': {}
        }
        
        try:
            for repo in self.user.get_repos():
                stats['total_repos'] += 1
                stats['total_stars_received'] += repo.stargazers_count
                stats['total_forks_received'] += repo.forks_count
                
                # Count language usage
                if repo.language:
                    stats['languages'][repo.language] = stats['languages'].get(repo.language, 0) + 1
                
                # Group by year
                year = repo.created_at.year
                stats['repos_by_year'][year] = stats['repos_by_year'].get(year, 0) + 1
                
                # Count commits (limited to avoid rate limit)
                try:
                    commits = list(repo.get_commits(author=self.user))
                    stats['total_commits'] += len(commits)
                except:
                    pass
        except Exception as e:
            print(f"Error collecting contribution stats: {e}")
        
        return stats
    def get_rate_limit_info(self) -> Dict[str, Any]:
        try:
            rate_limit = self.github.get_rate_limit()
            if hasattr(rate_limit, 'core'):
                return {
                    'core': {
                        'remaining': rate_limit.core.remaining,
                        'limit': rate_limit.core.limit,
                        'reset': rate_limit.core.reset.isoformat()
                    }
                }
            elif hasattr(rate_limit, 'rate'):
                return {
                    'core': {
                        'remaining': rate_limit.rate.remaining,
                        'limit': rate_limit.rate.limit,
                        'reset': rate_limit.rate.reset.isoformat() if rate_limit.rate.reset else 'N/A'
                    }
                }
            else:
                return {
                    'core': {
                        'remaining': 'N/A',
                        'limit': 'N/A',
                        'reset': 'N/A'
                    }
                }
        except Exception as e:
            print(f"⚠️  Could not verify rate limit: {e}")
            return {
                'core': {
                    'remaining': 'N/A',
                    'limit': 'N/A',
                    'reset': 'N/A'
                }
            }
