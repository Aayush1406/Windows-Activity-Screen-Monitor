import pypyodbc as odbc
import pyodbc
from mysql.connector import pooling
from datetime import datetime
import pytz

class DatabaseManager:
    
    def __init__(self):
        
        self.connection_pool = pooling.MySQLConnectionPool(
            
            pool_name = "",
            host="",  
            user="",  
            password="",  
            database=""      
        
        )
    
    def get_connection(self):
        
        return self.connection_pool.get_connection()    

    def insert_foreground_process_details_in_db(self,foreground_process_details_dict):
        try:
            print("++++++++++++++++++++Here++++++++++++++++++++")
            conn = self.get_connection()
            cursor = conn.cursor()    
            insert_query = """ 
            INSERT INTO applicationusagelogs(Window_Title, Child_Name, Executable_Path, Process_Name, Process_Status, Process_Create_Time ,Process_id, Current_Handle, Duration, Window_Start_Time, Window_End_Time, Window_Active_Status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s ,%s , %s, %s ) """
            cursor.execute(insert_query,(foreground_process_details_dict['window_title'],foreground_process_details_dict['child_name'], foreground_process_details_dict['executable_path'],
                                        foreground_process_details_dict['process_name'],foreground_process_details_dict['process_status'],foreground_process_details_dict['process_create_time'],
                                        foreground_process_details_dict['current_pid'], foreground_process_details_dict['current_handle'], None, None, None, None ))
            conn.commit()
            print("record inserted into db successfully !")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
                
    def dump_keyListener_session_to_db(self,current_session_id,idle_time):
        try:
        
            conn = self.get_connection()
            cursor = conn.cursor() 
            # Insert the idle time data into the Keylogger table
            insert_query = """
            INSERT INTO keylogger (Session_ID, Idle_Time) 
            VALUES (%s, %s)
            """
            data = (current_session_id, idle_time)
            cursor.execute(insert_query, data)
            conn.commit()
            # print(f"Inserted session data (Session_ID: {self.current_session_id}, Idle_Time: {idle_time}) into the database")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close() 
                
    def dump_mouseListener_session_to_db(self,current_session_id,idle_time):
        try:
        
            conn = self.get_connection()
            cursor = conn.cursor() 
            # Insert the idle time data into the Keylogger table
            insert_query = """
            INSERT INTO mouselogger (Session_ID, Idle_Time) 
            VALUES (%s, %s)
            """
            data = (current_session_id, idle_time)
            cursor.execute(insert_query, data)
            conn.commit()
            # print(f"Inserted session data (Session_ID: {self.current_session_id}, Idle_Time: {idle_time}) into the database")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()                 

    def insert_window_start_db(self, foreground_details_dict):
        try:
            
            print(foreground_details_dict.get('window_title'),foreground_details_dict.get('child_name'), foreground_details_dict.get('executable_path'),
                                        foreground_details_dict.get('process_name'),foreground_details_dict.get('process_status'),foreground_details_dict.get('process_create_time'),
                                        foreground_details_dict.get('current_pid'), foreground_details_dict.get('current_handle'), None,foreground_details_dict.get('window_start_time'))
            
            conn = self.get_connection()
            cursor = conn.cursor()    
            insert_query = """ 
            INSERT INTO device_data.applicationusagelogs(Window_Title, Child_Name, Executable_Path, Process_Name, Process_Status, Process_Create_Time ,Process_id, Current_Handle, Duration, Window_Start_Time, Window_End_Time, Window_Active_Status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s ,%s , %s, %s ) """
            cursor.execute(insert_query,(foreground_details_dict.get('window_title'),foreground_details_dict.get('child_name'), foreground_details_dict.get('executable_path'),
                                        foreground_details_dict.get('process_name'),foreground_details_dict.get('process_status'),foreground_details_dict.get('process_create_time'),
                                        foreground_details_dict.get('current_pid'), foreground_details_dict.get('current_handle'), None,foreground_details_dict.get('window_start_time') , None, 'Active' ))
            
            print("Start_Time = ",foreground_details_dict.get('window_start_time'))
            

            conn.commit()
            print("record inserted into db successfully !")
            
        except Exception as e:
            print(f"Error = {e}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
                return cursor.lastrowid
    
    def update_window_end_db(self, current_session_id, end_time, duration):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()    
            update_query = """ update applicationusagelogs set Window_End_Time = %s, Duration = %s, Window_Active_Status = %s  where id = %s """
            cursor.execute(update_query,(end_time, duration,'Inactive', current_session_id))
            conn.commit()
            # print("record inserted into db successfully !")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
                
        

    def insert_window_end_time_in_db(self,old_pid):
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor() 
            select_query = "SELECT * FROM applicationusagelogs WHERE Process_id = %s and Window_Active_Status = %s"
            cursor.execute(select_query, (old_pid,'Active'))
            record_value = cursor.fetchone()
            
            if record_value:
                update_query = "Update applicationusagelogs set Window_End_Time = %s where Process_id = %s and Window_Active_Status=%s"
                current_time = datetime.now(pytz.UTC)
            
                cursor.execute(update_query, (current_time, old_pid,'Active'))
                conn.commit()
            
                print("Window End Time = ", current_time)
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close() 
        
      

    def insert_window_start_time_in_db(self, current_pid):

        try:
            conn = self.get_connection()
            cursor = conn.cursor() 
            update_query = "Update ApplicationUsageLogs set Window_Start_Time = %s where Process_id = %s and Window_Active_Status = %s"
            current_time = datetime.now(pytz.UTC)
            cursor.execute(update_query,(current_time, current_pid,'Active'))
            conn.commit()       
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def insert_window_status_to_active_in_db(self, current_pid):

        try:
            conn = self.get_connection()
            cursor = conn.cursor()     
            update_query = "Update ApplicationUsageLogs set Window_Active_Status = %s where Process_id = %s and Window_Start_Time is Null"
            cursor.execute(update_query,('Active',current_pid))
            conn.commit()

        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()        

    def insert_window_status_to_inactive_in_db(self, old_pid):

        try:
            conn = self.get_connection()
            cursor = conn.cursor()     
            update_query = "Update ApplicationUsageLogs set Window_Active_Status = %s where Process_id = %s and Window_End_Time is Not Null"
            cursor.execute(update_query,('Inactive',old_pid))
            conn.commit()
        
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()   
                

    def insert_process_status_in_db(self,old_pid,process_name):
       
        try:
            conn = self.get_connection()
            cursor = conn.cursor()     
            select_query = "SELECT * FROM applicationusagelogs WHERE Process_id = %s"
            cursor.execute(select_query, (old_pid,))
            record_value = cursor.fetchall()

            if record_value and process_name=="No Such Process":   
                
                update_select_query = """UPDATE ApplicationUsageLogs AS t1
                                        JOIN (
                                            SELECT Process_id, MAX(Window_End_Time) AS max_end_time
                                            FROM ApplicationUsageLogs
                                            WHERE Process_id = %s
                                            GROUP BY Process_id
                                        ) AS t2
                                        ON t1.Process_id = t2.Process_id AND t1.Window_End_Time = t2.max_end_time
                                        SET t1.Process_Status = %s;
                                        """   
                cursor.execute(update_select_query,(old_pid,"Stopped"))
                conn.commit()        
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()               

    def set_process_duration_in_db(self,old_pid):

        try:
            conn = self.get_connection()
            cursor = conn.cursor()     
            select_query = "Select Window_Start_Time, Window_End_Time from ApplicationUsageLogs where Process_id = %s and Window_Active_Status = %s"
            cursor.execute(select_query, (old_pid,'Active'))
            rows = cursor.fetchall()
            duration = None
            if rows:
                for row in rows:                    
                    window_start_time = row[0]             
                    window_end_time = row[1]
                    
                    duration = window_end_time - window_start_time
                    print("duration = ",duration)
        
                update_query = "Update ApplicationUsageLogs set duration = %s where Process_id = %s and Window_Active_Status = %s"            
                cursor.execute(update_query,(duration,old_pid,'Active'))
                conn.commit()
            

        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()                
    