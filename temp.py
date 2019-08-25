def mdc(a, b):
    while b:
        a, b = b, a % b
    return a

value = input('Digite 2 números separados por vírgula')
value = value.split(',')
print(value)
print(mdc(int(value[0]),int(value[1])))