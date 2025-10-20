class IndexNode:
    def __init__(self, name, index, creator, owner, data_size, c_date, m_date, permissions, b_pointers=[], i_node_pointer=None):
        self.name = name
        self.index = index
        self.creator = creator
        self.owner = owner
        self.data_size = data_size
        self.creation_date = c_date
        self.modification_date = m_date
        self.permissions = permissions
        self.block_pointers = b_pointers
        self.inode_pointer = i_node_pointer