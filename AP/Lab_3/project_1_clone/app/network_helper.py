import requests

class NetworkHelper:

    def get_items(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()  
        return None 

    def get_item_by_id(self, url, item_id):
        response = requests.get(f"{url}/{item_id}")
        if response.status_code == 200:
            return response.json()  
        return None 

    def delete_item(self, url, item_id):
        response = requests.delete(f"{url}/{item_id}")  
        if response.status_code == 204:  
            return True
        return False  