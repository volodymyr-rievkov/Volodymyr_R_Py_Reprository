import requests

class NetworkHelper:

    __BASE_URL = "http://127.0.0.1:8888/"
    __USERNAME = "admin"
    __PASSWORD = "volodymyr"
    
    @classmethod
    def get_items(cls, items):
        url = f"{cls.__BASE_URL}/{items}/"
        response = requests.get(url, auth=(cls.__USERNAME, cls.__PASSWORD))
        if (response.status_code == 200):
            return response.json()  
        return None 

    @classmethod
    def get_item_by_id(cls, items, item_id):
        url = f"{cls.__BASE_URL}/{items}/{item_id}/"
        response = requests.get(url, auth=(cls.__USERNAME, cls.__PASSWORD))
        if (response.status_code == 200):
            return response.json()  
        return None 

    @classmethod
    def delete_item(cls, items, item_id):
        url = f"{cls.__BASE_URL}/{items}/{item_id}/"
        response = requests.delete(url, auth=(cls.__USERNAME, cls.__PASSWORD))  
        if (response.status_code == 204):  
            return True
        return False 
     