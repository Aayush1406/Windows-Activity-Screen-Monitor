import pypyodbc as odbc
import pyodbc
from mysql.connector import pooling
from datetime import datetime
import pytz
import requests

class DatabaseManager:
    
    def __init__(self):
        
        self.connection_pool = pooling.MySQLConnectionPool(
            
            pool_name = "mypool",
            host="database-1.czyq6yq0ownh.us-east-1.rds.amazonaws.com",  
            user="aayush",  
            password="aayush140620",  
            database="device_data"      
        
        )
    
    def get_connection(self):
        
        return self.connection_pool.get_connection()    
    
    #Legit            
    def dump_keyListener_session_to_db(self,current_session_id,idle_time):
        try:
        
            conn = self.get_connection()
            cursor = conn.cursor() 
            insert_query = """
            INSERT INTO keylogger (Session_ID, Idle_Time) 
            VALUES (%s, %s)
            """
            data = (current_session_id, idle_time)
            cursor.execute(insert_query, data)
            conn.commit()

        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()        
        
        
    # Legit           
    def dump_mouseListener_session_to_db(self,current_session_id,idle_time):
        try:
        
            conn = self.get_connection()
            cursor = conn.cursor() 
            insert_query = """
            INSERT INTO mouselogger (Session_ID, Idle_Time) 
            VALUES (%s, %s)
            """
            data = (current_session_id, idle_time)
            cursor.execute(insert_query, data)
            conn.commit()
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()                 

    # Legit
    def insert_window_start_db(self, foreground_details_dict):
        try:
            # 3/6 
            # print(foreground_details_dict.get('window_title'),foreground_details_dict.get('child_name'), foreground_details_dict.get('executable_path'),
            #                             foreground_details_dict.get('process_name'),foreground_details_dict.get('process_status'),foreground_details_dict.get('process_create_time'),
            #                             foreground_details_dict.get('current_pid'), foreground_details_dict.get('current_handle'), None,foreground_details_dict.get('window_start_time'))
            
            conn = self.get_connection()
            cursor = conn.cursor()    
            insert_query = """ 
            INSERT INTO device_data.applicationusagelogs(Window_Title, Child_Name, Executable_Path, Process_Name, Process_Status, Process_Create_Time ,Process_id, Current_Handle, Duration, Window_Start_Time, Window_End_Time, Window_Active_Status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s ,%s , %s, %s ) """
            cursor.execute(insert_query,(foreground_details_dict.get('window_title'),foreground_details_dict.get('child_name'), foreground_details_dict.get('executable_path'),
                                        foreground_details_dict.get('process_name'),foreground_details_dict.get('process_status'),foreground_details_dict.get('process_create_time'),
                                        foreground_details_dict.get('current_pid'), foreground_details_dict.get('current_handle'), None,foreground_details_dict.get('window_start_time') , None, 'Active' ))
            
            # print("Start_Time = ",foreground_details_dict.get('window_start_time')) 3/6
            

            conn.commit()
            print("record inserted into db successfully !")
            
        except Exception as e:
            print(f"Error = {e}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
                return cursor.lastrowid
            
            
    #Legit
    def update_window_end_db(self, current_session_id, end_time, duration):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()    
            update_query = """ update applicationusagelogs set Window_End_Time = %s, Duration = %s, Window_Active_Status = %s  where id = %s """
            cursor.execute(update_query,(end_time, duration,'Inactive', current_session_id))
            conn.commit()
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
                
        