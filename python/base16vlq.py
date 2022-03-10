"""

base16vlq.py

base16 unsigned variable length quantity (VLQ)

based on
https://gist.github.com/mjpieters/86b0d152bb51d5f5979346d11005588b
https://github.com/Rich-Harris/vlq

to encode *signed* integers, we would need _abc_len == 17

python -c $'from base16vlq import encode\nfor n in range(0, 64):\n  print(f"{n:3d} {encode(n):<3s}   ", end="")\n  if (n+1) % 8 == 0:\n    print()'

_shift_size = 3
_carry_flag = 8 =  1000 = 2^3
_mask       = 7 =   111 = 2^3-1
_len_abc   = 16 = 10000 = 2^4
_bytemax   = 15 =  1111 = 2^4-1
_abc_chars = (,:<[$*?)~=>]@&%

  0 (       1 ,       2 :       3 <       4 [       5 $       6 *       7 ?     
  8 ),      9 ~,     10 =,     11 >,     12 ],     13 @,     14 &,     15 %,    
 16 ):     17 ~:     18 =:     19 >:     20 ]:     21 @:     22 &:     23 %:    
 24 )<     25 ~<     26 =<     27 ><     28 ]<     29 @<     30 &<     31 %<    
 32 )[     33 ~[     34 =[     35 >[     36 ][     37 @[     38 &[     39 %[    
 40 )$     41 ~$     42 =$     43 >$     44 ]$     45 @$     46 &$     47 %$    
 48 )*     49 ~*     50 =*     51 >*     52 ]*     53 @*     54 &*     55 %*    
 56 )?     57 ~?     58 =?     59 >?     60 ]?     61 @?     62 &?     63 %?    

"""

from typing import List

_abc_chars = b"""(,:<[$*?)~=>]@&%"""
#                0123456701234567
# remaining special chars: {}#"'^`;|

_abc_table = [None] * (max(_abc_chars) + 1)
for i, b in enumerate(_abc_chars):
    _abc_table[b] = i

#_shift_size = 5 # base64
_shift_size = 3 # base16
# one bit is needed for the carry_flag

_carry_flag = 1 << _shift_size
_mask = (1 << _shift_size) - 1 # 2^4-1 = 15
_bytemax = _mask | _carry_flag
_len_abc = _bytemax + 1 # unsigned
#_len_abc = _bytemax + 2 # signed?

if False:
  print(f"_shift_size = {_shift_size}")
  print(f"_carry_flag = {_carry_flag}")
  print(f"_mask = {_mask}")

  print(f"_bytemax = {_bytemax}")
  print(f"_abc_chars = {_abc_chars.decode()}")
  print(f"_len_abc = {_len_abc}")

assert len(_abc_chars) == _len_abc

def decode(vlq_code: str) -> List[int]:
    """Decode Base16 VLQ value"""
    num_list = []
    shift_size, carry_flag, mask = _shift_size, _carry_flag, _mask
    shift = num = 0
    # use byte values and a table to go from base16 characters to integers
    for clamped in map(_abc_table.__getitem__, vlq_code.encode("ascii")):
        num += (clamped & mask) << shift
        if clamped & carry_flag:
            shift += shift_size
            continue
        ## read sign bit
        #num_sign = -1 if (num & 1) else +1
        #num = (num >> 1) * num_sign
        num_list.append(num)
        shift = num = 0
    return num_list

def encode(*num_list: int) -> str:
    """Encode integers to a VLQ value"""
    clamped_list = []
    shift_size = _shift_size
    carry_flag = _carry_flag
    mask = _mask
    for num in num_list:
        ## write sign bit
        #num = (abs(num) << 1) | int(num < 0)
        if type(num) != int or num < 0:
          raise ValueError("num must be unsigned integer")
        while True:
            clamped = num & mask
            num = num >> shift_size
            if num > 0:
              clamped = clamped | carry_flag
            clamped_list.append(clamped)
            if num == 0:
                break
    return bytes(map(_abc_chars.__getitem__, clamped_list)).decode()

# python -c 'from base16vlq import _test; _test()'
def _test():
  """throws on error"""
  for num in range(0, 1024):
    arr1 = [num, num]
    code = encode(*arr1)
    arr2 = decode(code)
    if not arr1 == arr2:
      print(f"arr1 = {arr1}")
      print(f"code = {code}")
      print(f"arr2 = {arr2}")
    assert arr1 == arr2
  assert decode(encode(1234))[0] == 1234
  try:
    encode(-1)
  except ValueError:
    pass
  try:
    encode(1.1)
  except ValueError:
    pass
  try:
    encode("a")
  except ValueError:
    pass
