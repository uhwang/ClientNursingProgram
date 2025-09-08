import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from PyQt5.QtCore import pyqtSignal, QObject

DB_FILE = "eben_clients.db"

change_assessment_yes = "Yes"
change_assessment_no = "No"

table_name = "clients"

EXPECTED_COLUMNS = [
    "client_id",
    "pic_path",
    "first_name_kor",
    "last_name_kor",
    "first_name_eng",
    "middle_name_eng",
    "last_name_eng",
    "dob",
    "sex",
    "room_number",
    "initial_assessment",
    "assessment_14th",
    "assessment_90th",
    "change_assessment",
    "change_assessment_done",
    "comments"
]

kr_name = lambda n : n.find("kor") >= 0

id_index                    = 0
pic_path_index              = 1
first_name_kor_index        = 2
last_name_kor_index         = 3
first_name_eng_index        = 4
middle_name_eng_index       = 5
last_name_eng_index         = 6
dob_index                   = 7
sex_index                   = 8
room_number_index           = 9
initial_assessment_index    = 10
assessment_14th_index       = 11
assessment_90th_index       = 12
change_assessment_index     = 13
change_assessment_done_index= 14
comments_index              = 15

col_id                     = EXPECTED_COLUMNS[id_index                    ]
col_pic_path               = EXPECTED_COLUMNS[pic_path_index              ]
col_first_name_kor         = EXPECTED_COLUMNS[first_name_kor_index        ]
col_last_name_kor          = EXPECTED_COLUMNS[last_name_kor_index         ]
col_first_name_eng         = EXPECTED_COLUMNS[first_name_eng_index        ]
col_middle_name_eng        = EXPECTED_COLUMNS[middle_name_eng_index       ]
col_last_name_eng          = EXPECTED_COLUMNS[last_name_eng_index         ]
col_dob                    = EXPECTED_COLUMNS[dob_index                   ]
col_sex                    = EXPECTED_COLUMNS[sex_index                   ]
col_room_number            = EXPECTED_COLUMNS[room_number_index           ]
col_initial_assessment     = EXPECTED_COLUMNS[initial_assessment_index    ]
col_assessment_14th        = EXPECTED_COLUMNS[assessment_14th_index       ]
col_assessment_90th        = EXPECTED_COLUMNS[assessment_90th_index       ]
col_change_assessment      = EXPECTED_COLUMNS[change_assessment_index     ]
col_change_assessment_done = EXPECTED_COLUMNS[change_assessment_done_index]
col_comments               = EXPECTED_COLUMNS[comments_index              ]

view_table_head_label=[
    "ID",
    "Pic",
    "First KR",
    "Last KR",
    "First EN",
    "Middle EN",
    "Last EN",
    "DOB",
    "Sex",
    "Room",
    "Initial",
    "14th",
    "90th",
    "Change",
    "State",
    "comments"
]

'''
default_view_visible_key = [
    view_table_head_label[2],
    view_table_head_label[3],
    view_table_head_label[4],
    view_table_head_label[5],
    view_table_head_label[6],
    view_table_head_label[],

]
'''

def available_view_column_key(col_name):
    index = view_table_head_label.index(col_name)
    return EXPECTED_COLUMNS[index]

