'''
    cnpcman: CNP Client Coordinatir
'''

from PyQt5.QtCore import QObject, pyqtSignal
import cnpdb, cidman

class ClientCoordinator(QObject):

    print_message = pyqtSignal(str)
    
    def __init__(self):
        super(ClientCoordinator, self).__init__()
        self.cur_client_index = 0
        self.db = cnpdb.ClientDB()
        self.cim = cidman.ClientID()
        self.clients = []
        
    def count(self):
        return len(self.clients)
        
    def load(self):
        # each client data is a dictionary
        # clients is a lift of dictionary(each client)
        self.clients = self.db.load_all_clients()
        if self.clients == []:
            return False
        id_ = [c_[cnpdb.col_id] for c_ in self.clients]
        self.cim.clear()
        self.cim.add_ids(id_)
        return True
        
    def close(self):
        self.db.close()
        
    def clear(self):
        self.clients = []
        self.cur_client_index = 0
        
    def remove_all(self):
        deleted_clients = self.db.remove_all()
        self.clear()
        return deleted_clients
        
    def get_clients(self):
        return self.clients
        
    def current_client(self):
        if self.clients == []:
            self.print_message.emit("... Error (ClientCoordinator::current_client). No client data exist")
            return None
        if self.cur_client_index >= len(self.clients):
            self.cur_client_index = len(self.clients)-1
        return self.clients[self.cur_client_index]
        
    def add_client(self, client):
        try:
            self.db.add_client(client)
        except Exception as e:
            self.print_message.emit(f"... Error (ClientCoordinator::add_client) : {e}")
            return 
        self.cur_client_index += 1
        
    def update_client(self, client):
        c_ = client.copy()
        self.db.update_client(client)
        self.clients[self.cur_client_index] = c_
        
    def delete_client(self, id_):
        try:
            self.db.delete_client(id_)
        except Exception as e:
            self.print_message.emit(f"... Error (ClientCoordinator::delete_client) : {e}")
            return 
        self.cim.remove(id_)
        
    # In case of delete. must be called after load
    def calculate_client_index(self, prv_client_index=-1):
        c_len = len(self.clients)
        
        if prv_client_index >= 0:
            self.cur_client_index = prv_client_index
            
        if self.cur_client_index < 0: 
            self.cur_client_index = 0
        elif self.cur_client_index > c_len:
            self.cur_client_index = c_len-1
        
    def end_client(self):
        self.cur_client_index = len(self.clients)-1
        
    def next_client(self):
        nc = len(self.clients)
        if (self.cur_client_index+1) >= nc:
            return False
        self.cur_client_index += 1
        return True
        
    def prev_client(self):
        if (self.cur_client_index-1) < 0:
            return False
        self.cur_client_index -= 1
        return True
    
    def init_client_index(self):
        self.cur_client = 0
        