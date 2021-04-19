import argparse
import string
from copy import copy

zeros = [0 for _ in range(256)]
special_symbols = copy(zeros)
for c in string.punctuation + string.whitespace + string.digits:
    special_symbols[ord(c)] = 1
ascii_uppercase = copy(zeros)
for c in string.ascii_uppercase:
    ascii_uppercase[ord(c)] = 1


def encode(cap_file, decap_file, mask_file) -> None:
    txt_bytes = cap_file.read()
    counter = 1
    for i, byte in enumerate(txt_bytes, start=1):
        if counter == 256:
            mask_file.write(b'\x00')
            counter = 1
        if ascii_uppercase[byte]:
            byte = ord(b'a') + byte - ord(b'A')
            mask_file.write(bytes([counter]))
        decap_file.write(bytes([byte]))
        counter += 1


def decode(cap_file, decap_file, mask_file) -> None:
    txt_bytes = decap_file.read()
    next_shift, next_cap = 0, 0
    for i, byte in enumerate(txt_bytes, start=1):
        while True:
            if i <= next_cap:
                break
            buf = mask_file.read(1)
            if not buf:
                break
            count = buf[0]
            if count == 0:
                next_shift += 255
            else:
                next_cap = next_shift + count
                break
        if i == next_cap:
            byte = ord(b'A') + byte - ord(b'a')
        cap_file.write(bytes([byte]))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--cap_filename", help="filename with text with capital letters")
    parser.add_argument("-df", "--decap_filename", help="filename for text without capital letters")
    parser.add_argument("-m", "--mask_filename", help="mask with decapitalization encoding")
    parser.add_argument("--encode", help="use encoding", action="store_true")

    args = parser.parse_args()

    if args.encode:
        with open(args.cap_filename, "br") as cap, open(args.decap_filename, "bw") as decap, \
                open(args.mask_filename, "bw") as mask:
            encode(cap, decap, mask)
    else:
        with open(args.cap_filename, "bw") as cap, open(args.decap_filename, "br") as decap, \
                open(args.mask_filename, "br") as mask:
            decode(cap, decap, mask)
