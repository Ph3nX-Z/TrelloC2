import sqlite3
import glob
import datetime
import re
import base64


"""
CREATE TABLE agents(id VARCHAR PRIMARY KEY UNIQUE, displayname VARCHAR, user VARCHAR, ip_addr VARCHAR, sleep_time FLOAT, stage VARCHAR);
CREATE TABLE tasks(id VARCHAR PRIMARY KEY UNIQUE, agent_id VARCHAR, command_sent_base64 VARCHAR, output_base64 VARCHAR, status VARCHAR, date_launched_timestamp INT);
"""

class SqliteConnector:

    def __init__(self,db_file_path:str):
        self.db_file_path = db_file_path
    
    def db_exec(self,command:str):
        with sqlite3.connect(self.db_file_path,timeout=10) as con:
            cur = con.cursor()
            res = cur.execute(command)
            con.commit()
            output = res.fetchall()
            cur.close()
            #con.close()
        return output
    
    def append_agent(self,agent_id:str, displayname:str, user:str, ip_addr:str, sleep_time:float, stage:str):
        try:
            self.db_exec(f"""INSERT INTO agents VALUES ("{agent_id}","{displayname}","{user}","{ip_addr}",{sleep_time},"{stage}")""")
            print("[+] New Agent added to database")
            return True
        except Exception as err:
            if not "UNIQUE" in str(err):
                print("[-] ",err)
                return False
            else:
                print("[+] Agent already in database")
                return False

    def append_task(self,task_id:str,agent_id:str,command_sent):
        try:
            command_sent_b64 = base64.b64encode(command_sent.encode()).decode()
            self.db_exec(f"""INSERT INTO tasks VALUES ("{task_id}","{agent_id}","{command_sent_b64}","","queued","{datetime.datetime.now()}")""")
            return True
        except Exception as err:
            print("[-] ",err)
            return False

    def get_agents(self):
        return self.db_exec("""SELECT * FROM agents;""")
    
    def pass_task_in_progress(self,task_id:str):
        return self.db_exec(f"""UPDATE tasks SET status="in progress" WHERE id=="{task_id}";""")
    
    def get_tasks_for_agent(self,given_id:str):
        return self.db_exec(f"""SELECT * FROM tasks JOIN agents ON tasks.agent_id=agents.id WHERE agents.id LIKE "%{given_id}%" OR tasks.id LIKE "%{given_id}%";""")
    
    def get_tasks_for_agent_queued(self,given_id:str):
        return self.db_exec(f"""SELECT * FROM tasks JOIN agents ON tasks.agent_id=agents.id WHERE (agents.id LIKE "%{given_id}%" OR tasks.id LIKE "%{given_id}%") AND tasks.status=="queued";""")

    def set_output_for_task_id(self,task_id:str,output:str):
        return self.db_exec(f"""UPDATE tasks SET output_base64="{output}" WHERE id=="{task_id}";""")
    
    def set_user_and_ip(self,task_id:str,output:str):
        output = base64.b64decode(output).decode()
        #print(output)
        user = output.split(",")[0]
        #print(user)
        ip = output.split(",")[1]
        #print(ip)
        return self.db_exec(f"""UPDATE agents SET user="{user}",ip_addr="{ip}",stage="ready" WHERE id==(SELECT agents.id FROM agents JOIN tasks ON tasks.agent_id=agents.id WHERE tasks.id=="{task_id}");""")
    
    def pass_task_done(self,task_id:str):
        return self.db_exec(f"""UPDATE tasks SET status="done" WHERE id=="{task_id}";""")
    
    def get_command_by_id(self,task_id:str):
        try:
            return base64.b64decode(self.db_exec(f"""SELECT command_sent_base64 FROM tasks WHERE id=="{task_id}";""")[0][0]).decode()
        except:
            return ""

if __name__=="__main__":
    obj = SqliteConnector("./database/database.db")