from pymongo import MongoClient
from bson import ObjectId

CLIENT = MongoClient("mongodb://localhost:27017/")

db = CLIENT['shop']

users_collection = db['users']
products_collection = db['products']
discounts_collections = db['discounts']
deliveries_collection = db['deliveries']
orders_collections = db['orders']

def insert_object_into(collection, object):
    try:
        result = collection.insert_one(object)
        print(f"Object with ID: {result.inserted_id} was inserted into collection '{collection.name}'")
    except Exception as e:
        print(f"Error: {e}")

def remove_object_from(collection, object_id):
    try:
        object_id = ObjectId(object_id)
        result = collection.delete_one({"_id": object_id})
        if result.deleted_count > 0:
            print(f"Object with ID: {object_id} was successfully deleted from collection '{collection.name}'.")
        else:
            print(f"Object with ID: {object_id} not found in collection '{collection.name}'.")
    except Exception as e:
        print(f"Error: {e}")

def update_object_in(collection, object_id, update_fields):
    try:
        object_id = ObjectId(object_id)  
        result = collection.update_one(
            {"_id": object_id},  
            {"$set": update_fields}  
        )
        
        if result.matched_count > 0:
            print(f"Object with ID: {object_id} was successfully updated.")
        else:
            print(f"Object with ID: {object_id} not found or nothing changed.")
    
    except Exception as e:
        print(f"Error: {e}")

user_1 = {'first_name': 'John', 'last_name': 'Doe', 'email': 'john_doe@gmail.com', 'phone_number': '171832647634', 'password': 'john_doe'}
user_2 = {'first_name': 'Tom', 'last_name': 'Cruise', 'email': 'tom_cruise@gmail.com', 'phone_number': '82774837324', 'password': 'tom_cruise'}
#insert_object_into(users_collection, user_1)

user_id = users_collection.find_one({'first_name': 'Bob'})['_id']
#remove_object_from(users_collection, user_id)

update_user = {'first_name': 'Chris'}
#update_object_in(users_collection, user_id, update_user)