class ClientDB(QObject):
    
    print_message  = pyqtSignal(str)
    
    def __init__(self, db_file=DB_FILE):
        super(ClientDB, self).__init__()
        self.db_valid = True
        self.db_file = db_file
        self.conn = None
        
    def close(self):
        if self.conn is not None:
            self.conn.close()

    def check(self):
        db_path = Path(self.db_file)
        if db_path.exists() == False:
            self.conn = sqlite3.connect(self.db_file)
            self.print_message.emit(f"... {self.db_file} not exist. Creating Table")
            try:
                #self.conn = sqlite3.connect(self.db_file)
                self.conn.row_factory = sqlite3.Row
                self.create_table()
            except Exception as e:
                self.print_message.emit("... Error : %s"%str(e))
                return
            self.print_message.emit("... Success: creating Table")
            self.db_valid = True
        else:
            self.conn = sqlite3.connect(self.db_file)                    
            self.print_message.emit("... DB validity check")
            #self.conn = sqlite3.connect(self.db_file)
            res = self.validate_database()
                
            if res == True:
                self.db_valid = True
                self.print_message.emit("... DB validity success")
            else:
                self.print_message.emit("... DB validity fail!!")
        return self.db_valid
            
    def validate_database(self):
        try:
            #conn = sqlite3.connect(self.db_file)
            cursor = self.conn.cursor()
    
            # Check if table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='clients';")
            if cursor.fetchone() is None:
                self.print_message.emit("Invalid database: 'clients' table not found.")
                self.db_valid = False
                raise ValueError("Invalid database: 'clients' table not found.")
                
            # Get actual columns
            cursor.execute("PRAGMA table_info(clients);")
            columns = [row[1] for row in cursor.fetchall()]
    
            # Compare with expected
            if columns != EXPECTED_COLUMNS:
                self.print_message.emit(f"Invalid database schema. Expected {EXPECTED_COLUMNS}, got {columns}")
                self.db_valid = False
                raise ValueError(f"Invalid database schema. Expected {EXPECTED_COLUMNS}, got {columns}")
                
            if not self.db_valid: self.conn.close()

        except Exception as e:
            #self.print_message.emit(f"Database validation failed: {e}")
            return False
        return True
        
    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS clients (
            client_id TEXT PRIMARY KEY,
            pic_path,
            first_name_kor TEXT,
            last_name_kor TEXT,
            first_name_eng TEXT,
            middle_name_eng TEXT,
            last_name_eng TEXT,
            dob TEXT,
            sex TEXT,
            room_number TEXT,
            initial_assessment TEXT,
            assessment_14th TEXT,
            assessment_90th TEXT,
            change_assessment TEXT,
            change_assessment_done TEXT,
            comments TEXT
        );
        """
        self.conn.execute(query)
        self.conn.commit()

    # -------------------
    # Basic CRUD
    # -------------------
                
    def remove_all(self):
        deleted_clients = 0
        
        if self.conn is None:
            self.print_message.emit("... ClientDB::Error::remove_all\n"+
                                    "    Database is not connected")
            raise ValueError("Database is not opened!")
            
        cursor = self.conn.cursor()
        try:
            cursor.execute('DELETE FROM clients;')
            self.conn.commit()
            deleted_clients = cursor.rowcount
        except sqlite3.Error as e:
            self.print_message.emit("... Error(ClientDB::Error::remove_all\n"+
                                    "    can't remove all clients\n"+
                                    f"   {str(e)}")
            raise RuntimeError(f"Remove all clients failed: {e}")
        
        self.print_message.emit(f"... Success: {deleted_clients} clients deleted")
        return deleted_clients
        
    def add_client(self, client_data: dict):
        """Insert new client. Blank values allowed."""
        placeholders = ", ".join("?" * len(client_data))
        columns = ", ".join(client_data.keys())
        values = [client_data[k] if client_data[k] else None for k in client_data]  # None -> NULL
        query = f"INSERT INTO clients ({columns}) VALUES ({placeholders})"
        try:
            self.conn.execute(query, values)
            self.conn.commit()
        except sqlite3.IntegrityError:
            raise ValueError(f"Client with id {client_data['client_id']} already exists.")

    def execute_query(self, query, key=None):
        cur = self.conn.execute(query)
        return [dict(self.row_to_client(row, key)) for row in cur.fetchall()]
        
    def custom_query(self, key):
        k_ = ','.join(key)
        cur = self.conn.execute(f"SELECT {k_} FROM clients")
        return [dict(self.row_to_client(row, key)) for row in cur.fetchall()]
        
    def search_by_name_roomnumber(self, f_name, l_name, r_num):
        cur = self.conn.execute("SELECT * FROM clients WHERE first_name_kor, last_name_kor, room_number LIKE ?", (f"%{f_name}%",))
        
    def update_client(self, client_data: dict):
        client_id = client_data.pop(col_id)
        """Update existing client by ID"""
        set_clause = ", ".join(f"{k}=?" for k in client_data.keys())
        values = [client_data[k] if client_data[k] else None for k in client_data]
        values.append(client_id)
        query = f"UPDATE clients SET {set_clause} WHERE client_id=?"
        #try:
        self.conn.execute(query, values)
        self.conn.commit()
        #except Exception as e:
        #    self.print_message.emit(str(e))
            
    def delete_client(self, client_id: str):
        """Delete client by ID"""
        self.conn.execute("DELETE FROM clients WHERE client_id=?", (client_id,))
        self.conn.commit()

    def row_to_client(self, row, key=None):
        if key is None:
            client = {
                col_id                    : row[id_index                    ],
                col_pic_path              : row[pic_path_index              ],
                col_first_name_kor        : row[first_name_kor_index        ],
                col_last_name_kor         : row[last_name_kor_index         ],
                col_first_name_eng        : row[first_name_eng_index        ],
                col_middle_name_eng       : row[middle_name_eng_index       ],
                col_last_name_eng         : row[last_name_eng_index         ],
                col_dob                   : row[dob_index                   ],
                col_sex                   : row[sex_index                   ],
                col_room_number           : row[room_number_index           ],
                col_initial_assessment    : row[initial_assessment_index    ],
                col_assessment_14th       : row[assessment_14th_index       ],
                col_assessment_90th       : row[assessment_90th_index       ],
                col_change_assessment     : row[change_assessment_index     ],
                col_change_assessment_done: row[change_assessment_done_index],
                col_comments              : row[comments_index              ]
            }
        else:
            client={}
            for k_, r_ in zip(key, row):
                client[k_] = r_
       
        return client
    
    def load_all_clients(self):
        cur = self.conn.execute("SELECT * FROM clients")
        return [dict(self.row_to_client(row)) for row in cur.fetchall()]
    # -------------------
    # Searching
    # -------------------
    def get_rooms(self):
        cur = self.conn.execute("SELECT * FROM clients")
        return [row[room_number_index] for row in cur.fetchall()]

    def search_by_krname_roomnumber(self,f_name=None, l_name=None, r_number=None):
        query = "SELECT * FROM clients WHERE 1=1"
        params = []

        # Dynamically build the WHERE clause based on provided arguments
        if f_name:
            query += " AND first_name_kor LIKE ?"
            # The first name is assumed to be the first word in the English name column
            params.append(f"{f_name}%")
    
        if l_name:
            query += " AND last_name_kor LIKE ?"
            # The last name is assumed to be the last word in the English name column
            params.append(f"%{l_name}")
    
        if r_number:
            query += " AND room_number = ?"
            params.append(r_number)
            
        try:
            cur = self.conn.execute(query, params)
            results = [dict(self.row_to_client(row)) for row in cur.fetchall()]
            #cursor.fetchall()
            return results
        except sqlite3.Error as e:
            self.print_message.emit(f"Error (ClientDB::search_by_krname_roomnumber). Database error: {e}")
            return []
        
    def search_by_lastname_kr(self, last_name: str):
        cur = self.conn.execute("SELECT * FROM clients WHERE last_name_kor LIKE ?", (f"%{last_name}%",))
        return [dict(self.row_to_client(row)) for row in cur.fetchall()]
        
    def search_by_firstname_kr(self, first_name: str):
        cur = self.conn.execute("SELECT * FROM clients WHERE first_name_kor LIKE ?", (f"%{first_name}%",))
        return [dict(self.row_to_client(row)) for row in cur.fetchall()]
        
    def search_by_lastname_eng(self, last_name: str):
        cur = self.conn.execute("SELECT * FROM clients WHERE last_name_eng LIKE ?", (f"%{last_name}%",))
        return [dict(self.row_to_client(row)) for row in cur.fetchall()]

    def search_by_firstname_eng(self, first_name: str):
        cur = self.conn.execute("SELECT * FROM clients WHERE first_name_eng LIKE ?", (f"%{first_name}%",))
        return [dict(self.row_to_client(row)) for row in cur.fetchall()]

    def search_by_birth_year(self, year: str):
        cur = self.conn.execute("SELECT * FROM clients WHERE dob LIKE ?", (f"%/{year}",))
        return [dict(row) for row in cur.fetchall()]

    def search_by_rooms(self, room_):
        cur = self.conn.execute(f"SELECT * FROM clients WHERE room_number LIKE '{room_}'")
        return [dict(self.row_to_client(row)) for row in cur.fetchall()]
        
    def search_by_room(self, room_number: str):
        cur = self.conn.execute("SELECT * FROM clients WHERE room_number=?", (room_number,))
        return [dict(self.row_to_client(row)) for row in cur.fetchall()]
        
    def check_client_id_exists(self, client_id):
        """
        Checks if a client with the given client_id exists in the database.
        Returns True if the client exists, False otherwise.
        """
        cursor = self.conn.cursor()
    
        try:
            # Use a SELECT query with a WHERE clause to check for the client_id
            cursor.execute("SELECT 1 FROM clients WHERE client_id = ?", (client_id,))
            
            # fetchone() returns the first row or None if no rows were found.
            # We only need to check for existence, so 'SELECT 1' is efficient.
            result = cursor.fetchone()
            
            # If result is not None, it means a record was found
            return result is not None
        
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            return False
        
    def search_by_assessment_month(self, month: str):
        """month = '01', '02', ... '12'"""
        cur = self.conn.execute("""
            SELECT * FROM clients 
            WHERE (initial_assessment LIKE ? 
                OR assessment_14th LIKE ? 
                OR assessment_90th LIKE ?)
        """, (f"{month}/%", f"{month}/%", f"{month}/%"))
        return [dict(row) for row in cur.fetchall()]

    # -------------------
    # Special checks
    # -------------------
    def due_assessments_today(self):
        """Find clients missing 14th or 90th assessments"""
        today = datetime.today().strftime("%m/%d/%Y")

        cur = self.conn.execute("""
            SELECT * FROM clients
            WHERE (assessment_14th=? OR assessment_90th=?) 
              AND change_assessment_done=0
        """, (today, today))

        return [dict(row) for row in cur.fetchall()]

        
if __name__ == "__main__":
    from cidman import ClientID
    db = ClientDB()
    cm = ClientID()
    db.check()
    db.load_all_clients()
    
    # Add client
    #id0=cm.get("M", 201)
    #print(id0)
    #db.add_client({
    #    "client_id": id0,
    #    "pic_path": "",
    #    "last_name_kor": "홍",
    #    "first_name_kor": "길동",
    #    "first_name_eng": "Gil Dong",
    #    "middle_name_eng": None,
    #    "last_name_eng": "Hong",
    #    "dob": "08/20/1990",
    #    "sex": "M",
    #    "room_number": "201",
    #    "initial_assessment": "08/20/2025",
    #    "assessment_14th": "09/03/2025",
    #    "assessment_90th": "11/18/2025",
    #    "change_assessment": None,
    #    "change_assessment_done": 0,
    #    "comments": "New client"
    #})
    #id1=cm.get("F", 401)
    #print(id1)
    #db.add_client({
    #    "client_id": id1,
    #    "pic_path" : "",
    #    "last_name_kor": "김",
    #    "first_name_kor": "지혜",
    #    "first_name_eng": "Gihae",
    #    "middle_name_eng": None,
    #    "last_name_eng": "Kim",
    #    "dob": "08/20/1990",
    #    "sex": "F",
    #    "room_number": "401",
    #    "initial_assessment": "08/20/2025",
    #    "assessment_14th": "09/03/2025",
    #    "assessment_90th": "11/18/2025",
    #    "change_assessment": None,
    #    "change_assessment_done": 0,
    #    "comments": "New client"
    #})
    
   
    
    # Find by first name English
    print(db.search_by_lastname("Hong"))
    
    # Find due assessments
    #print(db.due_assessments_today())