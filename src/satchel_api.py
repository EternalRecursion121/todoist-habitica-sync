import requests
import time

class SatchelAPI:
    def __init__(self, client_id: str, client_secret: str, username: str, password: str, school_id: str, student_id: str) -> None:
        self._session = requests.Session()
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self.school_id = school_id
        self.student_id = student_id
        # Initialize tokens
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = None

    def authenticate(self):
        """Authenticate with the Satchel API and obtain access tokens."""
        url = 'https://api.satchelone.com/oauth/token'
        headers = {
            'Content-Type': 'multipart/form-data',
            'User-Agent': 'python-requests'
        }
        data = {
            'grant_type': 'password',
            'username': self.username,
            'password': self.password,
            'school_id': self.school_id,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        response = self._session.post(url, files=data, headers=headers)
        if response.status_code == 200:
            tokens = response.json()
            self.access_token = tokens.get('access_token')
            self.refresh_token = tokens.get('refresh_token')
            self.token_expiry = time.time() + tokens.get('expires_in')
        else:
            raise Exception(f"Authentication failed: {response.status_code} - {response.text}")
    
    def refresh_access_token(self):
        """Refresh the access token using the refresh token."""
        url = 'https://api.satchelone.com/oauth/token'
        headers = {
            'Content-Type': 'multipart/form-data',
            'User-Agent': 'python-requests'
        }
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        response = self._session.post(url, files=data, headers=headers)
        if response.status_code == 200:
            tokens = response.json()
            self.access_token = tokens.get('access_token')
            self.refresh_token = tokens.get('refresh_token')  # Update refresh token if a new one is provided
        else:
            raise Exception(f"Failed to refresh token: {response.status_code} - {response.text}")
        
    def ensure_active_token(self):
        """Ensure the access token is valid, refreshing it if expired."""
        if time.time() > self.token_expiry - 300: # Subtracting 5 minutes as a buffer
            self.refresh_access_token()

    def get_todos(self, from_date: str, to_date: str):
        """Retrieve todos for a given date range."""
        self.ensure
        url = f'https://api.satchelone.com/api/todos?add_dateless=true&from={from_date}&to={to_date}'
        headers = {
            'Accept': 'application/smhw.v2021.5+json',
            'Authorization': f'Bearer {self.access_token}'
        }
        
        response = self._session.get(url, headers=headers)
        if response.status_code == 200:
            todos = response.json().get('todos', [])
            return todos
        else:
            raise Exception(f"Failed to retrieve todos: {response.status_code} - {response.text}")
        
    def get_timetable(self, request_date: str):
        """Get the timetable for a specified date."""
        url = f'https://api.satchelone.com/api/timetable/school/{self.school_id}/student/{self.student_id}?requestDate={request_date}'
        headers = {
            'Accept': 'application/smhw.v2021.5+json',
            'Authorization': f'Bearer {self.access_token}'
        }
        response = self._session.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to retrieve timetable: {response.status_code} - {response.text}")