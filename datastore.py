from google.cloud import datastore
datastore_client = datastore.Client()

# Insert the data (must stream to not overflow memory)
i = 0
n = 0
is_there = True
new = {}
with open('glove.twitter.27B.50d.txt.txt', 'r') as word2vec:
    for line in word2vec:
        n += 1
        # get first space
        split_arr = line.split(" ", 1)
        if("'" in split_arr[0]):
            i += 1
            continue
        # remove \n
        if(split_arr[0] == '______'):
            is_there = False
            continue
        if(is_there):
            continue
        split_arr[1] = split_arr[1][:-2]
        try:
            row = datastore.Entity(key=datastore_client.key('[default]', split_arr[0]))
            row.update({
                'vec_string': split_arr[1]
            })
            datastore_client.put(row)
        except:
            print(split_arr)
            break
        
print(n / (n + i))

