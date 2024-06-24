import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import platform
import xml.etree.ElementTree as ET

class SLURMJobSubmitGUI:
    def __init__(self, xml_file):
        self.conda = False
        self.cuda = False

        # Ler as partições e os núcleos do arquivo XML
        self.particoes, self.nucleos = self.carregar_particoes_nucleos(xml_file)
        
        self.janela = tk.Tk()
        self.janela.title("SLURM Submit GUI")
        
        # Criar a barra de menu
        self.menu_bar = tk.Menu(self.janela)
        # Criar o menu Ajuda
        self.menu_ajuda = tk.Menu(self.menu_bar, tearoff=False)
        self.menu_ajuda.add_command(label="Ajuda", command=self.mostrar_ajuda)
        # Adicionar o menu Ajuda à barra de menu
        self.menu_bar.add_cascade(label="Ajuda", menu=self.menu_ajuda)
        # Definir a barra de menu como o menu da janela
        self.janela.config(menu=self.menu_bar)
        
        # Estilos
        estilo = ttk.Style()
        estilo.configure('TimeEntry.TEntry', padding=5, font=('Arial', 12), width=40)
        
        # Entrada do nome do trabalho
        self.label_nome_trabalho = ttk.Label(self.janela, text="Nome do Trabalho:")
        self.label_nome_trabalho.grid(row=0, column=0, padx=5, pady=5)
        self.entry_nome_trabalho = ttk.Entry(self.janela, width=40)
        self.entry_nome_trabalho.grid(row=0, column=1, padx=5, pady=5)
        
        # Seleção da partição
        self.label_particao = ttk.Label(self.janela, text="Partição:")
        self.label_particao.grid(row=1, column=0, padx=5, pady=5)
        self.opcao_particao = tk.StringVar()
        self.opcao_particao.set(self.particoes[0])
        self.menu_particao = ttk.OptionMenu(self.janela, self.opcao_particao, None, *self.particoes, command=self.atualizar_nucleos)
        self.menu_particao.config(width=40)
        self.menu_particao.grid(row=1, column=1, padx=5, pady=5)
        
        # Seleção do número de núcleos
        self.label_num_nucleos = ttk.Label(self.janela, text="Número de Núcleos:")
        self.label_num_nucleos.grid(row=2, column=0, padx=5, pady=5)
        self.opcao_num_nucleos = tk.StringVar()
        self.menu_num_nucleos = ttk.OptionMenu(self.janela, self.opcao_num_nucleos, '')  # Inicialização da variável
        self.menu_num_nucleos.grid(row=2, column=1, padx=5, pady=5)
        self.atualizar_nucleos(self.particoes[0])
        
        # Entrada de memória
        self.label_memoria = ttk.Label(self.janela, text="Memória (ex.: 1G):")
        self.label_memoria.grid(row=3, column=0, padx=5, pady=5)
        self.entry_memoria = ttk.Entry(self.janela, width=40)
        self.entry_memoria.insert(0,'1G')
        self.entry_memoria.grid(row=3, column=1, padx=5, pady=5)
        
        # Entrada de limite de tempo
        self.label_tempo = ttk.Label(self.janela, text="Limite de Tempo (ex.: 1-00:00:00):")
        self.label_tempo.grid(row=4, column=0, padx=5, pady=5)
        self.entry_tempo = ttk.Entry(self.janela, style='TimeEntry.TEntry', width=40)
        self.entry_tempo.insert(0, '0-01:30:00')
        self.entry_tempo.grid(row=4, column=1, padx=5, pady=5)

        # Botão de ajuda para o tempo
        self.botao_ajuda_tempo = ttk.Button(self.janela, text="?", command=self.mostrar_ajuda_tempo)
        self.botao_ajuda_tempo.grid(row=4, column=2, padx=5, pady=5)
        
        # Entrada do caminho do script
        self.label_script = ttk.Label(self.janela, text="Comando a Executar:")
        self.label_script.grid(row=5, column=0, padx=5, pady=5)
        self.entry_script = ttk.Entry(self.janela, width=40)
        self.entry_script.grid(row=5, column=1, padx=5, pady=5)
        
        # Entrada de e-mail para --mail-user
        self.label_email = ttk.Label(self.janela, text="E-mail para Notificação:")
        self.label_email.grid(row=6, column=0, padx=5, pady=5)
        self.entry_email = ttk.Entry(self.janela, width=40)
        self.entry_email.grid(row=6, column=1, padx=5, pady=5)
        
        # Checkbox - conda
        self.check_conda = ttk.Checkbutton(self.janela, text='Habilitar Ambiente Conda', command=self.toggle_conda)
        self.check_conda.grid(row=7, column=0, padx=5, pady=5)
        
        # Checkbox - CUDA
        self.check_cuda = ttk.Checkbutton(self.janela, text='Habilitar Ambiente NVIDIA HPC SDK', command=self.toggle_cuda)
        self.check_cuda.grid(row=7, column=1, padx=5, pady=5)
        
        # Opções do NVIDIA SDK
        self.label_arquitetura_nvidia_hpc_sdk = ttk.Label(self.janela, text="Versão do NVIDIA HPC SDK:")
        self.label_arquitetura_nvidia_hpc_sdk.grid(row=8, column=0, padx=5, pady=5)
        
        # Definir as arquiteturas suportadas pelo CUDA
        cuda_architectures = ["24.1"]
        
        self.opcao_arquitetura_nvidia_hpc_sdk = tk.StringVar()
        self.opcao_arquitetura_nvidia_hpc_sdk.set(cuda_architectures[0][1])
        self.menu_arquitetura_cuda = ttk.OptionMenu(self.janela, self.opcao_arquitetura_nvidia_hpc_sdk, *cuda_architectures)
        self.menu_arquitetura_cuda.grid(row=8, column=1, padx=5, pady=5)
        
        # Botão de enviar
        self.botao_enviar = ttk.Button(self.janela, text="Enviar", command=self.gerar_script)
        self.botao_enviar.grid(row=9, column=0, padx=5, pady=5)
        
        self.botao_mostrar_arquivo = ttk.Button(self.janela, text="Mostrar Arquivo", command=self.mostrar_conteudo_arquivo)
        self.botao_mostrar_arquivo.grid(column=1, row=9, padx=5, pady=5)
        
        self.botao_fechar = tk.Button(self.janela, text="Fechar", command=self.janela.destroy)
        self.botao_fechar.grid(column=2, row=9, padx=5, pady=5)
        
        self.janela.mainloop()

    def carregar_particoes_nucleos(self, xml_file):
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        particoes = []
        nucleos = {}
        
        for particao in root.findall('particao'):
            nome = particao.get('nome')
            min_nucleos = int(particao.find('min_nucleos').text)
            max_nucleos = int(particao.find('max_nucleos').text)
            particoes.append(nome)
            nucleos[nome] = list(range(min_nucleos, max_nucleos + 1))
        
        return particoes, nucleos

    def atualizar_nucleos(self, particao):
        nucleos = self.nucleos[particao]
        menu = self.menu_num_nucleos['menu']
        menu.delete(0, 'end')
        
        for num in nucleos:
            menu.add_command(label=str(num), command=lambda value=num: self.opcao_num_nucleos.set(str(value)))
        
        self.opcao_num_nucleos.set(str(nucleos[0]))

    def toggle_conda(self):
        self.conda = not self.conda

    def toggle_cuda(self):
        self.cuda = not self.cuda
        
    def mostrar_ajuda_tempo(self):
        # Definir a função para exibir informações de ajuda específicas para o campo Limite de Tempo
        mensagem = """O campo Limite de Tempo define o tempo máximo que o trabalho pode executar.
        Ele deve ser especificado no formato:
               dias-horas:minutos:segundos.
        
        Exemplos válidos:
        - 1-00:00:00 para um dia (24 horas)
        - 2-12:00:00 para dois dias e 12 horas
        - 0-01:30:00 para uma hora e 30 minutos
        
        Certifique-se de seguir este formato ao inserir o tempo limite do seu trabalho."""
        
        # Mostrar a mensagem de ajuda em uma caixa de diálogo
        messagebox.showinfo("Ajuda - Limite de Tempo", mensagem)

    def mostrar_conteudo_arquivo(self):
        """Abrir uma nova janela e mostrar o conteúdo de um arquivo."""

        # Criar uma nova janela
        janela_arquivo = tk.Toplevel(self.janela)
        janela_arquivo.title("Conteúdo do Arquivo")
        # Criar um widget de texto para exibir o conteúdo do arquivo
        texto = tk.Text(janela_arquivo, wrap="word")
        texto.pack(side="left", fill="both", expand=True)
        # Adicionar uma barra de rolagem
        barra_rolagem = tk.Scrollbar(janela_arquivo, command=texto.yview)
        barra_rolagem.pack(side="right", fill="y")
        texto.config(yscrollcommand=barra_rolagem.set)
        # Ler o conteúdo do arquivo e inseri-lo no widget de texto
        nome_trabalho = self.entry_nome_trabalho.get()        
        with open(f"{nome_trabalho}.sbatch", "r") as f:
            conteudo = f.read()
            texto.insert("1.0", conteudo)
        # Desabilitar o widget de texto para evitar edição
        texto.configure(state="disabled")

    def gerar_script(self):
        nome_trabalho = self.entry_nome_trabalho.get()
        particao = self.opcao_particao.get()
        num_nucleos = self.opcao_num_nucleos.get()
        memoria = self.entry_memoria.get()
        tempo = self.entry_tempo.get()
        script = self.entry_script.get()
        email = self.entry_email.get()     
        condaENV =  "/home/conda/.conda/envs/HPC_env"

        with open(f"{nome_trabalho}.sbatch", "w") as f:
            f.write("#!/bin/bash\n")
            f.write(f"#SBATCH --job-name={nome_trabalho}\n")
            f.write(f"#SBATCH --partition={particao}\n")
            f.write(f"#SBATCH --nodes=1\n")
            f.write(f"#SBATCH --ntasks-per-node={num_nucleos}\n")
            f.write(f"#SBATCH --mem={memoria}\n")
            f.write(f"#SBATCH --time={tempo}\n")
            f.write(f"#SBATCH --output={nome_trabalho}.out\n")
            f.write(f"#SBATCH --error={nome_trabalho}.err\n")
            if self.cuda:   
                f.write(f"#SBATCH --gres=gpu:1\n")
            f.write(f"#SBATCH --mail-user={email}\n")
            f.write(f"#SBATCH --mail-type=ALL\n\n")            
            if self.conda:
                # f.write("\nmodule load conda\n")                
                f.write(f"conda activate {condaENV}\n")            
            if self.cuda:   
                                
                # Para disponibilizar o NVIDIA HPC SDK
                sdk_version = self.opcao_arquitetura_nvidia_hpc_sdk.get()
                f.write("\n# Para disponibilizar o NVIDIA HPC SDK:\n")
                f.write(f"NVARCH=`uname -s`_`uname -m`; export NVARCH\n")
                f.write(f"NVCOMPILERS=/opt/nvidia/hpc_sdk; export NVCOMPILERS\n")
                f.write(f"MANPATH=$MANPATH:$NVCOMPILERS/$NVARCH/{sdk_version}/compilers/man; export MANPATH\n")
                f.write(f"PATH=$NVCOMPILERS/$NVARCH/{sdk_version}/compilers/bin:$PATH; export PATH\n")

                f.write(f"export PATH=$NVCOMPILERS/$NVARCH/{sdk_version}/comm_libs/mpi/bin:$PATH\n")
                f.write(f"export MANPATH=$MANPATH:$NVCOMPILERS/$NVARCH/{sdk_version}/comm_libs/mpi/man\n")
                          
            f.write(f"\nsrun mpirun -n {num_nucleos} {script}\n")        

        messagebox.showinfo("Sucesso", "Script gerado com sucesso!")    

    def mostrar_ajuda(self):
        """Exibir informações gerais de ajuda."""
        mensagem = """Este programa permite enviar trabalhos para um cluster SLURM utilizando uma interface gráfica.\n
        Você pode preencher os campos para especificar o nome do trabalho, partição, número de núcleos, memória, limite de tempo, comando a executar e e-mail para notificações.\n
        Opções adicionais incluem habilitar ambiente Conda e ambiente NVIDIA HPC SDK.\n
        Após preencher os campos necessários, clique em 'Enviar' para gerar o script SLURM (.sbatch).\n
        Para mais informações sobre os parâmetros:\n
        - Nome do Trabalho: Nome do trabalho a ser executado no cluster.\n
        - Partição: Partição do cluster onde o trabalho será executado.\n
        - Número de Núcleos: Número de núcleos de processamento a serem alocados para o trabalho.\n
        - Memória: Quantidade de memória a ser alocada para o trabalho (exemplo: 1G para 1 gigabyte).\n
        - Limite de Tempo: Tempo máximo de execução do trabalho (exemplo: 1-00:00:00 para 1 dia).\n
        - Comando a Executar: Comando ou script a ser executado no trabalho.\n
        - E-mail para Notificação: Endereço de e-mail para notificações sobre o trabalho.\n
        - Habilitar Ambiente Conda: Marque esta opção se o ambiente Conda for necessário para o trabalho.\n
        - Habilitar Ambiente NVIDIA HPC SDK: Marque esta opção se o ambiente NVIDIA HPC SDK for necessário para o trabalho.\n
        """
        messagebox.showinfo("Ajuda", mensagem)


if __name__ == "__main__":
    # Obter o diretório absoluto onde o script Python está localizado
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Construir o caminho absoluto para o arquivo XML
    xml_file = os.path.join(script_dir, "particoes.xml")
    gui = SLURMJobSubmitGUI(xml_file)
