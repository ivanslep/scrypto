import unittest  
from datetime import datetime  
import json  
import io  
from app import application  

class WSGIAppTest(unittest.TestCase):
    
    def make_request(self, method, path, data=None): #Вспомогательная функция для выполнения запросов к WSGI-приложению.
        environ = {
            'REQUEST_METHOD': method,
            'PATH_INFO': path,
            'CONTENT_TYPE': 'application/json',
            'wsgi.input': None,
            'CONTENT_LENGTH': 0
        }
        
        if data: # Если данные есть, преобразуем их в JSON и помещаем в wsgi.input
       
            request_body = json.dumps(data).encode('utf-8')
            environ['wsgi.input'] = io.BytesIO(request_body)
            environ['CONTENT_LENGTH'] = len(request_body)
        
        response_body = []

        def start_response(status, headers):  # Коллбек для получения статуса и заголовков ответа
           
            self.status = status
            self.headers = headers

        response = application(environ, start_response)  # Выполняем запрос к приложению
        response_body = b''.join(response).decode('utf-8')  # Собираем и декодируем тело ответа
        return self.status, self.headers, response_body
    
    def test_get_current_time_gmt(self):
        """
        Тест для проверки получения текущего времени в GMT.
        """
        status, headers, response_body = self.make_request('GET', '/')
        self.assertEqual(status, '200 OK')
        self.assertIn('Current time in GMT', response_body)
    
    def test_convert_time(self):
        """
        Тест для проверки конвертации времени из одной временной зоны в другую.
        """
        data = {
            "date": "12.20.2021 22:21:05",
            "tz": "EST",
            "target_tz": "Europe/Moscow"
        }
        status, headers, response_body = self.make_request('POST', '/api/v1/convert', data)
        self.assertEqual(status, '200 OK')
        response = json.loads(response_body)
        self.assertIn('converted_time', response)
    
    def test_date_diff(self):
        """
        Тест для проверки вычисления разницы во времени между двумя датами в разных временных зонах.
        """
        data = {
            "first_date": "12.06.2024 22:21:05",
            "first_tz": "EST",
            "second_date": "12:30pm 2024-02-01",
            "second_tz": "Europe/Moscow"
        }
        status, headers, response_body = self.make_request('POST', '/api/v1/datediff', data)
        self.assertEqual(status, '200 OK')
        response = json.loads(response_body)
        self.assertIn('diff_seconds', response)

if __name__ == '__main__':
    unittest.main()
