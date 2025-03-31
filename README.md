Описание
Сервис для сокращения длинных URL-адресов, построенный на FastAPI, с функциями аналитики и управления ссылками.

Основные функции:
Создание, обновление и удаление коротких ссылок
Возможность задавать собственные алиасы (псевдонимы) для ссылок
Установка времени жизни ссылки (автоматическое удаление)
Статистика переходов по ссылке
Поиск по оригинальному URL
Фоновые задачи для очистки просроченных ссылок

API Endpoints:

Метод	Эндпоинт	Описание
POST	/links/shorten	Создание короткой ссылки
GET	/links/{short_code}	Перенаправление на оригинальный URL
GET	/links/{short_code}/stats	Получение статистики ссылки
DELETE	/links/{short_code}	Удаление короткой ссылки
PUT	/links/{short_code}	Обновление оригинального URL
GET	/links/search	Поиск ссылок по оригинальному URL

Технологии
Python 3.11
FastAPI
SQLAlchemy (PostgreSQL/SQLite)
Redis (кеширование)
Docker

Требования
Установленные Docker и Docker Compose