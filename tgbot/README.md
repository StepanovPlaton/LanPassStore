# Telegram Bot для магазина запчастей

Этот бот позволяет отслеживать заказы и управлять ими через Telegram.

## Структура проекта

```
tgbot/
├── bot.py                  # Точка входа, запуск polling + webhook сервера
├── config.py               # Настройки через pydantic-settings / .env
├── requirements.txt
├── .env
├── .env.example
├── Dockerfile
│
├── api/                    # Клиент к бэкенду
│   ├── __init__.py         # Экспорт OrderAPI
│   ├── client.py           # httpx AsyncClient + retry при 401
│   ├── auth.py             # JWTAuthManager
│   └── endpoints/
│       ├── __init__.py
│       ├── orders.py       # get_orders, get_order_by_id, update_status
│       └── products.py     # если нужно
│
├── handlers/               # Обработчики сообщений и callback'ов
│   ├── __init__.py         # Регистрация всех роутеров в dp
│   ├── start.py            # /start, помощь
│   ├── orders.py           # Просмотр заказов
│   └── status.py           # FSM смены статуса
│
├── keyboards/              # Только клавиатуры, никакой логики
│   ├── __init__.py
│   ├── reply.py            # ReplyKeyboardMarkup (главное меню)
│   └── inline.py           # InlineKeyboardMarkup (заказы, статусы)
│
├── states/                 # FSM состояния
│   ├── __init__.py
│   └── order_states.py     # OrderStates(StatesGroup)
│
├── middlewares/            # Middleware для dp
│   ├── __init__.py
│   └── auth.py             # Проверка, что юзер — админ
│
├── services/               # Бизнес-логика (между handlers и api)
│   ├── __init__.py
│   └── order_service.py    # Форматирование, фильтрация, уведомления
│
├── webhook/                # Входящие webhook'и от бэкенда
│   ├── __init__.py
│   └── server.py           # aiohttp сервер, валидация секрета
│
└── utils/
    ├── __init__.py
    └── formatters.py       # format_order, format_order_list
```

## Установка

1. Убедитесь, что у вас установлен Python 3.8+
2. Создайте виртуальное окружение:
```bash
cd tgbot
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate.bat  # Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

## Настройка

1. Скопируйте файл `.env.example` в `.env`:
```bash
cp .env.example .env
```

2. Отредактируйте `.env` файл:
```env
# Токен бота (получить у @BotFather)
BOT_TOKEN=your_bot_token_here

# ID чата для уведомлений (можно указать несколько через запятую)
CHAT_IDS=123456789,987654321

# Аутентификация через JWT
ADMIN_LOGIN=admin
ADMIN_PASSWORD=admin123

# Адрес backend API (по умолчанию)
API_HOST=localhost
API_PORT=8080

# Секрет для webhook
WEBHOOK_SECRET=your_webhook_secret_here
```

## Запуск

### Локально
```bash
cd tgbot
python bot.py
```

### Через Docker
```bash
cd tgbot
docker build -t tgbot .
docker run -it --env-file .env tgbot
```

## Команды бота

- `/start` - приветствие и список команд
- `/orders` - список всех заказов
- `/order <id>` - детали конкретного заказа

## Интеграция с frontend

Для отправки уведомлений о новых заказах из корзины, добавьте в frontend вызов webhook или используйте API бота напрямую:

```javascript
// Пример отправки уведомления
const response = await fetch('http://localhost:8080/api/orders', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer YOUR_ACCESS_TOKEN'
  },
  body: JSON.stringify({
    customer_name: 'Иван Иванов',
    customer_phone: '+79001234567',
    customer_email: 'email@example.com',
    comment: 'Комментарий к заказу',
    items: [
      {
        product_id: 1,
        quantity: 2
      }
    ]
  })
});
```

## Примечания

- Бот использует JWT авторизацию для аутентификации в backend
- Токен автоматически обновляется при истечении срока действия
- Статусы заказов: new, in_progress, done, cancelled
- Формат даты: ISO 8601
