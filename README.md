# tg session verifier

### env ###

    COMPOSE_PROJECT_NAME - имя проекта

    TG_TOKEN - aiogram bot токен от BotFather

### devops ###

1. git clone репы
2. Прописать env\
   2.1. Получить токен от BotFather\
   2.2. При использовании прокси ставим USE_PROXY в 1 и вставляем txt файл с проксями, каждая на новой строчке\
3. docker compose up -d --build
4. пользуемся
