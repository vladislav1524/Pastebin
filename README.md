# Pastebin ✍️

## Описание проекта 📄:
Приложение со схожим с [Pastebin.com](https://pastebin.com/) функционалом. 
Пользователь может разместить свой текст с уникальной ссылкой и поделиться с другими. (Для ограничения доступа можно установить пароль). 
Также, если пользователь аутентифицирован, то он сможет изменить и удалить свой текст. При создании текста пользователь выбирает, через какое время он будет удалён. 

## Используемые технологии:
- **Redis**: Для кэширования текстов и в качестве брокера сообщений.
- **Celery**: Для асинхронной отправки писем по электронной почте.
- **Django-allauth и social-django**: Система аутентификации пользователей через сайт и социальные сети.
- **PostgreSQL**
- **Docker**
- **Bootstrap и css**
  
## Как запустить проект 🛠️:
1. Добавьте `localhost` или ваш домен Ngrok в параметр `ALLOWED_HOSTS` в файле `settings.py`.
2. Создайте файл `.env` с вашими переменными (добавьте его в директорию, на уровне `manage.py`).

Примерный вид вашего файла `.env` (без пробелов и кавычек):
```
SECRET_KEY=...
DATABASE_NAME=...
DATABASE_USER=...
DATABASE_PASSWORD=...
DATABASE_HOST=db
DATABASE_PORT=...
EMAIL_HOST_USER=...
EMAIL_HOST_PASSWORD=...
SOCIAL_AUTH_VK_OAUTH2_KEY=...
SOCIAL_AUTH_VK_OAUTH2_SECRET=...
SOCIAL_AUTH_VK_OAUTH2_REDIRECT_URI=...
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=...
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=...
SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URI=...
SOCIAL_AUTH_DISCORD_KEY=...
SOCIAL_AUTH_DISCORD_SECRET=...
SOCIAL_AUTH_DISCORD_REDIRECT_URI=...
DEBUG=False
ALLOWED_HOSTS=...
CSRF_TRUSTED_ORIGINS=...
```
3. Запустите в главной директории на уровне `manage.py`:
```bash
docker-compose up --build
```
Затем выполните миграции:
```bash
docker-compose exec web python manage.py migrate
```
Чтобы создать суперпользователя:

```bash
docker-compose exec web python manage.py createsuperuser
```
## Если хотите протестировать аутентификацию через социальные сети 🌐:
1. Установите Ngrok для использования вашего компьютера как сервера и публикации сайта с HTTPS [Ссылка на Ngrok](https://ngrok.com/)

2. В консоли Ngrok выполните:
```bash
ngrok http 8000
```
Либо получите бесплатный домен в личном кабинете и выполните:
```bash
ngrok http --hostname=<your host> 8000  
```
3. создайте и настройте приложения для входа через соц сети добавьте данные в .env:

*Vk*: https://dev.vk.com/ru

*discord*: https://discord.com/developers/applications

*google*: https://console.cloud.google.com/cloud-resource-manager

4. Добавьте ваш домен Ngrok в CSRF_TRUSTED_ORIGINS и ALLOWED_HOSTS и запустите контейнер.
```bash
docker-compose up --build
```
