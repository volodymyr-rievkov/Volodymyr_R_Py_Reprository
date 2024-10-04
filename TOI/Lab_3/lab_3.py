from collections import Counter
from math import log2, ceil

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
    c_keys = list(codes.keys())
    c_values = list(codes.values())
    return {c_keys[i]: {"L": len(str(c_values[i])), "C": c_values[i]} for i in range(len(codes))}

def print_table_1(probs_dict, codes):
    print("-----------------Huffman Coding-----------------")
    print(" _______________________________________________")
    print("| Symbol |    Probability    |    Code    | Len |")
    print("|--------|-------------------|------------|-----|")
    for key in probs_dict:
        symbol = f" {key} ".ljust(8)
        prob = f" {probs_dict[key]:.5f} ".center(19)
        code = f" {codes[key]["C"]} ".center(12)
        length = f" {codes[key]["L"]} ".center(5)
        print(f"|{symbol}|{prob}|{code}|{length}|")
        print("|--------|-------------------|------------|-----|")
    print("Kraft inequality: ", kraft_inequality(codes))
    print("Entropy: ", round(calculate_entropy(probs_dict.values()), 2))
    print("Expected code length: ", round(calculate_expected_length(probs_dict, codes), 2))
    print()

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
    result = {symbols[i]: {"F": f[i + 1], "F_M": f_m[i], "F_M_B": f_m_b[i], "L": l[i], "C": codes[i]} for i in range(n)}
    return result

def print_table_2(probs_dict, codes):
    print("-----------------------------Shannon-Fano-Elias Coding-----------------------------")
    print(" ___________________________________________________________________________________")
    print("| Symbol | Probability |     F(x)    | F(x)_modified | F(x)_m_binary  | Len |  Code  |")
    print("|--------|-------------|-------------|---------------|----------------|-----|--------|")
    for key in probs_dict:
        symbol = key
        prob = f"{probs_dict[key]:<10.5f}"  
        f = f"{codes[key]['F']:<12.6f}"  
        f_m = f"{codes[key]['F_M']:<13.5f}"   
        f_m_b = f"{codes[key]['F_M_B']:<14}"  
        length = codes[key]['L']
        code = codes[key]['C']  
        print(f"| {symbol:<6} | {prob} | {f} | {f_m} | {f_m_b} | {length:<3} | {code:<6} |")
        print("|--------|------------|--------------|---------------|----------------|-----|--------|")
    print("Kraft inequality - ", kraft_inequality(codes))
    print("Entropy: ", round(calculate_entropy(probs_dict.values()), 2))
    print("Expected code length: ", round(calculate_expected_length(probs_dict, codes), 2))
    print()

def kraft_inequality(codes):
    sum = 0.0
    for symbol in codes:
        sum += (1 / pow(2, codes[symbol]["L"]))
    return sum <= 1

def calculate_entropy(probs):
    entropy = 0.0
    for p in probs:
        if p > 0:  
            entropy -= p * log2(p)
    return entropy

def calculate_expected_length(probs, codes):
    expected_length = 0.0
    for symbol in probs:
        expected_length += probs[symbol] * codes[symbol]["L"]
    return expected_length

X = {"X1": 0.10, "X2": 0.09, "X3":0.19, "X4": 0.10, "X5": 0.04, "X6": 0.13, "X7": 0.08, "X8": 0.10, "X9": 0.09, "X10": 0.10}
TEXT = "Rievkov Volodymyr Volodymyrovych"
probs_dict = get_probs_dict(TEXT)
h_codes_1 = huffman_method(X)
print_table_1(X, h_codes_1)
h_codes_2 = huffman_method(probs_dict)
print_table_1(probs_dict, h_codes_2)
sfe_code_1 = shannon_fano_elias_method(X)
print_table_2(X, sfe_code_1)
sfe_code_2 = shannon_fano_elias_method(probs_dict)
print_table_2(probs_dict, sfe_code_2)
