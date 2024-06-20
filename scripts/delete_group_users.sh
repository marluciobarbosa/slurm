#!/bin/bash

# Verifica se o script foi executado com privilégios de superusuário
if [ "$(id -u)" -ne 0 ]; then
    echo "Este script precisa ser executado como root."
    exit 1
fi

# Verifica se o nome do grupo foi fornecido como argumento
if [ -z "$1" ]; then
    echo "Uso: $0 nome_do_grupo"
    exit 1
fi

# Atribui o nome do grupo à variável GROUP
GROUP=$1

# Verifica se o grupo existe
if ! getent group "$GROUP" > /dev/null; then
    echo "Grupo '$GROUP' não existe."
    exit 1
fi

# Obtém a lista de todos os usuários do sistema
USERS=$(getent passwd | awk -F: '{print $1}')

# Remove cada usuário do grupo especificado
for USER in $USERS; do
    # Verifica se o usuário pertence ao grupo especificado
    if id -nG "$USER" | grep -qw "$GROUP"; then
        echo "Apagando usuário $USER do grupo $GROUP"
        userdel -r -f "$USER"
    fi
done

echo "Todos os usuários do grupo '$GROUP' foram removidos."