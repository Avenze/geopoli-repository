import random

def titleCase(word):
    s = ''
    for w in word.split(' '):
        if w != 'of':
            s += w[0].upper()+w[1:].lower()+' '
        else:
            s += w.lower()+' '
    return s[:-1]

def setISO(nation, currISO):
    temp = nation.upper()
    for i in range(33, 127):
        if not chr(i).isalpha():
            temp = temp.replace(chr(i), ' ')
    if not temp.isalpha() or len(temp.split(' ')) == 0:
        while True:
            iso = chr(random.randint(65, 90)) + chr(random.randint(65, 90)) + chr(random.randint(65, 90))
            if iso not in currISO:
                return iso
    if len(temp.split(' ')) == 1:
        iso = temp[min(0, len(temp)-1)] + temp[min(len(temp)//2, len(temp)-1)] + temp[len(temp)-1]
        if iso not in currISO:
            return iso
        iso = temp[min(0, len(temp)-1)] + temp[min(1, len(temp)-1)] + temp[min(2, len(temp)-1)]
        if iso not in currISO:
            return iso
        while True:
            iso = chr(random.randint(65, 90)) + chr(random.randint(65, 90)) + chr(random.randint(65, 90))
            if iso not in currISO:
                return iso
    if len(temp.split(' ')) > 1:
        iso = temp.split(' ')[min(0, len(temp.split(' '))-1)][0] + temp.split(' ')[min(len(temp.split(' '))//2, len(temp.split(' '))-1)][0] + temp.split(' ')[len(temp.split(' '))-1][0]
        if iso not in currISO:
            return iso
        iso = temp[min(0, len(temp)-1)] + temp[min(len(temp)//2, len(temp)-1)] + temp[len(temp)-1]
        if iso not in currISO:
            return iso
        iso = temp[min(0, len(temp)-1)] + temp[min(1, len(temp)-1)] + temp[min(2, len(temp)-1)]
        if iso not in currISO:
            return iso
        while True:
            iso = chr(random.randint(65, 90)) + chr(random.randint(65, 90)) + chr(random.randint(65, 90))
            if iso not in currISO:
                return iso
    while True:
            iso = chr(random.randint(65, 90)) + chr(random.randint(65, 90)) + chr(random.randint(65, 90))
            if iso not in currISO:
                return iso

def numbered(num):
    lastdigit = str(num)[len(str(num))-1]
    if lastdigit == '1':
        return str(num)+'st'
    if lastdigit == '2':
        return str(num)+'nd'
    if lastdigit == '3':
        return str(num)+'rd'
    return str(num)+'th'
