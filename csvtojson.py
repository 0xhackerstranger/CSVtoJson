import csv
import json
from collections import defaultdict, OrderedDict
import collections

from pprint import pprint


class OrderedDefaultDict(OrderedDict, defaultdict):
    def __init__(self, default_factory=None, *args, **kwargs):
        # in python3 you can omit the args to super
        super(OrderedDefaultDict, self).__init__(*args, **kwargs)
        self.default_factory = default_factory
        # self.default_factory = dict


class CustomDictReader(csv.DictReader):
    '''
        override the next() function and  use an
        ordered dict in order to preserve writing back
        into the file
    '''

    def __init__(self, f, fieldnames=None, restkey=None, restval=None, dialect="excel", *args, **kwds):
        csv.DictReader.__init__(self, f, fieldnames=None, restkey=None, restval=None, dialect="excel", *args, **kwds)

    def next(self):
        if self.line_num == 0:
            # Used only for its side effect.
            self.fieldnames
        row = self.reader.next()
        self.line_num = self.reader.line_num

        # unlike the basic reader, we prefer not to return blanks,
        # because we will typically wind up with a dict full of None
        # values
        while row == []:
            row = self.reader.next()
        d = collections.OrderedDict(zip(self.fieldnames, row))

        lf = len(self.fieldnames)
        lr = len(row)
        if lf < lr:
            d[self.restkey] = row[lf:]
        elif lf > lr:
            for key in self.fieldnames[lr:]:
                d[key] = self.restval
        return d


def build_dict(source_file):
    projects = OrderedDefaultDict(dict)
    # projects = defaultdict(dict)

    with open(source_file, 'r') as fp:
        reader = CustomDictReader(fp)
        # reader = csv.DictReader(fp)
        for rowdict in reader:
            channel = rowdict['Channel']
            filename = rowdict.pop("Filename")
            session = rowdict.pop('Number_of_Session')
            # session = rowdict['Number_of_Session']
            no = rowdict.pop('No')
            t = OrderedDict(rowdict)
            for k,v in t.items():
                if v == '':
                    del t[k]
            if filename not in projects:
                projects[filename][session] = [t]
            else:
                try:
                    projects[filename][session].append(t)
                except KeyError:
                    projects[filename][session] = [t]
                    # print projects[filename].keys()
                    # pass
    return projects

x = build_dict('Recording.csv')

with open('Recording_log.json', 'w') as f:
    json.dump(x, f, indent=4)
print ('Done')
