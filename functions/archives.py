from exceptions import *

# <-::- FUNÇÕES DE ARQUIVOS -::->

class Archives():
    def __init__(self, control):
        #o construtor recebe a instância de Control, que é o motor de I/O de baixo nível
        self.control = control

    def touch(self, file, cwd, inodes_array, blocks_bitmap, inodes_bitmap, *args):
        #cria arquivo vazio 
        if len(args) != 1: raise WrongParameters('Você deve passar um parâmetro para esta função! Use touch [arquivo]')
        dir = args[0].split('/') # dir[-1] --> Filename
        if dir[-1] in ['.', '..', '']: raise NotAcceptableFileName
        cwd = self.control.change_dir(file, cwd[0], dir[0:-1], inodes_array)
        self.control.create_file(file, dir[-1], inodes_array, inodes_bitmap, cwd, blocks_bitmap)
        #self.control.add_in_folder(file, file_inode, inodes_array, cwd, blocks_bitmap)

    def rm(self, file, cwd, inodes_array, blocks_bitmap, inodes_bitmap, *args):
        #remove um arquivo
        if len(args) != 1: raise WrongParameters('Você deve passar um parâmetro para esta função! Use rm [arquivo]')
        dir = args[0].split('/')
        if dir[-1] in ['.', '..']: raise CantRemove
        cwd = self.control.change_dir(file, cwd[0], dir[0:-1], inodes_array)
        folder_dict = self.control.read_blocks(file, cwd, inodes_array)
        f_inode = self.control.read_inode(inodes_array, folder_dict[dir[-1]])

        if f_inode.permissions[0] == '-':
            for block in f_inode.block_pointers:
                blocks_bitmap[block] = 0
            inodes_bitmap[f_inode.index] = 0
            del folder_dict[dir[-1]]
            self.control.save_bitmap(file, blocks_bitmap, inodes_bitmap)
            self.control.rewrite(file, cwd, inodes_array, folder_dict, blocks_bitmap)

    def echo(self, file, cwd, inodes_array, blocks_bitmap, inodes_bitmap, *args):
        #comando: echo ["mensagem"] [>, >>] [arquivo] - Escreve conteúdo em um arquivo
        if len(args) != 3: raise WrongParameters('Você deve passar três parâmetros para esta função! Use echo ["mensagem"] [>, >>] [arquivo]')
        dir = args[2].split('/') # dir[-1] --> Filename
        if dir[-1] in ['.', '..', '']: raise NotAcceptableFileName
        cwd = self.control.change_dir(file, cwd[0], dir[0:-1], inodes_array)
        folder_dict = self.control.read_blocks(file, cwd, inodes_array)
        match args[1]:
            case '>':
                if dir[-1] in folder_dict:
                    self.control.rewrite(file, self.control.read_inode(inodes_array, folder_dict[dir[-1]]), inodes_array, args[0], blocks_bitmap)
                else:
                    self.control.create_file(file, dir[-1], inodes_array, inodes_bitmap, cwd, blocks_bitmap, args[0])
            case '>>':
                if dir[-1] in folder_dict:
                    file_content = self.control.read_blocks(file, self.control.read_inode(inodes_array, folder_dict[dir[-1]]), inodes_array)
                    self.control.rewrite(file, self.control.read_inode(inodes_array, folder_dict[dir[-1]]), inodes_array, (file_content  + '\n' + args[0]) if file_content else args[0], blocks_bitmap)
                else:
                    self.control.create_file(file, dir[-1], inodes_array, inodes_bitmap, cwd, blocks_bitmap, args[0])

    def cat(self, file, cwd, inodes_array, blocks_bitmap, inodes_bitmap, *args):
        #exibe conteudo de um arquivo 
        if len(args) != 1: raise WrongParameters('Você deve passar um parâmetro para esta função! Use cat [arquivo]')
        dir = args[0].split('/') # dir[-1] --> Filename
        if dir[-1] in ['.', '..', '']: raise NotAcceptableFileName
        cwd = self.control.change_dir(file, cwd[0], dir[0:-1], inodes_array)
        folder_dict = self.control.read_blocks(file, cwd, inodes_array)
        file_inode = self.control.read_inode(inodes_array, folder_dict[dir[-1]])
        content = self.control.read_blocks(file, file_inode, inodes_array)
        print('<-::- FILE CONTENT -::->')
        print(content.replace("\\n", '\n'))
        print('<-::- END OF FILE -::->')

    def cp(self, file, cwd, inodes_array, blocks_bitmap, inodes_bitmap, *args):
        #cp [origem] [destino] - Copia um arquivo
        # <-::- Manipular Arquivo 1 -::->
        if len(args) != 2: raise WrongParameters('Você deve passar dois parâmetros para esta função! Use cp [origem] [destino]')
        dir1, dir2 = args
        dir1 = dir1.split('/')
        if dir1[-1] in ['.', '..', '']: raise NotAcceptableFileName
        t_cwd = self.control.change_dir(file, cwd[0], dir1[0:-1], inodes_array)
        folder_dict = self.control.read_blocks(file, t_cwd, inodes_array)
        content = self.control.read_blocks(file, self.control.read_inode(inodes_array, folder_dict[dir1[-1]]), inodes_array)

        # <-::- Copiar Arquivo 2 -::->
        self.echo(file, cwd, inodes_array, blocks_bitmap, inodes_bitmap, content, '>', dir2)
        