from nuitka import Options

Options.create(
    main_module="job_generator",  # Módulo principal a ser compilado
    # standalone=True,              # Criar um executável independente
    onefile=True,                # Criar um arquivo de execução em vez de um pacote
    recurse_all=True,             # Recursivamente incluir todas as dependências
    include_package_data=True,    # Incluir dados de pacotes (por exemplo, arquivos XML)
    follow_imports=True,          # Seguir importações dinâmicas
    remove_output=True,           # Remover diretório de saída existente antes da compilação
)


# Options.create("job_generator.py")
