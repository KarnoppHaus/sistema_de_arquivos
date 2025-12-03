from exceptions import *
import hashlib
import re

# <-::- FUNÇAO DE LOGIN/CRIACAO DE USUARIO -::->

class Login():
    def __init__(self, control):
        self.control = control

    def login(self, file, inodes_array, user, password):
        users = self.__users_infos(file, inodes_array)
        for usr in users:
            if usr[0] == user:
                if hashlib.sha256(password.encode()).hexdigest() == usr[1]:
                    self.control.user = user
                    self.control.user_group = usr[3]
                    return [self.control.change_dir(file, None, usr[4].split('/'), inodes_array)] # -> Retorna pasta inicial do usuário
                return 'err_passwd' # -> Retorna ERRO de senha
        return 'err_usr' # -> Retorna ERRO de usuario

    def create(self, file, inodes_array, blocks_bitmap, inodes_bitmap, user, password, group):
        usr_pat = re.compile(r'[a-zA-Z0-9\-\.]{4,32}')
        gp_pat = re.compile(r'[a-zA-Z0-9\-\.]{1,32}')
        users_list = self.list_users(file, inodes_array)
        if user in users_list:
            return 'err_existent_usr'
        if not bool(usr_pat.match(user)):
            return 'err_invalid_usr'
        if not bool(gp_pat.match(group)):
            return 'err_invalid_grp'

        passwd_inode = self.control.read_inode(inodes_array, 4)
        passwd_content = self.control.read_blocks(file, passwd_inode, inodes_array) + f'{user}:{hashlib.sha256(password.encode()).hexdigest()}:{self.__find_user_id(file, inodes_array)}:{group}:/home/{user}\n'
        self.control.user = 'root'
        self.control.user_group = 'root_group'
        cwd = self.control.change_dir(file, None, f'/home'.split('/'), inodes_array)
        self.control.create_folder(file, user, inodes_array, inodes_bitmap, cwd, blocks_bitmap)
        self.control.rewrite(file, passwd_inode, inodes_array, passwd_content, blocks_bitmap)
        self.control.user = user
        self.control.user_group = group
        cwd_content = self.control.read_blocks(file, cwd, inodes_array)
        dir_inode = self.control.read_inode(inodes_array, cwd_content[user])
        dir_inode.creator = user
        dir_inode.owner = user
        dir_inode.group = group
        self.control.save_inode(inodes_array, dir_inode)
        
        return [self.control.change_dir(file, None, f'/home/{user}'.split('/'), inodes_array)]
        
    def list_users(self, file, inodes_array):
        passwd_inode = self.control.read_inode(inodes_array, 4)
        passwd_content = self.control.read_blocks(file, passwd_inode, inodes_array)
        return list(map(lambda x: x.split(':')[0], passwd_content.split('\n')[:-1]))

    def __users_infos(self, file, inodes_array):
        passwd_inode = self.control.read_inode(inodes_array, 4)
        passwd_content = self.control.read_blocks(file, passwd_inode, inodes_array)
        return list(map(lambda x: x.split(':'), passwd_content.split('\n')[:-1]))
    
    def __find_user_id(self, file, inodes_array):
        users_infos = self.__users_infos(file, inodes_array)
        max_id = -1
        for usr in users_infos:
            max_id = max(max_id, int(usr[2]))
        return max_id + 1
    