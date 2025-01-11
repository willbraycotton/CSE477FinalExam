import mysql.connector
import glob
import json
import csv
from io import StringIO
import itertools
import hashlib
import os
import cryptography
from cryptography.fernet import Fernet
from math import pow

class database:

    def __init__(self, purge = False):

        # Grab information from the configuration file
        self.database       = 'db'
        self.host           = '127.0.0.1'
        self.user           = 'master'
        self.port           = 3306
        self.password       = 'master'
        self.tables         = [ 'users','boards','user_boards','cards']
        
        # NEW IN HW 3-----------------------------------------------------------------
        self.encryption     =  {   'oneway': {'salt' : b'averysaltysailortookalongwalkoffashortbridge',
                                                 'n' : int(pow(2,5)),
                                                 'r' : 9,
                                                 'p' : 1
                                             },
                                'reversible': { 'key' : '7pK_fnSKIjZKuv_Gwc--sZEMKn2zc8VvD6zS96XcNHE='}
                                }
        #-----------------------------------------------------------------------------

    def query(self, query = "SELECT * FROM users", parameters = None):

        cnx = mysql.connector.connect(host     = self.host,
                                      user     = self.user,
                                      password = self.password,
                                      port     = self.port,
                                      database = self.database,
                                      charset  = 'latin1'
                                     )


        if parameters is not None:
            cur = cnx.cursor(dictionary=True)
            cur.execute(query, parameters)
        else:
            cur = cnx.cursor(dictionary=True)
            cur.execute(query)

        # Fetch one result
        row = cur.fetchall()
        cnx.commit()

        if "INSERT" in query:
            cur.execute("SELECT LAST_INSERT_ID()")
            row = cur.fetchall()
            cnx.commit()
        cur.close()
        cnx.close()
        return row

    def createTables(self, purge=False, data_path = 'flask_app/database/'):
        ''' FILL ME IN WITH CODE THAT CREATES YOUR DATABASE TABLES.'''

        #should be in order or creation - this matters if you are using forign keys.
         
        if purge:
            for table in self.tables[::-1]:
                self.query(f"""DROP TABLE IF EXISTS {table}""")
            
        # Execute all SQL queries in the /database/create_tables directory.
        for table in self.tables:
            
            #Create each table using the .sql file in /database/create_tables directory.
            with open(data_path + f"create_tables/{table}.sql") as read_file:
                create_statement = read_file.read()
            self.query(create_statement)

            # Import the initial data
            try:
                params = []
                with open(data_path + f"initial_data/{table}.csv") as read_file:
                    scsv = read_file.read()            
                for row in csv.reader(StringIO(scsv), delimiter=','):
                    params.append(row)
            
                # Insert the data
                cols = params[0]; params = params[1:] 
                self.insertRows(table = table,  columns = cols, parameters = params)
            except:
                print('no initial data')

    def insertRows(self, table='table', columns=['x','y'], parameters=[['v11','v12'],['v21','v22']]):
        
        # Check if there are multiple rows present in the parameters
        has_multiple_rows = any(isinstance(el, list) for el in parameters)
        keys, values      = ','.join(columns), ','.join(['%s' for x in columns])
        
        # Construct the query we will execute to insert the row(s)
        query = f"""INSERT IGNORE INTO {table} ({keys}) VALUES """
        if has_multiple_rows:
            for p in parameters:
                query += f"""({values}),"""
            query     = query[:-1] 
            parameters = list(itertools.chain(*parameters))
        else:
            query += f"""({values}) """                      
        
        insert_id = self.query(query,parameters)[0]['LAST_INSERT_ID()']         
        return insert_id



#######################################################################################
# AUTHENTICATION RELATED
#######################################################################################
    def createUser(self, email='me@email.com', password='password', role='user'):
        query = "INSERT INTO users (role, email, password) VALUES (%s, %s, %s)"
        self.query(query, (role, email, self.onewayEncrypt(password)))
        return {'success': 1}

    def authenticate(self, email='me@email.com', password='password'):
        query = "SELECT * FROM users WHERE email = %s AND password = %s"
        result = self.query(query, (email, password))
        if result:
            return {'success': 1}
        else:
            return {'success': 0}

    def onewayEncrypt(self, string):
        encrypted_string = hashlib.scrypt(string.encode('utf-8'),
                                          salt = self.encryption['oneway']['salt'],
                                          n    = self.encryption['oneway']['n'],
                                          r    = self.encryption['oneway']['r'],
                                          p    = self.encryption['oneway']['p']
                                          ).hex()
        return encrypted_string


    def reversibleEncrypt(self, type, message):
        fernet = Fernet(self.encryption['reversible']['key'])
        
        if type == 'encrypt':
            message = fernet.encrypt(message.encode())
        elif type == 'decrypt':
            message = fernet.decrypt(message).decode()

        return message


    def get_user_boards(self, user_email):
        conn = self.get_conn()
        cur = conn.cursor()
        
        cur.execute("SELECT id FROM users WHERE email = ?", (user_email,))
        user_id = cur.fetchone()
        
        if user_id:
            cur.execute("""
                SELECT b.id, b.name FROM boards b
                INNER JOIN user_boards ub ON b.id = ub.board_id
                WHERE ub.user_id = ?
            """, (user_id[0],))
            
            boards = cur.fetchall()
            cur.close()
            return [{'id': board[0], 'name': board[1]} for board in boards]
        else:
            cur.close()
            return [] 

    def create_board(self, board_name, member_emails, owner_email):
        try:
            board_id = self.query("INSERT INTO boards (name) VALUES (%s)", (board_name,))[0]["LAST_INSERT_ID()"]

            if not board_id:
                raise Exception("Failed to create board or retrieve new board ID.")

            owner_results = self.query("SELECT user_id FROM users WHERE email = %s", (owner_email,))

            owner_id = owner_results[0]['user_id'] if owner_results else None

            if not owner_id:
                raise Exception("Owner email not found in database.")

            self.query("INSERT INTO user_boards (user_id, board_id) VALUES (%s, %s)", (owner_id, board_id))
            

            for email in member_emails:
                member_results = self.query("SELECT user_id FROM users WHERE email = %s", (email,))
                if member_results:
                    member_id = member_results[0]['user_id']
                    self.query("INSERT INTO user_boards (user_id, board_id) VALUES (%s, %s)", (member_id, board_id))
            
            return board_id
        except Exception as e:
            print("An error occurred:", e)
            return None