
def lz78_encode(message):

    dictionary = dict()
    dict_index = 1
    string = ""

    for char in message:
        value = string + char
        if(value not in dictionary):
            if(string == ""):
                dictionary[value] = (dict_index, (0, char))
            else:
                dictionary[value] = (dict_index, (dictionary[string][0], char))

            dict_index += 1
            string = ""
        else:
            string = value
            
    if (string != ""):
        value = string + "EOF"
        dictionary[value] = (dict_index, (dictionary[string][0], "EOF"))

    return dictionary

def calculate_average_length(dictionary):
    total_length = sum(len(value) for value in dictionary.keys())
    average_length = total_length / len(dictionary) if (dictionary) else 0
    return average_length

def print_encode_table(dictionary):

    print("----------- Table for LZ78 Encoding -----------")
    print(" __________________________________________________")
    print("|  Index  |  Value  | Mark (Prev Index, Last Char) |")
    print("|---------|---------|------------------------------|")

    for value, (index, (prev_index, last_char)) in dictionary.items():
        value_display = f" {value} ".center(9)  
        index_display = f"{index}".center(9)    
        label_display = f"({prev_index}, '{last_char}')".center(30)  

        print(f"|{index_display}|{value_display}|{label_display}|")
        print("|---------|---------|------------------------------|")
    
    print("Average length code value:", round(calculate_average_length(dictionary), 3))
    print()

MESSAGE_1 = "RievkovRievkov"
encode_dict_1 = lz78_encode(MESSAGE_1)
print_encode_table(encode_dict_1)

MESSAGE_2 = "The quick brown fox jumps over the lazy dog while the sun sets in the horizon, painting the sky with shades of orange and pink."
encode_dict_2 = lz78_encode(MESSAGE_2)
print_encode_table(encode_dict_2)

MESSAGE_3 = "ljskd flaksj djslkf asdf jalksd fjlkasj dfkj aowje kfjsd alskd jwerq lkjhadf qweir uijwer lkjd fjasl aokwej kjdfa laksd"
encode_dict_3 = lz78_encode(MESSAGE_3)
print_encode_table(encode_dict_3)