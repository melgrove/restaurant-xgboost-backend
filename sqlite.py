import sqlite3
con = sqlite3.connect("word2vec.db")
cur = con.cursor()
# Create the table
cur.execute('''
    CREATE TABLE word2vec (
        word TEXT NOT NULL UNIQUE,
        vec_string TEXT NOT NULL
    )
''')

# Insert the data (must stream to not overflow memory)
i = 0
n = 0
with open('glove.twitter.27B.50d.txt.txt', 'r') as word2vec:
    for line in word2vec:
        n += 1
        # get first space
        split_arr = line.split(" ", 1)
        if("'" in split_arr[0]):
            i += 1
            continue
        # remove \n
        split_arr[1] = split_arr[1][:-2]
        try:
            cur.execute(f"INSERT INTO word2vec (word, vec_string) VALUES ('{split_arr[0]}', '{split_arr[1]}')")
        except:
            print(split_arr)
            break
        
print(n / (n + i))
