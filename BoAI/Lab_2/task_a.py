import sys
from collections import Counter
import math

input = sys.stdin.readline

if __name__ == "__main__":

    N, M, K = map(int, input().split())

    spam_total = 0
    ham_total = 0
    spam_count = Counter()
    ham_count = Counter()

    for _ in range(N):
        message = input().split()
        ham_total += len(message)
        ham_count.update(message)
    
    for _ in range(M):
        message = input().split()
        spam_total += len(message)
        spam_count.update(message)
    
    total = N + M

    ham_p = N / total
    spam_p = M / total


    for _ in range(K):
        words = input().split()

        log_ham_p = math.log(ham_p) if ham_p > 0 else float("-inf")
        log_spam_p = math.log(spam_p) if spam_p > 0 else float("-inf")

        ham_zero = False
        spam_zero = False

        for word in words:
            sc = spam_count[word]
            if sc == 0:
                spam_zero = True
            else:
                log_spam_p += math.log(sc / spam_total)

            hc = ham_count[word]
            if hc == 0:
                ham_zero = True
            else:
                log_ham_p += math.log(hc / ham_total)

        if spam_zero and not ham_zero:
            print(0.0)

        elif not spam_zero and ham_zero:
            print(1.0)
            
        elif spam_zero and ham_zero:
            print(spam_p)
            
        else:
            print(1 / (1 + math.exp(log_ham_p - log_spam_p)))

# O(N + M + K * L), L - word length.