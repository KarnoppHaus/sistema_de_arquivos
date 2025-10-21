import os

from exceptions import *

class Common:
    def __init__(self, control):
        self.control = control

    def mv(self, file, cwd, inodes_array, blocks_bitmap, inodes_bitmap, *args):
        # <-::- Manipular Arquivo 1 -::->
        if len(args) != 2: raise WrongParameters('Você deve passar dois parâmetros para esta função! Use mv [arquivo1] [arquivo2]')
        dir1, dir2 = args
        dir1 = dir1.split('/')
        if dir1[-1] in ['.', '..', '']: raise CantMoveParent('Use ../ para mover esta pasta')
        t1_cwd = self.control.change_dir(file, cwd[0], dir1[0:-1], inodes_array)
        folder_dict1 = self.control.read_blocks(file, t1_cwd, inodes_array)
        index = folder_dict1[dir1[-1]]
        del folder_dict1[dir1[-1]]

        # <-::- Manipular Arquivo 2 -::->
        dir2 = dir2.split('/')
        if dir2[-1] in ['.', '..', '']: raise CantMoveParent('Não é possível utilizar este tipo de caminho')
        t2_cwd = self.control.change_dir(file, cwd[0], dir2[0:-1], inodes_array)
        folder_dict2 = self.control.read_blocks(file, t2_cwd, inodes_array)
        if dir2[-1] in folder_dict2: raise FileAlreadyExists('O diretório final já existe!')
        folder_dict2[dir2[-1]] = index
        inode = self.control.read_inode(inodes_array, index)
        inode.name = dir2[-1]

        # <-::- Gravar alterações -::->
        self.control.save_inode(inodes_array, inode)
        self.control.rewrite(file, t1_cwd, inodes_array, folder_dict1, blocks_bitmap)
        self.control.rewrite(file, t2_cwd, inodes_array, folder_dict2, blocks_bitmap)       
        
    def ln(self, file, cwd, inodes_array, blocks_bitmap, inodes_bitmap, *args):
        # <-::- Manipular Arquivo 1 -::->
        if len(args) != 2: raise WrongParameters('Você deve passar dois parâmetros para esta função! Use "ln [arquivo1] [arquivo2]"')
        dir1, dir2 = args
        dir1 = dir1.split('/')
        if dir1[-1] in ['.', '..', '']: raise CantMoveParent('Use ../ para linkar esta pasta')
        t1_cwd = self.control.change_dir(file, cwd[0], dir1[0:-1], inodes_array)
        folder_dict1 = self.control.read_blocks(file, t1_cwd, inodes_array)
        org_inode = self.control.read_inode(inodes_array, folder_dict1[dir1[-1]])

        # <-::- Manipular Arquivo 2 -::->
        dir2 = dir2.split('/')
        if dir2[-1] in ['.', '..', '']: raise CantMoveParent('Não é possível criar um link em uma pasta pai')
        t2_cwd = self.control.change_dir(file, cwd[0], dir2[0:-1], inodes_array)
        folder_dict2 = self.control.read_blocks(file, t2_cwd, inodes_array)
        if dir2[-1] in folder_dict2: raise FileAlreadyExists('O diretório/arquivo final já existe!')
        inode = self.control.create_link_inode(dir2[-1], org_inode, inodes_bitmap)
        folder_dict2[inode.name] = inode.index

        # <-::- Gravar alterações -::->
        self.control.save_inode(inodes_array, inode)
        self.control.rewrite(file, t1_cwd, inodes_array, folder_dict1, blocks_bitmap)
        self.control.rewrite(file, t2_cwd, inodes_array, folder_dict2, blocks_bitmap)       

    def clear(*args):
        os.system('clear')

    def exit(*args):
        exit(0)