#!/bin/bash

export_env_variables() {
    if [ ! -f ".env" ]; then
        echo "Файл .env не найден."
        exit 1
    fi

    while IFS='=' read -r key value
    do
        if [[ ! -z $key && ! -z $value && $key != \#* ]]; then
            export $key="$value"
        fi
    done < ".env"
    echo "Все переменные окружения из .env экспортированы."
}

set_env_variable() {
    local var_name=$1
    local var_value=$2

    if grep -q "^${var_name}=" ".env"; then
        sed -i '' "s/^${var_name}=.*/${var_name}=${var_value}/" ".env"
    else
        echo "${var_name}=${var_value}" >> ".env"
    fi

    export $var_name="$var_value"
}

check_postgres() {
    if ! pg_isready -q; then
        echo "PostgreSQL не запущен. Запустите PostgreSQL перед запуском проекта."
        exit 1
    else
        echo "PostgreSQL запущен и готов к использованию."
    fi
}

run_poetry() {
    echo "Запускаем проект локально с помощью Poetry..."

    if ! command -v poetry &> /dev/null; then
        echo "Poetry не установлен. Установите Poetry перед запуском этого скрипта."
        exit 1
    fi

    check_postgres

    set_env_variable "DB_HOST" "localhost"

    export_env_variables

    poetry install
    poetry run python fin_analyse_bot/main.py
}

run_docker() {
    echo "Запускаем проект с помощью Docker..."

    if ! command -v docker &> /dev/null || ! command -v docker-compose &> /dev/null; then
        echo "Docker или Docker Compose не установлены. Установите Docker и Docker Compose перед запуском этого скрипта."
        exit 1
    fi

    set_env_variable "DB_HOST" "database"

    docker-compose up --build
}

env_file=".env"

update_env_file() {
    local var_name=$1
    local current_value=$(grep "^${var_name}=" "$env_file" | cut -d '=' -f2)

    if [ -z "$current_value" ]; then
        if [ -z "${!var_name}" ]; then
            read -p "Введите значение для ${var_name}: " current_value
            export $var_name="$current_value"
        else
            current_value="${!var_name}"
        fi

        echo "${var_name}=${current_value}" >> "$env_file"
    else
        export $var_name="$current_value"
    fi
}
declare -a vars=("BOT_TOKEN" "USER_ID")

for var in "${vars[@]}"; do
    update_env_file "$var"
done

if [ "$1" == "docker" ]; then
    run_docker
elif [ "$1" == "poetry" ]; then
    run_poetry
else
    echo "Неправильный параметр. Используйте 'docker' или 'poetry' для запуска."
    exit 1
fi

