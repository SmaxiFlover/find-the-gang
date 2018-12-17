import math
import random

INT_MIN = -0x80000000
INT_MAX = 0x7fffffff
unknown = "Unknown"

data_name = []
data_type = []
str_name = []
int_name = []
spc_name = []

int_sum = []

"""
#accuracy = 93%
weight_str =  [0.05890778000335173, 0.533506896696842, 0.0007569125275403571, 0.9425671167940682, 0.004447473973003864, 0.4107172377588405, 0.8502398496061225, 0.16378109672210256, 0.3446606420572652, 0.8046461190961984, 0.8802817248084133, 0.38909464504953994, 0.04238804904518405, 0.9588178173404087, 0.0529939391533899, 0.14162765463685978, 0.9695130292493863, 0.07780361889328258, 0.006775130359359385, 0.7764357948787968, 0.9996757348825787, 0.5264819116658188, 0.010410227270018703, 0.2666292384292256, 0.13914531297124072, 0.8655360169804117, 0.6131124383392166, 0.2848469039058312, 0.8436663110329025, 0.001035539630345859]
weight_int =  [0.589242723352017, 0.9767282111781421, 0.0848340248696052, 0.24042303070971888, 0.9733569933492728, 0.9447543328614612, 0.892906620519122, 0.056654645199023516, 0.886563579897472]
"""

#accuracy = 98%
weight_str =  [1.679932767872194e-09, 0.3704009839146038, 0.6198627429579228, 0.5329647442403873, 4.833526957807098e-05, 0.9999296185737507, 0.6215364011714778, 0.7048992097000968, 0.9994941401858789, 0.574701883805357, 4.60615995920149e-06, 0.28958048902410954, 0.9999703914875008, 0.9896142018290407, 0.00014987590577285873, 0.003948580461515993, 0.2236955095955647, 0.43450336974047293, 0.9999148363615032, 0.48174636775076146, 0.9990643011719138, 2.994676151604018e-07, 0.6006115505115993, 0.829572159516621, 0.5011895835796714, 0.3615057380743315, 0.9999941803193416, 0.9998678817352761, 0.002241354560088799, 0.8837849275184249]
weight_int =  [0.001350784426728233, 0.9999806971696831, 0.5724756993371293, 0.5542503338398189, 0.2170025987518881, 7.245285523419161e-07, 5.06502439872725e-06, 0.9999764822649871, 5.593771392522118e-07]
weight_spc = []

n_str = 0
n_int = 0
n_spc = 0
n_sample = 0

terr = []
sample = {}

def calcDateNFromEventid(s):
    return (int(s[ : 4]) - 2015) * 365 + (int(s[4 : 6]) - 1) * 12 + int(s[7 : 8]) - 1

class Terr:
    
    def __init__(self, terr_type = "normal"):
        if (terr_type == "normal"):
            self.str_info = []
            self.int_info = []
            self.spc_info = []
        elif (terr_type == "sample"):
            self.str_info = [set()] * n_str
            self.int_info = [0] * n_int
            self.spc_info = [0] * n_spc
        self.gname = ""
        self.suspect = {}
        self.severity = 0.0
    
    def addSample(self, new_s):
        #print(new_s.str_info)
        
        for i, s in enumerate(new_s.str_info):
            self.str_info[i].add(s)
        for i, v in enumerate(new_s.int_info):
            self.int_info[i] += v / n_sample
        for i, s in enumerate(new_s.spc_info):
            if (spc_name[i] == "eventid"):
                self.spc_info[i] += calcDateNFromEventid(s) / n_sample
            elif (spc_name[i] == "weapdetail"):
                pass
            elif (spc_name[i] == "propcomment"):
                pass
            elif (spc_name[i] == "addnotes"):
                pass

    def regulate(self):
        for i in range(n_int):
            if (self.int_info[i] == ""):
                self.int_info[i] = 0.0
            elif (self.int_info[i] == "-99"):
                self.int_info[i] = 0.0 # random.random() * int_sum[i] / len(terr) * 2.0
                #if (self.int_info[i] > 10000):
                #    print(self.int_info[i], int_sum[i])
            else:
                self.int_info[i] = float(self.int_info[i]) / int_sum[i]

def calcDist(sample, event):
    res = 0.0
    for i in range(n_str):
        temp = 1
        for j in sample.str_info[i]:
            if (event.str_info[i] == j):
                temp = 0
                break
        res += (weight_str[i] * temp) ** 2
    
    for i in range(n_int):
        res += (weight_int[i] * abs(float(event.int_info[i]) - sample.int_info[i])) ** 2
    
    return math.sqrt(res)

def readData():
    global terr, n_str, n_int, n_spc, n_sample, weight_str, weight_int, weight_spc, int_sum
    with open("data/data_tagged.txt", "r", encoding = "UTF-8") as f:
        for s in f.readline()[1:-1].split("\t"):
            data_name.append(s)
            
        for i, s in enumerate(f.readline()[:-1].split("\t")):
            if (s == "0"):
                data_type.append("int")
                int_name.append(data_name[i])
                n_int += 1
            elif (s == "1"):
                data_type.append("str")
                str_name.append(data_name[i])
                n_str += 1
            elif (s == "-1"):
                data_type.append("spc")
                spc_name.append(data_name[i])
                n_spc += 1
                
        int_sum = [0] * n_int
        
        rest_file = f.readlines()
        for line in rest_file:
            temp = Terr()
            for i, s in enumerate(line[:-1].split("\t")):
                if (data_name[i] == "gname"):
                    temp.gname = s
                    if (s != unknown):
                        n_sample += 1
                        if (not s in sample):
                            sample[s] = Terr("sample")
                if (data_type[i] == "str"):
                    temp.str_info.append(s)
                elif (data_type[i] == "int"):
                    temp.int_info.append(s)
                    if (s != "" and s != "-99"):
                        int_sum[len(temp.int_info) - 1] += float(s)
                elif (data_type[i] == "spc"):
                    temp.spc_info.append(s)
            terr.append(temp)

    for t in terr:
        t.regulate()
    for t in terr:
        if (t.gname != unknown):
            sample[t.gname].addSample(t)

    terr = []
    
    with open("data/prob_2.txt", "r", encoding = "UTF-8") as f:
        f.readline()
            
        rest_file = f.readlines()
        for line in rest_file:
            temp = Terr()
            for i, s in enumerate(line[:-1].split("\t")):
                if (data_name[i] == "gname"):
                    temp.gname = s
                if (data_type[i] == "str"):
                    temp.str_info.append(s)
                elif (data_type[i] == "int"):
                    temp.int_info.append(s)
                elif (data_type[i] == "spc"):
                    temp.spc_info.append(s)
            terr.append(temp)
    
    for t in terr:
        t.regulate()


def findSuspect():
    for t in terr:
        severity = {}
        for s in sample:
            dist = calcDist(sample[s], t)
            severity[dist] = s
        print(t.spc_info[0], " : ")
        for sev, gname in sorted(severity.items())[:10]:
            print("%25s : " % gname[:20], sev)
        print()

if __name__ == "__main__":
    readData()
    findSuspect()
