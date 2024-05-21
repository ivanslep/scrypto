from wsgiref.simple_server import make_server 
import json  
from datetime import datetime  
from pytz import timezone, all_timezones, utc  

def current_time_html(tz_name="GMT"): # Функция для получения текущего времени в заданной временной зоне и возвращения его в формате HTML.
    try:
        tz = timezone(tz_name) if tz_name else utc
        now = datetime.now(tz)
        return f"<html><body><h1>Current time in {tz_name}: {now.strftime('%Y-%m-%d %H:%M:%S')}</h1></body></html>"
    except Exception as e:
        return f"<html><body><h1>Error: {str(e)}</h1></body></html>" # Обрабатываем исключения и возвращаем сообщение об ошибке

def convert_time(data, target_tz): #Функция для конвертации времени из одной временной зоны в другую.
    try:
        date_str = data['date']  
        source_tz = timezone(data['tz'])  # Определяем исходную временную зону
        target_tz = timezone(target_tz)  # Определяем целевую временную зону
        source_time = datetime.strptime(date_str, '%m.%d.%Y %H:%M:%S')  # Парсим дату и время из строки
        source_time = source_tz.localize(source_time)  # Локализуем время в исходной временной зоне
        target_time = source_time.astimezone(target_tz)  # Переводим время в целевую временную зону
        return {'converted_time': target_time.strftime('%Y-%m-%d %H:%M:%S')}
    except Exception as e:
        return {'error': str(e)} # Обрабатываем исключения и возвращаем сообщение об ошибке
def date_diff(data): #Функция для вычисления разницы в секундах между двумя датами в разных временных зонах.
    try:
        first_date_str = data['first_date']  # Извлекаем и определяем даты из JSON-данных
        first_tz = timezone(data['first_tz']) 
        second_date_str = data['second_date']  
        second_tz = timezone(data['second_tz'])  
        first_date = first_tz.localize(datetime.strptime(first_date_str, '%m.%d.%Y %H:%M:%S')) # Парсим и локализуем  даты
        second_date = second_tz.localize(datetime.strptime(second_date_str, '%I:%M%p %Y-%m-%d'))       
        diff_seconds = (second_date - first_date).total_seconds()  # Вычисляем разницу в секундах между двумя датами
        return {'diff_seconds': diff_seconds}
    except Exception as e:
        return {'error': str(e)}  # Обрабатываем исключения и возвращаем сообщение об ошибке

def application(environ, start_response): #Основная функция WSGI-приложения, обрабатывающая входящие запросы.
    path = environ.get('PATH_INFO', '').lstrip('/')  # Получаем путь запроса
    method = environ['REQUEST_METHOD']  # Получаем метод запроса (GET или POST)   
    if method == 'GET' and (path in all_timezones or path == ''): # Обработка GET-запросов для получения текущего времени в указанной временной зоне
        tz_name = path if path else 'GMT'  # Если путь пустой, используем GMT
        response_body = current_time_html(tz_name)  # Генерируем HTML-ответ с текущим временем
        status = '200 OK'
        headers = [('Content-Type', 'text/html')] 
    elif method == 'POST' and path == 'api/v1/convert': # Обработка POST-запросов для конвертации времени
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
            request_body = environ['wsgi.input'].read(request_body_size)
            data = json.loads(request_body)  # Парсинг JSON-данных
            target_tz = data.get('target_tz')  # Получаем целевую временную зону из данных
            result = convert_time(data, target_tz)  # Конвертируем время
            response_body = json.dumps(result)  # Формируем JSON-ответ
            status = '200 OK'
            headers = [('Content-Type', 'application/json')]
        except Exception as e:  
            response_body = json.dumps({'error': str(e)}) # Обрабатываем ошибки и возвращаем сообщение об ошибке
            status = '400 Bad Request'
            headers = [('Content-Type', 'application/json')]
    elif method == 'POST' and path == 'api/v1/datediff': # Обработка POST-запросов для вычисления разницы между двумя датами
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
            request_body = environ['wsgi.input'].read(request_body_size)
            data = json.loads(request_body)  # Парсинг JSON-данных
            result = date_diff(data)  # Вычисляем разницу между датами
            response_body = json.dumps(result)  # Формируем JSON-ответ
            status = '200 OK'
            headers = [('Content-Type', 'application/json')]
        except Exception as e:           
            response_body = json.dumps({'error': str(e)})  # Обрабатываем ошибки и возвращаем сообщение об ошибке
            status = '400 Bad Request'
            headers = [('Content-Type', 'application/json')]
    else:  
        response_body = '<html><body><h1>404 Not Found</h1></body></html>' # Обработка запросов к несуществующим страницам
        status = '404 Not Found'
        headers = [('Content-Type', 'text/html')] 
    start_response(status, headers)
    return [response_body.encode('utf-8')]
if __name__ == '__main__':
    httpd = make_server('localhost', 8051, application)
    print("Serving on port 8051...")
    httpd.serve_forever()
