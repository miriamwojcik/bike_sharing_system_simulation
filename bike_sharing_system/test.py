from django.test import TestCase

# if 'test' in sys.argv:
#     DATABASES['default'] = {'ENGINE': 'django.db.backends.sqlite3'}

class URLTest(TestCase):
    def test_simulation_page(self):
        response = self.client.get('/')
        self.assertEquals(response.status_code,200)