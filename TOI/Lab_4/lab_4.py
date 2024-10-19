from collections import Counter 
from decimal import Decimal, getcontext

getcontext().prec = 50

def get_probs_dict(message):
    n = len(message)
    symbol_dict = Counter(message)
    probs_dict = {symbol: Decimal(count) / Decimal(n) for symbol, count in symbol_dict.items()}
    return probs_dict

def get_intervals_dict(probs_dict):
    intervals_dict = dict()
    prob = Decimal(0.0)
    for s, p in probs_dict.items():
        low = prob
        high = prob + Decimal(p)
        intervals_dict[s] = (low, high)
        prob = high
    return intervals_dict

def arithmetic_coding(message, intervals_dict):
    low = Decimal(0.0)
    high = Decimal(1.0)
    code_list = list()
    for s in message:
        width = high - low
        high = low + width * intervals_dict[s][1]
        low = low + width * intervals_dict[s][0]
        code_list.append((s, low, high))
    return Decimal((low + high) / 2), code_list

def arithmetic_decoding(value, intervals_dict, mess_len):
    decode_list = list()
    for _ in range(mess_len):
        for symbol, (low, high) in intervals_dict.items():
            if low <= value < high:
                decode_list.append((symbol, value, low, high))
                value = (value - low) / (high - low)
                break
    return decode_list

def print_table_1(intervals_dict):
    print("---------------- Table for sequence ----------------")
    print(" ___________________________________________________")
    print("| Symbol | Probability | Lower Bound | Upper Bound  |")
    print("|--------|-------------|-------------|--------------|")
    for symbol, (low, high) in intervals_dict.items():
        symbol_display = f" {symbol} ".ljust(8)
        prob = f"{high - low:.5f}".center(13)
        lower_bound = f"{low:.5f}".center(13)
        higher_bound = f"{high:.5f}".center(14)
        print(f"|{symbol_display}|{prob}|{lower_bound}|{higher_bound}|")
        print("|--------|-------------|-------------|--------------|")
    print()    

def print_table_2(code_list):
    print("---------------- Arithmetic Coding ----------------")
    print(" __________________________________________________")
    print("| Symbol |    Lower Bound     |    Upper Bound     |")
    print("|--------|--------------------|--------------------|")
    for row in code_list:
        symbol, low, high = row
        symbol_display = f" {symbol} ".ljust(8)
        low_bound = f" {low:.16f} ".center(13)
        high_bound = f" {high:.16f} ".center(14)
        print(f"|{symbol_display}|{low_bound}|{high_bound}|")
        print("|--------|--------------------|--------------------|")
    print()

def print_table_3(decode_list):
    print("--------------------- Arithmetic Decoding ---------------------")
    print(" _____________________________________________________________")
    print("| Symbol |        Code        |  Lower Bound  |  Upper Bound  |")
    print("|--------|--------------------|---------------|---------------|")
    for row in decode_list:
        symbol, code, low, high = row
        symbol_display = f" {symbol} ".center(8)
        code_value = f" {code:.16f} ".center(16)
        low_bound = f" {low:.5f} ".center(15)
        high_bound = f" {high:.5f} ".center(15)
        print(f"|{symbol_display}|{code_value}|{low_bound}|{high_bound}|")
        print("|--------|--------------------|---------------|---------------|")
    print()   

message = "Rievkov Volodymyr Volodymyrovych"
sequence = get_probs_dict(message)
i_sequence = get_intervals_dict(sequence)
print_table_1(i_sequence)
code_m, encoded_m = arithmetic_coding(message, i_sequence)
print_table_2(encoded_m)
decoded_m = arithmetic_decoding(code_m, i_sequence, len(message))
print_table_3(decoded_m)

sequence_x = {"X1": 0.10, "X2": 0.09, "X3": 0.19, "X4": 0.10, "X5": 0.04, "X6": 0.13, "X7": 0.08, "X8": 0.10, "X9": 0.09, "X10": 0.08}
i_sequence_x = get_intervals_dict(sequence_x)
print_table_1(i_sequence_x)

message_5 = ["X1", "X7", "X6", "X2", "X4"]
code_m_5, encoded_m_5 = arithmetic_coding(message_5, i_sequence_x)
print_table_2(encoded_m_5)
decoded_m_5 = arithmetic_decoding(code_m_5, i_sequence_x, len(message_5))
print_table_3(decoded_m_5)

message_10 = ["X5", "X9", "X2", "X3", "X7", "X2", "X8", "X2", "X10", "X9"]
code_m_10, encoded_m_10 = arithmetic_coding(message_10, i_sequence_x)
print_table_2(encoded_m_10)
decoded_m_10 = arithmetic_decoding(code_m_10, i_sequence_x, len(message_10))
print_table_3(decoded_m_10)