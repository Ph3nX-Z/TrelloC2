import requests
import sys

class TrelloAPI:

    """
    https://trello.com/1/connect?key=yourkey&name=your_board_name&expiration=never&response_type=token&scope=read,write
    """

    def __init__(self,api_key:str,token:str,dashboard_id:str,base_url:str|None=None)->object:
        self.api_key = api_key
        self.token = token
        self.dashboard_id = dashboard_id
        self.params = {'key': api_key,'token': token}
        self.base_url = base_url or "https://api.trello.com/1"

    
    def __do_get_request(self,uri:str)->dict:
        request_output = requests.get(self.base_url+uri,params=self.params)
        try:
            return request_output.json()
        except requests.exceptions.JSONDecodeError as error:
            print(request_output.content,"\n",error)
            return False
    
    def __do_put_request(self,uri:str,data:dict)->dict:
        for key in self.params.keys():
            data[key]=self.params[key]
        request_output = requests.put(self.base_url+uri,params=data)
        try:
            return request_output.json()
        except requests.exceptions.JSONDecodeError as error:
            print(request_output.content,"\n",error)
            return False

    def get_all_card(self)->dict:
        return self.__do_get_request(f"/boards/{self.dashboard_id}/cards")
    
    def get_card_by_id(self,card_id:str)->dict:
        return self.__do_get_request(f"/cards/{card_id}")
    
    def get_cards_by_names(self,names:list)->list:
        all_cards = self.get_all_card()
        list_valid_cards = []
        for card in all_cards:
            if card["name"].lower() in [name.lower() for name in names]:
                list_valid_cards.append(card)
        return list_valid_cards
    
    def get_cards_by_name_contains(self,keyword:str)->dict:
        all_cards = self.get_all_card()
        list_valid_cards = []
        for card in all_cards:
            if keyword.lower() in card["name"].lower():
                list_valid_cards.append(card)
        return list_valid_cards
    
    def post_comment_on_card(self,card_id:str,comment:str)->dict:
        return self.__do_put_request(f"/cards/{card_id}",{"desc":comment})
    
    def post_comment_on_card_by_name(self,card_name:str,comment:str)->bool:
        all_cards = self.get_all_card()
        written = False
        for card in all_cards:
            if card["name"].lower() == card_name.lower():
                self.post_comment_on_card(card["shortLink"],comment)
                written = True
        return written

