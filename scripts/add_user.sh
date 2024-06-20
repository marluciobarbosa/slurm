#!/bin/bash

# Verifica se o script foi executado com privilégios de superusuário
if [ "$(id -u)" -ne 0 ]; then
    echo "Este script precisa ser executado como root."
    exit 1
fi

# Verifica se o nome do usuário foi fornecido como argumento
if [ -z "$1" ]; then
    echo "Uso: $0 nome_do_usuario [data_de_suspensao] [grupo]"
    echo "     data_de_suspensao deve ser fornecida no formato AAAA-MM-DD"
    echo "     grupo é opcional, o padrão é 'default'"
    exit 1
fi

# Atribui o nome do usuário à variável USERNAME
USERNAME=$1
# in case IDs are uppercase, convert to lowercase
USERNAME=$(echo "$USERNAME" | tr '[:upper:]' '[:lower:]')

# Verifica se a data de suspensão foi fornecida como argumento
SUSPENSION_DATE=$2

# Atribui o nome do grupo à variável GROUP ou usa 'default' como padrão
GROUP=${3:-default}

# Gera uma senha aleatória de 12 caracteres
PASSWORD=$(openssl rand -base64 12)

# Verifica se o grupo especificado existe e cria se necessário
if ! getent group "$GROUP" > /dev/null; then
    groupadd "$GROUP"
    echo "Grupo '$GROUP' criado."
fi

# Criando a pasta home para os usuarios
sudo mkdir -p /storage/home/

# Cria o usuário com o diretório home especificado e adiciona ao grupo especificado
useradd -m -d /storage/home/"$USERNAME" -s /bin/bash -g "$GROUP" "$USERNAME"

# Define a senha para o usuário
echo "$USERNAME:$PASSWORD" | chpasswd

# Exige que o usuário mude a senha no primeiro login
chage -d 0 "$USERNAME"

# Se uma data de suspensão foi fornecida, define a data de expiração da conta
if [ -n "$SUSPENSION_DATE" ]; then
    chage -E "$SUSPENSION_DATE" "$USERNAME"
    echo "A conta do usuário '$USERNAME' será suspensa em $SUSPENSION_DATE."
fi

# Definir cota na unidade de armazenamento
sudo setquota -u $USERNAME 150G 150G 0 0 /storage
sudo setquota -u $USERNAME 5G 5G 0 0 /

# Exibe a senha gerada
echo "Usuário '$USERNAME' foi criado com sucesso."
echo "Senha temporária: $PASSWORD"
echo "Grupo: $GROUP"