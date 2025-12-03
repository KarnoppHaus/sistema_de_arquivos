from exceptions import *

class Directory:
    def __init__(self, control):
        self.control = control

    def mkdir(self, file, cwd, inodes_array, blocks_bitmap, inodes_bitmap, *args):
        if len(args) != 1: raise WrongParameters
        dir = args[0].split('/')
        if dir[-1] in ['.', '..', '']: raise NotAcceptableDirName(f"A pasta não pode se chamar {dir[-1]}")
        cwd = self.control.change_dir(file, cwd[0], dir[0:-1], inodes_array)
        self.control.create_folder(file, dir[-1], inodes_array, inodes_bitmap, cwd, blocks_bitmap)

    def rmdir(self, file, cwd, inodes_array, blocks_bitmap, inodes_bitmap, *args):
        if len(args) != 1: raise WrongParameters
        dir = args[0].split('/')
        if dir[-1] in ['.', '..']: raise CantRemove
        cwd = self.control.change_dir(file, cwd[0], dir, inodes_array)
        folder_dict = self.control.read_blocks(file, cwd, inodes_array)
        f_cwd = self.control.read_inode(inodes_array, folder_dict['..'])
        if len(folder_dict) == 2:
            for block in cwd.block_pointers:
                blocks_bitmap[block] = 0
            inodes_bitmap[cwd.index] = 0
            cwd = self.control.read_inode(inodes_array, folder_dict['..'])
            folder_dict = self.control.read_blocks(file, cwd, inodes_array)
            del folder_dict[dir[-1]]
            self.control.save_bitmap(file, blocks_bitmap, inodes_bitmap)
            self.control.rewrite(file, cwd, inodes_array, folder_dict, blocks_bitmap)

    def ls(self, file, cwd, inodes_array, blocks_bitmap, inodes_bitmap, *args):
        if len(args) != 0 and len(args) != 1: raise WrongParameters
        dir = args[0].split('/') if len(args) != 0 else []
        cwd = self.control.change_dir(file, cwd[0], dir[0:-1], inodes_array)
        if not self.__verify_perm(cwd, 'r'): raise NoPermissionTo('Voce nao tem permissao para ler nesta pasta!')
        folder_dict = self.control.read_blocks(file, cwd, inodes_array)

        # <-::- Formatar saida -::->
        del folder_dict['.'], folder_dict['..']
        formatted_output = sorted(folder_dict, key=lambda x: (self.control.read_inode(inodes_array, folder_dict[x]).permissions[0], x))
        for item in formatted_output:
            if self.control.read_inode(inodes_array, folder_dict[item]).permissions[0] == 'd':
                print(f'\033[1;31m{item}/ ', end='')
            else:
                print(f'\033[37m{item} ', end='')
        if len(folder_dict) > 0: print('\033[0m')

            

    def cd(self, file, cwd, inodes_array, blocks_bitmap, inodes_bitmap, *args):
        if len(args) != 1: raise WrongParameters
        dir = args[0].split('/')
        cwd[0] = self.control.change_dir(file, cwd[0], dir, inodes_array)

    def __verify_perm(self, archive, perm) -> bool:
        if self.control.user == 'root': return True
        v = {'r':0, 'w':1, 'x':2}
        comp1 = [archive.owner, archive.group, None]
        comp2 = [self.control.user, self.control.user_group, None]
        for i, (c1, c2) in enumerate(zip(comp1, comp2)):
            if c1 == c2:
                if archive.permissions[(i * 3) + v[perm] + 1] != '-':
                    return True
                return False
