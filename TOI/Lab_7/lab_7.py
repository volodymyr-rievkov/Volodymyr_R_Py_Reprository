import random
from collections import Counter
from math import ceil, log2

class node:
    def __init__(self, probability, symbol = None, left = None, right = None):
        self.probability = probability
        self.symbol = symbol
        self.left = left
        self.right = right

def get_probs_dict(text):
    n = len(text)
    symbol_dict = Counter(text)
    probs_dict = {symbol: count / n for symbol, count in symbol_dict.items()}
    return probs_dict

def get_codes(node, code = "", codes = dict()):
    if(node.symbol is not None):
        codes[node.symbol] = code
    else:
        if(node.left is not None):
            get_codes(node.left, code + '0', codes)
        if(node.right is not None):
            get_codes(node.right, code + '1', codes)
    return codes

def huffman_method(probs_dict):
    nodes = [node(prob, symbol) for symbol, prob in probs_dict.items()]
    while (len(nodes) > 1):
        nodes.sort(key = lambda node: node.probability)
        left = nodes.pop(0)
        right = nodes.pop(0)
        new_prob = left.probability + right.probability
        new_node = node(new_prob, left = left, right = right)
        nodes.append(new_node)
    root = nodes[0]
    codes = get_codes(root)

    return {symbol: code for symbol, code in codes.items()}

def convert_to_binary(num, max_length=8):
    if num == 0:
        return "0.0"
    binary = "0."
    count = 0
    while num > 0 and count < max_length:
        num *= 2
        bit = int(num)
        binary += str(bit)
        num -= bit
        count += 1
    if len(binary) < max_length + 2:
        binary += "0" * (max_length + 2 - len(binary))
    return binary[:max_length+2]

def shannon_fano_elias_method(probs_dict):
    symbols = list(probs_dict.keys())
    probs = list(probs_dict.values())
    n = len(probs_dict)
    f = [sum(probs[:i]) for i in range(n + 1)]
    f_m = [f[i] + (probs[i] / 2) for i in range(n)]
    f_m_b = [convert_to_binary(num) for num in f_m]
    l = [ceil(log2(1 / probs[i])) + 1 for i in range(n)]
    codes  = [f_m_b[i][2:l[i] + 2] for i in range(n)]
    return {symbols[i]: codes[i] for i in range(n)}


def add_error(word):
    word_list = list(word)  
    error_index = random.randint(0, len(word_list) - 1) 
    word_list[error_index] = '1' if word_list[error_index] == '0' else '0'  
    return ''.join(word_list)  

def create_errors_in_dict(code_dict):
    dict_size = len(code_dict)
    errors_amount = random.randint(0, dict_size - 1)
    errors_indexes = list()
    for _ in range(errors_amount):
        errors_indexes.append(random.randint(0, dict_size - 1))
    error_code_dict = dict()
    i = 0
    for key, value in code_dict.items():
        if(i in errors_indexes):
            error_code_dict[key] = add_error(value)
        else:
            error_code_dict[key] = value
        i += 1
    return error_code_dict


def encode(code_dict, encode_func):
    encode_code_dict = dict()
    for key, value in code_dict.items():
        encode_code_dict[key] = encode_func(value)
    return encode_code_dict

def check(code_dict, check_func):
    mark_code_dict = dict()
    for key, value in code_dict.items():
        result = check_func(value)
        if isinstance(result, bool):
            if result:
                mark_code_dict[key] = (value, "True")
            else:
                mark_code_dict[key] = (value, "False")
        else:
            mark_code_dict[key] = (value, result)
    return mark_code_dict

def invert_word(word):
    return ''.join('1' if bit == '0' else '0' for bit in word)


def add_parity_bit(word):
    count = word.count('1')
    parity_bit = '1' if(count % 2 == 0) else '0'
    return word + parity_bit

def check_parity(code_word):
    word, parity_bit = code_word[:-1], code_word[-1]
    count = word.count('1')
    expected_parity_bit = '1' if(count % 2 == 0) else '0'
    return parity_bit == expected_parity_bit


def add_bauer_inverse(word):
    count = word.count('1')  
    if(count % 2 == 0):
        return word + word
    else:
        inverted_word = invert_word(word)
        return word + inverted_word

def check_bauer_inverse(code_word):
    n = len(code_word) // 2
    word = code_word[:n]
    inverted_word = code_word[n:]
    count = word.count('1')
    if(count % 2 == 0):
        return word == inverted_word
    else:
        return word == invert_word(inverted_word)


def add_correlation(word):
    code_word = ""
    for bit in word:
        if(bit == '0'):
            code_word += '01'
        elif(bit == '1'):
            code_word += '10'
    return code_word
    
def check_correlation(code_word):
    for i in range(0, len(code_word), 2):
        pair = code_word[i:i+2]
        if (pair != '01') and (pair != '10'):
            return i  
    return True  


def add_berger_code(word):
    n = len(word)
    count = word.count('1')
    r = ceil(log2(n + 1))
    bin = format(count, f'0{r}b')
    check_part = invert_word(bin)
    return word + check_part

