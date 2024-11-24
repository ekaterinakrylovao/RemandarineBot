# Telegram бот для напоминаний: RemandarineBot

## Описание проекта

Этот проект представляет собой Telegram-бота, который напоминает о событиях с заданной Вами периодичностью и высылает прикрепленные к ним файлы. 

### Некоторые возможности:
- Редактирование событий.
- Кнопки для вывода списка текущих и завершённых дел.
  - Завершённое дело можно вернуть в список текущих дел.
- Хранение файлов в **Google Drive**.

## Интеграция с Jenkins

Для автоматизации предоставлены все настройки для работы с Jenkins.

### Быстрый запуск Jenkins:
Используйте команду:
```bash
docker compose -f docker-compose-jenkins.yaml up -d
```
Это запустит Jenkins, который можно настроить под свои нужды.

### Некогда реализованные мной настройки:
1. Добавление вебхука для GitHub:
   - При коммите в ветку `main` репозитория с ботом вебхук отправляет сигнал Jenkins.
   - Jenkins Job скачивает файлы из репозитория, оборачивает бота в Docker-контейнер и запускает его локально.
   
2. Автоматический бэкап:
   - Ежедневная задача скачивает файлы из удалённого хранилища, создаёт дамп базы данных, архивирует, шифрует и отправляет обратно в хранилище.

3. Периодические напоминания:
   - Задача раз в указанное количество минут отправляет API-запрос к боту для рассылки уведомлений.

## Логирование

- Добавлен кастомный конфиг для формата логов.
- Реализовано логирование пользовательских действий (легко расширяется по аналогии).
  
### Мониторинг через Docker:
Для работы с логами используются **Promtail**, **Loki** и **Grafana**. 

#### Быстрый запуск:
```bash
docker compose up -d
```

#### Настройка Grafana:
1. Откройте Grafana в браузере по адресу [http://localhost:3000](http://localhost:3000).
2. Войдите с учётными данными: **admin / admin**.
3. Перейдите во вкладку **Configuration → Data Sources**.
4. Нажмите **Add data source**, выберите **Loki**.
5. Укажите URL: `http://loki:3100`, затем нажмите **Save & Test**.

#### Просмотр логов:
1. Перейдите на вкладку **Explore**.
2. Введите следующий Loki-запрос:
   ```logql
   {job="varlogs"} | json | level="INFO"
   ```

![Снимок экрана 2024-11-24 193702](https://github.com/user-attachments/assets/8b818623-1f58-49f0-96b9-d7d483825ab3)

## Запуск бота

Для запуска бота вместе с логированием используйте:
```bash
docker compose up -d
```
