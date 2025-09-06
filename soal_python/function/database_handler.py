import mysql.connector
from mysql.connector import Error

class DatabaseManager:
    def __init__(self, host='localhost', user='root', password='', database='ProjectDB', port=3306):
        self.config = {
            'host': host,
            'user': user,
            'password': password,
            'database': database,
            'port': port
        }
        self.connection = None
        
    def connect(self):
        """Membuat koneksi ke database"""
        try:
            self.connection = mysql.connector.connect(**self.config)
            return self.connection
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return None
    
    def disconnect(self):
        """Menutup koneksi database"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
    
    def execute_query(self, query, params=None):
        """Menjalankan query dengan parameter"""
        try:
            connection = self.connect()
            if connection:
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, params)
                
                if query.strip().lower().startswith('select'):
                    result = cursor.fetchall()
                else:
                    connection.commit()
                    result = cursor.rowcount
                
                cursor.close()
                self.disconnect()
                return result
            return None
        except Error as e:
            print(f"Error executing query: {e}")
            return None
    
    def initialize_database(self):
        """Membuat database dan tabel jika belum ada"""
        try:
            # Create database if not exists
            temp_config = self.config.copy()
            temp_config.pop('database')
            
            connection = mysql.connector.connect(**temp_config)
            cursor = connection.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.config['database']}")
            cursor.close()
            connection.close()
            
            # Create table
            create_table_query = """
            CREATE TABLE IF NOT EXISTS nodeDB (
                id VARCHAR(10) PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                updated_at DATETIME NOT NULL
            )
            """
            self.execute_query(create_table_query)
            return True
        except Error as e:
            print(f"Error initializing database: {e}")
            return False