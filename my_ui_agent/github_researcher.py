"""
GitHub Research Module для поиска лучших алгоритмов UI анализа
Интеграция с GitHub MCP Server для исследования существующих решений
"""

import requests
import json
import os
from typing import List, Dict, Optional
from datetime import datetime
import time

try:
    from github_config import GITHUB_TOKEN, SEARCH_CONFIG, SEARCH_QUERIES
except ImportError:
    GITHUB_TOKEN = None
    SEARCH_CONFIG = {"max_results_per_query": 10, "min_stars": 3, "search_delay": 1}
    SEARCH_QUERIES = [
        "UI element detection computer vision language:python stars:>10",
        "GUI automation element detection screenshot stars:>5",
        "web scraping element detection python stars:>20"
    ]

class GitHubUIResearcher:
    """Исследователь GitHub репозиториев для UI анализа"""
    def __init__(self, token: Optional[str] = None):
        """
        Инициализация исследователя
        
        Args:
            token: GitHub Personal Access Token (опционально)
        """
        self.token = token or GITHUB_TOKEN or os.getenv('GITHUB_TOKEN')
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'UI-Agent-Research-Tool'
        }
        if self.token and self.token != "your_github_token_here":
            self.headers['Authorization'] = f'token {self.token}'
            print("✅ GitHub токен настроен")
        else:
            print("⚠️ GitHub токен не настроен. Будет использован ограниченный доступ.")
        
        self.base_url = 'https://api.github.com'
        self.search_history = []
        self.config = SEARCH_CONFIG
        
    def search_ui_analysis_repositories(self, max_results: int = 50) -> List[Dict]:
        """
        Поиск репозиториев с алгоритмами UI анализа
        
        Args:
            max_results: Максимальное количество результатов
            
        Returns:
            Список релевантных репозиториев
        """
        print("🔍 Начинаю поиск репозиториев для UI анализа...")
          # Используем поисковые запросы из конфигурации
        search_queries = SEARCH_QUERIES
        
        all_repos = []
        
        for i, query in enumerate(search_queries, 1):
            print(f"📊 Обрабатываю запрос {i}/{len(search_queries)}: {query[:50]}...")
            try:
                repos = self._search_repositories(query, per_page=self.config.get('max_results_per_query', 10))
                all_repos.extend(repos)
                
                # Добавляем задержку между запросами из конфигурации
                time.sleep(self.config.get('search_delay', 1))
                
            except Exception as e:
                print(f"⚠️ Ошибка при поиске '{query}': {e}")
                continue
        
        # Удаляем дубликаты и фильтруем
        unique_repos = self._remove_duplicates(all_repos)
        filtered_repos = self._filter_relevant_repos(unique_repos)
        
        # Сортируем по релевантности
        final_repos = self._rank_repositories(filtered_repos)[:max_results]
        
        print(f"✅ Найдено {len(final_repos)} релевантных репозиториев")
        return final_repos
    
    def _search_repositories(self, query: str, per_page: int = 10) -> List[Dict]:
        """Выполнение поискового запроса к GitHub API"""
        url = f"{self.base_url}/search/repositories"
        params = {
            'q': query,
            'sort': 'stars',
            'order': 'desc',
            'per_page': per_page
        }
        
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('items', [])
        elif response.status_code == 403:
            print("⚠️ Превышен лимит запросов GitHub API. Ожидание...")
            time.sleep(60)  # Ждем минуту
            return []
        else:
            response.raise_for_status()
    
    def _remove_duplicates(self, repos: List[Dict]) -> List[Dict]:
        """Удаление дубликатов по ID репозитория"""
        seen_ids = set()
        unique_repos = []
        
        for repo in repos:
            if repo['id'] not in seen_ids:
                seen_ids.add(repo['id'])
                unique_repos.append(repo)
        
        return unique_repos
    
    def _filter_relevant_repos(self, repos: List[Dict]) -> List[Dict]:
        """Фильтрация релевантных репозиториев"""
        relevant_repos = []
        
        # Ключевые слова для определения релевантности
        ui_keywords = [
            'ui', 'gui', 'interface', 'element', 'detection', 'automation',
            'screenshot', 'ocr', 'vision', 'computer', 'machine', 'learning',
            'selenium', 'playwright', 'opencv', 'testing', 'scraping',
            'annotation', 'bounding', 'box', 'recognition', 'analysis'
        ]
        
        for repo in repos:
            description = (repo.get('description') or '').lower()
            name = repo.get('name', '').lower()
            topics = [topic.lower() for topic in repo.get('topics', [])]
            
            # Проверяем наличие ключевых слов
            text_to_check = f"{description} {name} {' '.join(topics)}"
            keyword_count = sum(1 for keyword in ui_keywords if keyword in text_to_check)
            
            # Фильтруем по количеству ключевых слов и звезд
            if (keyword_count >= 2 and 
                repo.get('stargazers_count', 0) >= 3 and
                not repo.get('archived', False)):
                
                relevant_repos.append({
                    'id': repo['id'],
                    'name': repo['name'],
                    'full_name': repo['full_name'],
                    'description': repo.get('description', ''),
                    'html_url': repo['html_url'],
                    'stars': repo['stargazers_count'],
                    'forks': repo['forks_count'],
                    'language': repo.get('language', 'Unknown'),
                    'topics': repo.get('topics', []),
                    'updated_at': repo['updated_at'],
                    'created_at': repo['created_at'],
                    'relevance_score': keyword_count,
                    'size': repo.get('size', 0)
                })
        
        return relevant_repos
    
    def _rank_repositories(self, repos: List[Dict]) -> List[Dict]:
        """Ранжирование репозиториев по релевантности"""
        def calculate_score(repo):
            """Вычисление общего рейтинга репозитория"""
            stars_score = min(repo['stars'] / 100, 10)  # Максимум 10 баллов за звезды
            relevance_score = repo['relevance_score'] * 2  # 2 балла за каждое ключевое слово
            language_score = 3 if repo['language'] == 'Python' else 1  # Предпочтение Python
            freshness_score = self._calculate_freshness_score(repo['updated_at'])
            
            return stars_score + relevance_score + language_score + freshness_score
        
        # Добавляем общий рейтинг
        for repo in repos:
            repo['total_score'] = calculate_score(repo)
        
        # Сортируем по рейтингу
        return sorted(repos, key=lambda x: x['total_score'], reverse=True)
    
    def _calculate_freshness_score(self, updated_at: str) -> float:
        """Вычисление баллов за свежесть репозитория"""
        try:
            updated_date = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            now = datetime.now(updated_date.tzinfo)
            days_ago = (now - updated_date).days
            
            if days_ago < 30:
                return 3
            elif days_ago < 180:
                return 2
            elif days_ago < 365:
                return 1
            else:
                return 0
        except:
            return 0
    
    def get_repository_details(self, repo_name: str) -> Dict:
        """Получение детальной информации о репозитории"""
        url = f"{self.base_url}/repos/{repo_name}"
        
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()
    
    def get_repository_readme(self, repo_name: str) -> Optional[str]:
        """Получение README файла репозитория"""
        url = f"{self.base_url}/repos/{repo_name}/readme"
        
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            content = response.json()
            # Декодируем base64 контент
            import base64
            readme_content = base64.b64decode(content['content']).decode('utf-8')
            return readme_content
        else:
            return None
    
    def analyze_repository_code(self, repo_name: str, file_extensions: List[str] = None) -> Dict:
        """Анализ структуры кода репозитория"""
        if file_extensions is None:
            file_extensions = ['.py', '.js', '.cpp', '.java']
        
        url = f"{self.base_url}/repos/{repo_name}/contents"
        
        try:
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                contents = response.json()
                
                analysis = {
                    'total_files': 0,
                    'code_files': 0,
                    'directories': 0,
                    'file_types': {},
                    'key_files': []
                }
                
                for item in contents:
                    if item['type'] == 'file':
                        analysis['total_files'] += 1
                        
                        # Проверяем расширение файла
                        name = item['name'].lower()
                        for ext in file_extensions:
                            if name.endswith(ext):
                                analysis['code_files'] += 1
                                analysis['file_types'][ext] = analysis['file_types'].get(ext, 0) + 1
                                break
                        
                        # Ищем ключевые файлы
                        if any(keyword in name for keyword in 
                               ['detect', 'ui', 'element', 'vision', 'ocr', 'analysis']):
                            analysis['key_files'].append(item['name'])
                    
                    elif item['type'] == 'dir':
                        analysis['directories'] += 1
                
                return analysis
            
            else:
                return {'error': f'Failed to access repository: {response.status_code}'}
                
        except Exception as e:
            return {'error': str(e)}
    
    def save_research_results(self, repos: List[Dict], filename: str = None) -> str:
        """Сохранение результатов исследования"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"github_ui_research_{timestamp}.json"
        
        research_data = {
            'timestamp': datetime.now().isoformat(),
            'total_repositories': len(repos),
            'repositories': repos,
            'search_summary': {
                'top_languages': self._get_language_stats(repos),
                'average_stars': sum(r['stars'] for r in repos) / len(repos) if repos else 0,
                'most_recent': max(r['updated_at'] for r in repos) if repos else None
            }
        }
        
        filepath = os.path.join('learning_data', filename)
        os.makedirs('learning_data', exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(research_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Результаты исследования сохранены в {filepath}")
        return filepath
    
    def _get_language_stats(self, repos: List[Dict]) -> Dict[str, int]:
        """Статистика по языкам программирования"""
        languages = {}
        for repo in repos:
            lang = repo.get('language', 'Unknown')
            languages[lang] = languages.get(lang, 0) + 1
        
        return dict(sorted(languages.items(), key=lambda x: x[1], reverse=True))
    
    def print_research_summary(self, repos: List[Dict]):
        """Вывод сводки исследования"""
        if not repos:
            print("❌ Репозитории не найдены")
            return
        
        print(f"\n📊 СВОДКА ИССЛЕДОВАНИЯ GitHub")
        print("=" * 50)
        print(f"🔍 Найдено репозиториев: {len(repos)}")
        print(f"⭐ Средний рейтинг: {sum(r['stars'] for r in repos) / len(repos):.1f} звезд")
        
        # Топ языков
        languages = self._get_language_stats(repos)
        print(f"\n💻 Популярные языки:")
        for lang, count in list(languages.items())[:5]:
            print(f"   {lang}: {count} репозиториев")
        
        # Топ репозитории
        print(f"\n🏆 ТОП-10 РЕКОМЕНДУЕМЫХ РЕПОЗИТОРИЕВ:")
        print("-" * 50)
        
        for i, repo in enumerate(repos[:10], 1):
            print(f"{i:2d}. ⭐{repo['stars']:4d} | {repo['name']}")
            print(f"     📝 {repo['description'][:80]}...")
            print(f"     🔗 {repo['html_url']}")
            print(f"     💻 {repo['language']} | 🔄 {repo['updated_at'][:10]}")
            print()

def main():
    """Основная функция для тестирования"""
    print("🚀 Запуск GitHub исследователя UI анализа...")
    
    # Создаем исследователя
    researcher = GitHubUIResearcher()
    
    # Выполняем поиск
    repos = researcher.search_ui_analysis_repositories(max_results=30)
    
    # Выводим сводку
    researcher.print_research_summary(repos)
    
    # Сохраняем результаты
    researcher.save_research_results(repos)
    
    print("\n✅ Исследование завершено!")

if __name__ == "__main__":
    main()
