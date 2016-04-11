#!/usr/bin/env python

import os
import hashlib
import const

class MerkleTree:
    def __init__(self, root):
        self._linelength = 30
        self._root = root
        self._hashlist = {}
        self._tree = {}
        self.__MT__()

    def __MT__(self):
        self.HashList(self._root)
        print "Merkle Tree for %s: " % self._root

    def ParseMT(self):
        def tmp(x,y):
            func    ={const.DIRC:MTDIRC,const.FILE:MTFILE}
            x.update(func[y[:4]](y))
            return x
        def MTFILE(value):
            value,name = value.split('#')
            t= {name:value}
            return t
        def MTDIRC(value):
            value,name = value.split('#')
            items = self._tree[value].split(',')[:-1]
            items = [{}]+items
            return {name:reduce(tmp, items)}
        top = self._hashlist['root']
        if top:
            tophash = self._tree[top]
            items = tophash.split(',')[:-1]
            self._mt = reduce(tmp, items,{})
        else:
            self._mt={}
        return self._mt

    def md5sum(self, data):
        m = hashlib.sha1()
        fn = os.path.join(self._root, data)
        if os.path.isfile(fn):
            try:
                f = file(fn, 'rb')
            except:
                return 'ERROR: unable to open %s' % fn
            while True:
                d = f.read(8096)
                if not d:
                    break
                m.update(d)
            f.close()
        else:
            m.update(data)
        return m.hexdigest()

    def GetItems(self, directory):
        return [item for item in os.listdir(os.path.join(self._root, directory))] if os.path.isdir(os.path.join(self._root, directory)) else  []
    
    def HashList(self, rootdir):
        items = [item for item in os.listdir(rootdir)] if os.path.isdir(rootdir) else  []
        if not items:
            self._hashlist[rootdir] = ''
            return
        for item in items:
            if os.path.isdir(os.path.join(self._root, item)):
                self.HashListChild(item)
                s = reduce((lambda x,y: x+self._hashlist[os.path.join(item,y)]+'#'+y+','), self.GetItems(item),'')
                self._hashlist[item] = const.DIRC+self.md5sum(s)
                self._tree[self._hashlist[item]]    = s
            else:
                self._hashlist[item] = const.FILE+self.md5sum(item)
                open("./cache/"+self._hashlist[item], "wb").write(open(os.path.join(self._root, item), "rb").read())
        s = reduce((lambda x,y: x+self._hashlist[y]+'#'+y+','), items,'')
        self._hashlist['root'] = const.ROOT+self.md5sum(s)
        self._tree[self._hashlist['root']]    = s

    def HashListChild(self, rootdir):
        items = self.GetItems(rootdir)
        if not items:
            self._hashlist[rootdir] = ''
            return
        for item in items:
            itemname = os.path.join(rootdir, item)
            if os.path.isdir(os.path.join(self._root, itemname)):
                self.HashListChild(itemname)
                s = reduce((lambda x,y: x+self._hashlist[os.path.join(itemname,y)]+'#'+y+','), self.GetItems(itemname),'')
                self._hashlist[itemname] = const.DIRC+self.md5sum(s)
                self._tree[self._hashlist[itemname]]    = s
            else:
                self._hashlist[itemname] = const.FILE+self.md5sum(itemname)
                open("./cache/"+self._hashlist[itemname], "wb").write(open(os.path.join(self._root, itemname), "rb").read())

def MTDiff(mt_a, mt_b):
    if mt_a._hashlist['root'] == mt_b._hashlist['root']:
        print "Top hash is equal for %s and %s" % (mt_a._hashlist['root'], mt_b._hashlist['root'])
    else:
        a_child = mt_a._mt    # retrive the child list for merkle tree a
        b_child = mt_b._mt    # retrive the child list for merkle tree b

        for item in mt_a._mt.keys():
            try:
                if mt_b[item] == mt_a[item]:
                    print "Info: SAME : %s" % item
            except:
                print "Info: DIFFERENT : %s" % item
                temp_value = mt_a._mt[item]
                if len(temp_value[1]) > 0:      # check if this is a directory
                    diffhash = list(set(b_child.keys()) - set(a_child.keys()))
                    MTDiff(mt_a, itemhash, mt_b, diffhash[0])

if __name__ == "__main__":
    mt_a = MerkleTree('testA')
    print mt_a.ParseMT()
    print mt_a._tree
    print mt_a._hashlist