s = 'hello world'
while True:
    if len(s) > 5:
        s = s[1:]
    else:
        break
print(s)