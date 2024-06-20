#!/bin/bash

body="$2"
recipients="$3"

# Extrair Job ID, Name e Status do corpo da mensagem
job_id=$(echo "$body" | sed -n 's/.*Job_id=\([0-9]*\).*/\1/p')
name=$(echo "$body" | sed -n 's/.*Name=\([^ ]*\).*/\1/p')
status=$(echo "$body" | sed -n 's/.*Name=[^ ]* \([^,]*\).*/\1/p')

# Formatar o assunto
subject="Slurm Job ID: $job_id (Status: $status, Name: $name)"

# Obter os caminhos dos arquivos de saída e erro do SLURM
output_file="$(scontrol show job $job_id | grep -oP '(?<=StdOut=)\S+')"
error_file="$(scontrol show job $job_id | grep -oP '(?<=StdErr=)\S+')"

# Criar o corpo do email em HTML
email_body="<html><body>"
email_body+="<p>$body</p>"

# Tentar ler o arquivo de saída
output_content=$(sudo cat "$output_file" 2>/dev/null)
if [ -n "$output_content" ]; then
    email_body+="<h3>Conteúdo do arquivo de saída ($output_file):</h3>"
    email_body+="<pre>$output_content</pre>"
else
    email_body+="<p>Arquivo de saída ($output_file) não encontrado ou não legível.</p>"
fi

# Tentar ler o arquivo de erro
error_content=$(sudo cat "$error_file" 2>/dev/null)
if [ -n "$error_content" ]; then
    email_body+="<h3>Conteúdo do arquivo de erro ($error_file):</h3>"
    email_body+="<pre>$error_content</pre>"
else
    email_body+="<p>Arquivo de erro ($error_file) não encontrado ou não legível.</p>"
fi

email_body+="</body></html>"

# Enviar o e-mail usando ssmtp
(
    echo "Subject: $subject"
    echo "Content-Type: text/html"
    echo ""
    echo "$email_body"
) | /usr/sbin/ssmtp $recipients