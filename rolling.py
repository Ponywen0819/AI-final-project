def rolling():
    i = 0
    l = ['-', '\\', '|', '/']
    while 1:
        i = (i + 1) % 200
        print(l[i // 50], end='\r')
        yield