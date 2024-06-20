#!/bin/bash

# Verifica se o script foi executado com privilégios de superusuário
if [ "$(id -u)" -ne 0 ]; then
    echo "Este script precisa ser executado como root."
    exit 1
fi

# Verifica se o nome do arquivo CSV foi fornecido como argumento
if [ -z "$1" ]; then
    echo "Uso: $0 caminho_do_arquivo_csv [nome_do_grupo]"
    exit 1
fi

CSV_FILE=$1
GROUP=${2:-default}

# Verifica se o arquivo CSV existe
if [ ! -f "$CSV_FILE" ]; then
    echo "Arquivo CSV não encontrado: $CSV_FILE"
    exit 1
fi

#! Habilitação de cotas
# Note que que cota precisará ser habilitada para o volume /storage
# Verifica se o comando setquota está disponível
# if ! command -v setquota &> /dev/null
# then
#     echo "Comando setquota não encontrado. Instalando..."
#     # Atualiza os repositórios e instala o pacote quota
#     sudo apt-get update
#     sudo apt-get install -y quota
# fi

# Função para criar o usuário e definir configurações
create_user() {
    local NAME=$1
    local ID=$2
    local EMAIL=$3
    local USERNAME=$4
    local MAXJOBS=$5
    local MAXSUBMITJOBS=$6
    local MAXWALL=$7
    local STORAGEQUOTA=$8
    local QUOTA=$9
    
    USERNAME=$(echo "$USERNAME" | tr '[:upper:]' '[:lower:]')
    
    # Gera uma senha aleatória de 12 caracteres
    PASSWORD=$(openssl rand -base64 12)
    
    # Verifica se o grupo especificado existe e cria se necessário
    if ! getent group "$GROUP" > /dev/null; then
        groupadd "$GROUP"
        echo "Grupo '$GROUP' criado."
    fi
    
    # Criando a pasta home para os usuários
    sudo mkdir -p /storage/home/
    
    # Cria o usuário com o diretório home especificado e adiciona ao grupo especificado
    useradd -m -d /storage/home/"$USERNAME" -s /bin/bash -g "$GROUP" "$USERNAME"
    
    # Define a senha para o usuário
    echo "$USERNAME:$PASSWORD" | chpasswd
    
    # Exige que o usuário mude a senha no primeiro login
    chage -d 0 "$USERNAME"
    
    # Define cotas na unidade de armazenamento
    # sudo setquota -u $USERNAME $STORAGEQUOTA $STORAGEQUOTA 0 0 /storage
    # sudo setquota -u $USERNAME $QUOTA $QUOTA 0 0 /
    
    # Configurações do SLURM para o usuário
    sacctmgr add user name=$USERNAME DefaultAccount=$GROUP MaxJobs=$MAXJOBS MaxSubmitJobs=$MAXSUBMITJOBS MaxWall=$MAXWALL
    
    # Exibe a senha gerada
    echo "Usuário '$USERNAME' foi criado com sucesso."
    echo "Senha temporária: $PASSWORD"
    echo "Grupo: $GROUP"
}

# Lê o arquivo CSV e cria usuários
while IFS=, read -r NAME ID EMAIL USERNAME MAXJOBS MAXSUBMITJOBS MAXWALL STORAGEQUOTA QUOTA; do
    # Ignora linhas de comentário
    if [[ "$NAME" == \#* ]]; then
        continue
    fi
    create_user "$NAME" "$ID" "$EMAIL" "$USERNAME" "$MAXJOBS" "$MAXSUBMITJOBS" "$MAXWALL" "$STORAGEQUOTA" "$QUOTA"
done < "$CSV_FILE"