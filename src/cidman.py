'''
    04/18/2025
    
'''

# Client ID Format
# C  : Client 
# XX : State Abbreviation (GA, ...)
# 00 : two digit sequential number of 1st, 2nd, ... building
# N  : 
# XXX: 
# Example : CGA01N000, CGA01N002

class ClientID:
    def __init__(self):
        self.clear()
        
    def clear(self):
        self.id_pool = []
        self.id_key = {}
        self.cur_id = 0
        
    def __str__(self):
        msg = "ID  : "+','.join(self.id_key.keys())+'\n'
        msg += "POOL: "+','.join([f"{i_:03d}" for i_ in self.id_pool])
        return msg
        
    def get(self, state, building):
        if len(self.id_pool) == 0:
            self.cur_id += 1
            new_id = self.cur_id
        else:
            self.cur_id = self.id_pool.pop()
            new_id = self.cur_id
        id_str = f"C{state}{building:02d}N{new_id:03d}"
        self.id_key[f"{new_id:03d}"] = id_str

        return id_str
    
    def discard(self, id_str):
        if self.find(id_str):
            del self.id_key[id_str]      
            
    def id_(self, id_str):
        return id_str[6:]
    
    def add(self, id_str):
        i_ = self.id_(id_str)
        self.id_key[i_] = id_str
        self.cur_id = int(i_)
        
    def add_ids(self, id_str_list):
        for i_ in id_str_list:
            self.add(i_)
        # check any jump in consecutive ids
        id_ = [int(i_[-3:]) for i_ in id_str_list]
        id_.sort()
        prv_i = id_[0]
        for i_ in id_[1:]:
            if (i_ - prv_i) > 1:
                for j_ in range(prv_i+1, i_):
                    self.id_pool.append(j_)
            prv_i = i_
            
    def find(self, id_str):
        try:
            value = self.id_key[id_str]
            return True
        except:
            return False
        
    def remove(self, id_str):
        id_ = id_str[-3:]
        if id_ in self.id_key:
            self.id_pool.append(int(id_))
            del self.id_key[id_]
    
if __name__ == "__main__":          
    i_ = ClientID()
    print(i_.id_pool)