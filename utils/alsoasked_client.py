import requests

class AlsoAskedClient:
    """A client for the v1 AlsoAsked API."""
    API_URL = "https://alsoaskedapi.com/v1/search"

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API key cannot be empty.")
        self._api_key = api_key
        self._session = requests.Session()
        self._session.headers.update({
            'X-Api-Key': self._api_key,
            'Content-Type': 'application/json'
        })

    def get_questions_for_keyword(self, keyword: str, region: str = 'us', language: str = 'en') -> list:
        """Fetches questions for a single keyword."""
        payload = {
            'terms': [keyword],
            'language': language,
            'region': region,
            'depth': 2,
            'async': False
        }
        try:
            response = self._session.post(self.API_URL, json=payload, timeout=90)
            response.raise_for_status()
            data = response.json()
            
            query_results = data.get('queries', [{}])[0].get('results')
            if not query_results:
                return []
            
            return self._extract_questions(query_results)
        except requests.RequestException as e:
            return [f"API Request Error: {e}"]
        except (KeyError, IndexError):
            return ["API Error: Invalid response structure"]

    def _extract_questions(self, results_list: list) -> list:
        """Recursively extracts questions from the results."""
        all_questions = []
        for item in results_list:
            if item.get('question'):
                all_questions.append(item['question'])
            if item.get('results'):
                all_questions.extend(self._extract_questions(item['results']))
        return all_questions
