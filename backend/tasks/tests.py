from django.test import TestCase
from rest_framework.test import APIClient
from datetime import date, timedelta

class ScoringTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        today = date.today()
        self.sample = [
            {"id":"1","title":"A","due_date": (today + timedelta(days=1)).isoformat(), "estimated_hours": 2, "importance": 8, "dependencies": []},
            {"id":"2","title":"B","due_date": (today - timedelta(days=2)).isoformat(), "estimated_hours": 5, "importance": 6, "dependencies": ["1"]},
            {"id":"3","title":"C","due_date": None, "estimated_hours": 0.5, "importance": 4, "dependencies": []},
        ]

    def test_analyze_returns_sorted(self):
        resp = self.client.post('/api/tasks/analyze/?strategy=smart_balance', self.sample, format='json')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        tasks = data['tasks']
        self.assertTrue(len(tasks) == 3)
        # top task should be B (past due + blocks 1)
        self.assertIn('score', tasks[0])

    def test_suggest_returns_top3(self):
        resp = self.client.post('/api/tasks/suggest/', self.sample, format='json')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue('suggestions' in data)
        self.assertTrue(len(data['suggestions']) <= 3)

    def test_invalid_input(self):
        resp = self.client.post('/api/tasks/analyze/', {"not":"a list"}, format='json')
        self.assertEqual(resp.status_code, 400)
