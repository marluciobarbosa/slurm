#!/bin/bash

# Verifica se o script foi executado com privilégios de superusuário
if [ "$(id -u)" -ne 0 ]; then
    echo "Este script precisa ser executado como root."
    exit 1
fi

# Verifica se o número de dias foi fornecido como argumento
if [ -z "$1" ]; then
    echo "Uso: $0 numero_de_dias"
    exit 1
fi

# Atribui o número de dias à variável DAYS
DAYS=$1

# Data atual em segundos desde Epoch
CURRENT_DATE=$(date +%s)

# Obtém a lista de todos os usuários e verifica se estão no grupo default
USERS=$(getent passwd | awk -F: '{print $1}')

for USER in $USERS; do
    if id -nG "$USER" | grep -qw "default"; then
        # Obtém a data de expiração da conta do usuário
        EXPIRATION_DATE=$(chage -l -i $USER | grep "Account expires" | awk -F: '{print $2}' | xargs)

        # Se a conta não tem data de expiração, pula para o próximo usuário
        if [ "$EXPIRATION_DATE" == "never" ]; then
            continue
        fi

        # Converte a data de expiração para segundos desde Epoch
        if ! EXPIRATION_DATE_EPOCH=$(date -d "$EXPIRATION_DATE" +%s 2>/dev/null); then
            echo "Data de expiração inválida para o usuário $USER: $EXPIRATION_DATE"
            continue
        fi

        # Calcula a diferença em dias entre a data atual e a data de expiração
        DIFF_DAYS=$(( (CURRENT_DATE - EXPIRATION_DATE_EPOCH) / (60*60*24) ))

        # Se a diferença em dias for maior que o número de dias fornecido, apaga o usuário
        if [ "$DIFF_DAYS" -gt "$DAYS" ]; then
            echo "Apagando usuário $USER (expirado há $DIFF_DAYS dias)"
            userdel -r -f $USER
        fi
    fi
done