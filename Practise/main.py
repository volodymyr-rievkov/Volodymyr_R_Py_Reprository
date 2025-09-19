# dict_ = {'a': 8, 'b': 10, 'c': 4}

# first_max = float("-inf")
# first_max_key = None
# second_max = float("-inf")
# second_max_key = None

# for key, value in dict_.items():
#     if(value > first_max):
#         second_max_key = first_max_key
#         second_max = first_max
#         first_max = value
#         first_max_key = key
#     elif(value > second_max):
#         second_max = value
#         second_max_key = key
#     max = {first_max_key: first_max, second_max_key: second_max}
# print(max)


# from math import sqrt

# def is_prime(n):
#     if(n <= 1):
#         return False
#     if(n <= 3):
#         return True
    
#     sqrt_num = int(sqrt(n)) + 1
#     for i in range(2, sqrt_num):
#         if(n % i == 0):
#             return False
#     return True

# print(is_prime(12))


# from math import ceil

# def is_palindrome(str):
#     return str == str[::-1]

# def is_palindrome_manual(str):
#     l = len(str) - 1
#     for i in range(ceil(l / 2)):
#         if(str[i] != str[l - i]):
#             return False
#     return True

# print(is_palindrome("potop"))
# print(is_palindrome_manual("potop"))


# import time

# def count_time(func):
#     def wrapper(*args, **kwargs):
#         start_time = time.time()
#         func(*args, **kwargs)
#         end_time = time.time()
#         print(f"Function worked {end_time - start_time} s.")
#     return wrapper

# @count_time
# def fibonacci(n):
#      if(n < 2):
#         return n
#      else:
#         a, b = 0, 1
#         for _ in range(n + 1):
#             a, b = b, a + b
#         return b

# fibonacci(100000)


# def error_catcher(func):
#     def wrapper(*args, **kwargs):
#         try:
#             result = func(*args, **kwargs)
#         except Exception as e:
#             print(f"Error: {e}!")
#         else:
#             print(result)
#             print("Successful func performing.")
#         finally:
#             print("Finishing error catching.")
#     return wrapper

# @error_catcher
# def two_nums_divider(a, b):
#     return a / b

# print(two_nums_divider(1, 1))


# def find_max(nested_list):
#     maximum = float("-inf")
#     for element in nested_list:
#         if(isinstance(element, (int, float))):
#             maximum = max(maximum, element)
#         elif(isinstance(element, list)):
#             maximum = max(maximum, find_max(element))
#     return maximum

# nested_list = [1, [2, 3], [4, [5, 6], 7], 8, 9] 
# print("Max:", find_max(nested_list))


# def find_sum(nested_list):
#     sum = 0
#     for element in nested_list:
#         if(isinstance(element, (int, float))):
#             sum += element
#         elif(isinstance(element, list)):
#             sum += find_sum(element)
#     return sum

# nested_list = [1, [2, 3], [4, [5, 6], 7], 8, 9] 
# print("Sum:", find_sum(nested_list))

lst = [1, 9, 3, 6, 2, 5, 0, 1]

def bubble_sort(lst):
    l = len(lst)
    for i in range(l):
        for j in range(l - i - 1):
            if(lst[j] > lst[j + 1]):
                lst[j], lst[j + 1] = lst[j + 1], lst[j]
    return lst

# def selection_sort(lst):
#     l = len(lst)
#     for i in range(l):
#         for j in range(i, l):
#             if(lst[i] > lst[j]):
#                 lst[i], lst[j] = lst[j], lst[i]
#     return lst
    
# from math import ceil

# def reverse(lst):
#     l = len(lst) - 1
#     for i in range(ceil(l / 2)):
#         lst[i], lst[l - i] = lst[l - i], lst[i]
#     return lst

# print(bubble_sort(lst))    
# print(selection_sort(lst)) 
# print(reverse(lst))   

# from math import ceil

# def binary_search(sorted_list, n):
#     left = 0
#     right = len(sorted_list) - 1
#     while(left <= right):
#         mid = (left + right) // 2
#         if(sorted_list[mid] == n):
#             return mid
#         elif(sorted_list[mid] < n):
#             left = mid + 1
#         else:
#             right = mid - 1
#     return None

# print(binary_search(bubble_sort(lst), 1))


# def factorial(n):
#     if(n <= 1):
#         return 1
#     else:
#         result = 1
#         while(n != 0):
#             result *= n
#             n -= 1
#         return result

# print(factorial(5))

class User():

    def __init__(self, name, age, password, country):
        self.name = name
        self.age = age
        self.password = password
        self.country = country

    def __str__(self):
        return f"Hello my name is {self.name}, \nI am {self.age} years old, \nI am from {self.country}."

import random
import time

class Worker(User):
    def __init__(self, name, age, password, country):
        self.__WORKS = ["repairing", "building", "cleaning"]
        super().__init__(name, age, password, country)

    def __str__(self):
        return super().__str__() + "\nI am Worker."
    
    def start_work(self):
        self.__current_work = random.choice(self.__WORKS)
        self.__start_time = time.time()
        print(f"Worker {self.name} started {self.__current_work}.")

    def end_work(self):
        self.__end_time = time.time()
        print(f"Worker {self.name} ended {self.__current_work} through {round(self.__end_time - self.__start_time, 2)} s.")
        self.__current_work = None



worker = Worker("Chris", 24, "sdkjskjdl", "USA")
print(worker)
worker.start_work()
time.sleep(2)
worker.end_work()

