# Libs
import shlex # Lib usada para tokenizar entrada e reconhecer operações
from bitarray import bitarray # Lib usada para salvar os maps de blocos e inodes
import pickle
import numpy as np
import os

# Files
from functions import archives, directory, common, login # Arquivos contendo funções
from variables import *
from control import *

def absolute_path(f, inode, inodes_array):
    path = []
    while inode.index != 0:
        path.append(inode.name)
        inode = ctrl.change_dir(f, inode, ['..'], inodes_array)
    path.reverse()
    if len(path) == 0: return '/'
    try:
        if path[0] == 'home' and path[1] == ctrl.user:
            path.pop(0)
            path.pop(0)
            return '~/' + '/'.join(path)
    except IndexError:
        pass
    return '/' + '/'.join(path)
    

def read_bitmap(file, pos, n):
    file.seek(pos)
    bitmap = bitarray()
    bitmap.frombytes(f.read(n))
    return list(bitmap)

# Arquitetura Atual
# Bloco 0 --> Super bloco
# Blocos 1-32 --> Bitmap de blocos 0/1 -> livres/ocupados => (HDD em Bytes / Tamanho dos blocos = Blocos) / 8 = Bytes necessários para representar estados) / Tamanho dos blocos = Blocos necessários para Bitmap
## Bloco 33 --> Bitmap de inodes 0/1 -> livres/ocupados => Numero de INodes / INodes por bloco / Tamanho dos blocos = Blocos necessários para Bitmap
## Blocos 34-1058 --> INodes em si => Valor arbitrário
# Blocos 1058-131071 (inicia em bloco 0) --> dados (arquivos/diretorios) => Blocos restantes

# <-::- Ler Array de INodes -::->
try:
    inodes_array = np.load('inodes.npy', allow_pickle=True)
except ModuleNotFoundError:
    exit(f'Erro. Crie o disco primeiramente com "disk_manipulate.py"')


try:
    with open('disk.img', 'r+b') as f:
        # <-::- Ler Superbloco -::->
        f.seek(0)
        sb = pickle.load(f)

        ctrl = Control(sb)

        # <-::- Criar operações para leitura -::->
        df = directory.Directory(ctrl)
        af = archives.Archives(ctrl)
        cf = common.Common(ctrl)
        login = login.Login(ctrl)

        operations = {'mv':cf.mv, # Funções que serão reconhecidas pelo token
                    'ln':cf.ln,  
                    'chown':cf.chown,
                    'chmod':cf.chmod,
                    'clear':cf.clear,
                    'exit':cf.exit,
                    'touch':af.touch, 
                    'rm':af.rm, 
                    'echo':af.echo, 
                    'cat':af.cat, 
                    'cp':af.cp, 
                    'mkdir':df.mkdir, 
                    'rmdir':df.rmdir, 
                    'ls':df.ls, 
                    'cd':df.cd
                    }
        
        # <-::- Carregar CWD e Bitmaps -::->

        blocks_bitmap = read_bitmap(f, sb['blocks_bitmap_start'] * sb['block_size'], (sb['inodes_bitmap_start'] - sb['blocks_bitmap_start']) * sb['block_size'])
        inodes_bitmap = read_bitmap(f, sb['inodes_bitmap_start'] * sb['block_size'], (sb['data_blocks_start'] - sb['inodes_bitmap_start']) * sb['block_size'])

        os.system('clear') # Limpar terminal

        # <-::- Login -::->
        while True:
            opt = input(f'1. Login\n2. Criar usuario\n3. Listar usuarios\n')
            match opt:
                case '1':
                    user = input(f'Insira o usuário de Login: ')
                    passwd = input(f'Insira a senha: ')
                    cwd = login.login(f, inodes_array, user, passwd)
                    match cwd:
                        case 'err_usr':
                            print(f'O usuario inserido esta incorreto!')
        
                        case 'err_passwd':
                            print(f'A senha inserida esta incorreta!')
                        
                        case _:
                            break         
                
                case '2':
                    user = input(f'Insira o usuário de Login: ')
                    passwd = input(f'Insira a senha: ')
                    group = input(f'Insira o grupo do usuario: ')
                    cwd = login.create(f, inodes_array, blocks_bitmap, inodes_bitmap, user, passwd, group)
                    match cwd:
                        case 'err_existent_usr':
                            print(f'O usuario inserido ja existe!')
        
                        case 'err_invalid_usr':
                            print(f'O nome de usuario nao e aceito!')
                        
                        case 'err_invalid_grp':
                            print(f'O nome de grupo nao e aceito!')
                        
                        case _:
                            break
                
                case '3':
                    print(', '.join(login.list_users(f, inodes_array)))
                
                case _:
                    print(f'Erro. Insira uma opcao valida!')
                
        del login

        while True: # Loop para entradas>
            entry = input(f"{ctrl.user}:{absolute_path(f, cwd[0], inodes_array)}$ ") # Entrada do terminal
            tokens = shlex.split(entry) # Tokeniza entrada

            try:
                op = operations[tokens[0]] # Primeiro token sempre será a operação a ser realizada
                op(f, cwd, inodes_array, blocks_bitmap, inodes_bitmap, *tokens[1:])
            except KeyError:
                print("Erro. Comando não existente!")
            except Exception as e:
                print(e)

except FileNotFoundError:
    exit(f'Erro. Crie o disco primeiramente com "disk_manipulate.py"')
