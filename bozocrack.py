#!/usr/bin/env python
import hashlib
import re
from urllib import FancyURLopener
import sys
from optparse import OptionParser

HASH_REGEX = re.compile("([a-fA-F0-9]{32})")

class MyOpener(FancyURLopener):
    version = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11'

def dictionary_attack(h, wordlist):
    for word in wordlist:
        m = hashlib.md5()
        m.update(word)

        if m.hexdigest() == h:
            return word

    return None

def format_it(hash, plaintext):
    return "{hash}:{plaintext}".format(hash=hash, plaintext=plaintext)

def crack_single_hash(h):
    myopener = MyOpener()
    response = myopener.open("http://www.google.com/search?q={hash}".format(hash=h))
    
    wordlist = response.read().replace('.',' ').replace(':',' ').replace('?','').split(' ')
    plaintext = dictionary_attack(h, set(wordlist))
    
    return plaintext

class BozoCrack(object):
    def __init__(self, filename, *args, **kwargs):
        self.hashes = []
        self.cache = {}
        
        with open(filename, 'r') as f:
            hashes = [x.lower() for line in f if HASH_REGEX.match(line) for x in HASH_REGEX.findall(line.replace('\n',''))]

        self.hashes = sorted(list(set(hashes)))

        print "Loaded {count} unique hashes".format(count=len(self.hashes))

        self.load_cache()
                                                     
    def crack(self):
        for h in self.hashes:
            if h in self.cache:
                print format_it(h, self.cache[h])
                continue

            plaintext = crack_single_hash(h)

            if plaintext:
                print format_it(h, plaintext)
                self.cache[h] = plaintext
                self.append_to_cache(h, plaintext)
            
    def load_cache(self, filename='cache'):
        with open(filename, 'a+') as c:
            for line in c:
                line = line.replace('\n','').split(':')
                self.cache[line[0]] = line[1]

    def append_to_cache(self, h, plaintext, filename='cache'):
        with open(filename, 'a+') as c:
            c.write(format_it(hash=h, plaintext=plaintext))

if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option('-s', '--single', metavar='MD5HASH', help='cracks a single hash', dest='single', default=False)
    parser.add_option('-f', '--file', metavar='HASHFILE', help='cracks multiple hashes on a file', dest='target',)

    (options, args) = parser.parse_args()
    
    if not options.single and not options.target:
        parser.error("please select -s or -f")
    elif options.single:
        plaintext = crack_single_hash(options.single)

        if plaintext:
            print format_it(hash=options.single, plaintext=plaintext)
    else:
        BozoCrack(options.target).crack()
