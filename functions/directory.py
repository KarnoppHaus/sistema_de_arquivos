from exceptions import *

class Directory:
    #classe responsável pelos comandos de manipulação de diretórios (pastas)
    
    def __init__(self, control):
        #o construtor recebe a instância de Control, o núcleo de I/O de disco
        self.control = control

    def mkdir(self, file, cwd, inodes_array, blocks_bitmap, inodes_bitmap, *args):
        #comando: mkdir [pasta] - Cria um novo diretório
        if len(args) != 1: raise WrongParameters # Exige exatamente um argumento
        
        dir = args[0].split('/') #divide o caminho/nome da nova pasta
        #valida se o nome da pasta não é reservado (., .., ou vazio)
        if dir[-1] in ['.', '..', '']: raise NotAcceptableDirName(f"A pasta não pode se chamar {dir[-1]}")
        
        #1. Navega até o diretório pai (dir[0:-1] exclui o nome da nova pasta)
        cwd = self.control.change_dir(file, cwd[0], dir[0:-1], inodes_array)
        
        #2. Delega a criação da pasta para o núcleo de controle, que aloca i-node e bloco
        self.control.create_folder(file, dir[-1], inodes_array, inodes_bitmap, cwd, blocks_bitmap)
        #self.control.add_in_folder(...) # Linha comentada (lógica já incluída em create_folder)

    def rmdir(self, file, cwd, inodes_array, blocks_bitmap, inodes_bitmap, *args):
        #comando: rmdir [pasta] - Remove um diretório VAZIO
        if len(args) != 1: raise WrongParameters #exige exatamente um argumento
        
        dir = args[0].split('/')
        if dir[-1] in ['.', '..']: raise CantRemove # Proíbe remover as referências internas
        
        # 1. Navega para a pasta a ser removida (inclui o nome da pasta no caminho)
        cwd = self.control.change_dir(file, cwd[0], dir, inodes_array)
        
        # 2. Lê o conteúdo da pasta a ser removida
        folder_dict = self.control.read_blocks(file, cwd, inodes_array)
        
        # 3. VERIFICAÇÃO DE VAZIO: Um diretório só está "vazio" se tiver apenas '.' e '..'
        if len(folder_dict) == 2:
            # <-::- Liberação de Recursos -::->
            for block in cwd.block_pointers:
                blocks_bitmap[block] = 0 #marca os blocos de dados do diretório como LIVRES
            inodes_bitmap[cwd.index] = 0 #marca o i-node do diretório como LIVRE
            
            # 4. Atualiza o Diretório Pai
            #obtém o i-node do diretório pai (lendo o índice '..' do dicionário)
            cwd_parent_inode = self.control.read_inode(inodes_array, folder_dict['..'])
            #lê o conteúdo do diretório pai
            folder_dict = self.control.read_blocks(file, cwd_parent_inode, inodes_array)
            #remove a entrada do diretório que foi excluído
            del folder_dict[dir[-1]] 
            
            # 5. Persiste as Mudanças
            self.control.save_bitmap(file, blocks_bitmap, inodes_bitmap) #salva os Bitmaps atualizados
            #reescreve o dicionário da pasta pai (cwd_parent_inode) no disco
            self.control.rewrite(file, cwd_parent_inode, inodes_array, folder_dict, blocks_bitmap)

    def ls(self, file, cwd, inodes_array, blocks_bitmap, inodes_bitmap, *args):
        #comando: ls [caminho opcional] - Lista o conteúdo de um diretório
        if len(args) != 0 and len(args) != 1: raise WrongParameters #aceita 0 ou 1 argumento
        
        #determina o caminho: usa args[0] se existir, senão usa o diretório atual
        dir = args[0].split('/') if len(args) != 0 else []
        
        #navega para o diretório alvo da listagem (dir[0:-1] se for um caminho, senão o próprio CWD)
        cwd = self.control.change_dir(file, cwd[0], dir[0:-1], inodes_array)
        folder_dict = self.control.read_blocks(file, cwd, inodes_array) #lê o conteúdo do diretório

        # <-::- Formatar saida -::->
        del folder_dict['.'], folder_dict['..'] #remove as referências internas para exibição
        
        #ordena a saída: chave de ordenação prioriza o tipo ('d' para diretório) e depois o nome
        formatted_output = sorted(folder_dict, key=lambda x: (self.control.read_inode(inodes_array, folder_dict[x]).permissions[0], x))
        
        for item in formatted_output:
            inode_check = self.control.read_inode(inodes_array, folder_dict[item])
            if inode_check.permissions[0] == 'd':
                #usa código ANSI para cor vermelha (\033[1;31m) para diretórios
                print(f'\033[1;31m{item}/ ', end='')
            else:
                #usa código ANSI para cor branca (\033[37m) para arquivos
                print(f'\033[37m{item} ', end='')
        
        if len(folder_dict) > 0: print('\033[0m')

    def cd(self, file, cwd, inodes_array, blocks_bitmap, inodes_bitmap, *args):
        #comando: cd [destino] - Muda o diretório de trabalho atual
        if len(args) != 1: raise WrongParameters
        
        dir = args[0].split('/')
        # 1. Usa change_dir para navegar e obter o i-node de destino
        new_cwd_inode = self.control.change_dir(file, cwd[0], dir, inodes_array)
        
        # 2. ATUALIZAÇÃO DO CWD: Altera o i-node na primeira posição da lista 'cwd'
        cwd[0] = new_cwd_inode