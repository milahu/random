#!/usr/bin/env python3



import hashlib



def get_hash(file_path=None, data=None, algo="sha1"):
    # https://stackoverflow.com/questions/22058048/hashing-a-file-in-python
    hash_func = getattr(hashlib, algo)
    if data:
        return hash_func(data).digest()
    assert file_path
    # BUF_SIZE is totally arbitrary, change for your app!
    BUF_SIZE = 65536  # lets read stuff in 64kb chunks!
    hash = hash_func()
    with open(file_path, 'rb') as f:
        while data := f.read(BUF_SIZE):
            #md5.update(data)
            hash.update(data)
    #return hash.digest()
    #return hash.digest().hex()
    return hash.hexdigest()



if __name__ == "__main__":
    import sys
    file_path = sys.argv[1]
    hash = get_hash(file_path)
    print(f"{hash}  {file_path}")