def check_berger_code(code_word):
    n = len(code_word) // 2  
    word = code_word[:n]
    check_part = code_word[n:]

    count = word.count('1')
    r = len(check_part)  
    bin_ones = format(count, f'0{r}b')  
    expected_check_bits = invert_word(bin_ones)  
    return check_part == expected_check_bits


def get_control_bits_amount(n):
    r = 0
    while (2 ** r) < (int(n) + r + 1):
        r += 1
    return r

def insert_bits_val(word, r):
    j = 0
    k = 1
    m = len(word)
    res = ""
    for i in range(1, m + r + 1):
        if(i == 2 ** j):
            res = res + '0'
            j += 1
        else:
            res = res + word[-1 * k]
            k += 1

    return res[::-1]

def insert_control_bits_val(word, r):
    n = len(word)
    for i in range(r):
        val = 0
        for j in range(1, n + 1):
            if(j & (2**i) == (2**i)):
                val = val ^ int(word[-1 * j])
        word = word[:n-(2**i)] + str(val) + word[n-(2**i)+1:]
    return word

def add_hamming_code(word):
    n = len(word)
    global r 
    r = get_control_bits_amount(n)
    code_word = insert_bits_val(word, r)
    code_word = insert_control_bits_val(code_word, r)
    return code_word

def check_hamming_code(code_word):
    n = len(code_word)
    res = 0
    for i in range(r):
        val = 0
        for j in range(1, n + 1):
            if(j & (2**i) == (2**i)):
                val = val ^ int(code_word[-1 * j])
        res = res + val*(10**i)
    if (res == 0):
        return "True"
    else:
        return int(str(res), 2)
    

def run_program(code_dict, type):
    if(type == 1):
        encoded_code_dict = encode(code_dict, add_parity_bit)
        error_code_dict = create_errors_in_dict(encoded_code_dict)
        marked_code_dict = check(error_code_dict, check_parity)
        print(f"------------------- {"Parity check".center(38)} -------------------")
    elif(type == 2):
        encoded_code_dict = encode(code_dict, add_bauer_inverse)
        error_code_dict = create_errors_in_dict(encoded_code_dict)
        marked_code_dict = check(error_code_dict, check_bauer_inverse)
        print(f"------------------- {"Bauer inverse code".center(38)} -------------------")
    elif(type == 3):
        encoded_code_dict = encode(code_dict, add_correlation)
        error_code_dict = create_errors_in_dict(encoded_code_dict)
        marked_code_dict = check(error_code_dict, check_correlation)
        print(f"------------------- {"Correlation code".center(38)} -------------------")
    elif(type == 4):
        encoded_code_dict = encode(code_dict, add_berger_code)
        error_code_dict = create_errors_in_dict(encoded_code_dict)
        marked_code_dict = check(error_code_dict, check_berger_code)
        print(f"------------------- {"Berger code".center(38)} -------------------")
    elif(type == 5):
        encoded_code_dict = encode(code_dict, add_hamming_code)
        error_code_dict = create_errors_in_dict(encoded_code_dict)
        marked_code_dict = check(error_code_dict, check_hamming_code)
        print(f"------------------- {"Hamming code".center(38)} -------------------")
    else:
        print("Error: Wrong type.")
    print_table(code_dict, encoded_code_dict, error_code_dict, marked_code_dict)
        
def print_table(code_dict, encoded_code_dict, error_code_dict, marked_code_dict):
    print("------------------- Table for Encoding and Error Detection -------------------")
    print(" ______________________________________________________________________________")
    print("|  Original Word  |  Encoded Word  | Encoded Word with Error  | Detected Errors|")
    print("|-----------------|----------------|--------------------------|----------------|")

    RED = '\033[31m'
    RESET = '\033[0m'
    GREEN = '\033[32m'

    for key in code_dict:
        original_word = f"{code_dict[key]}".center(17)
        encoded_word = f"{encoded_code_dict[key]}".center(16)
        error_word = f"{error_code_dict[key]}".center(26)
        code = marked_code_dict[key][0]
        status = marked_code_dict[key][1]
        if(status == "False"):
            marked_word = f" {RED}{code}{RESET}".center(25) 
        elif(status == "True"):
            marked_word = f" {GREEN}{code}{RESET}".center(25)
        else:
            marked_word = f" {code[:status]}{RED}{code[status:status + 1]}{RESET}{code[status + 1:]}".center(25)
        print(f"|{original_word}|{encoded_word}|{error_word}|{marked_word}|")
        print("|-----------------|----------------|--------------------------|----------------|")
    
    print()  

X = {"X1": 0.10, "X2": 0.09, "X3":0.19, "X4": 0.10, "X5": 0.04, "X6": 0.13, "X7": 0.08, "X8": 0.10, "X9": 0.09, "X10": 0.10}
TEXT = "Rievkov Volodymyr Volodymyrovych"

h_code_1 = huffman_method(X)
h_code_2 = huffman_method(get_probs_dict(TEXT))

sfe_code_1 = shannon_fano_elias_method(X)
sfe_code_2 = shannon_fano_elias_method(get_probs_dict(TEXT))

run_program(h_code_1, 5)

