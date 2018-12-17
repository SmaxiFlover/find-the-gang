import math
import random

INT_MIN = -0x80000000
INT_MAX = 0x7fffffff
unknown = "Unknown"

try_times_1 = 1000
try_times_2 = 6
start_radius = 0.5
r_drop = 0.8
radius_min = 0.01
test_time = 640

data_name = []
data_type = []
str_name = []
int_name = []
spc_name = []

int_sum = []

weight_str = []
weight_int = []
weight_spc = []
w_str_bak = []
w_int_bak = []
w_spc_bak = []
cur_w_str = []
cur_w_int = []
cur_w_spc = []
ans_w_str = []
ans_w_int = []
ans_w_spc = []


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

    """
    for i in range(n_spc):
        if (spc_name[i] == "eventid"):
            pass 
            #res += (weight_spc[i] * abs(sample.spc_info[i] - calcDateNFromEventid(event.spc_info[i]))) ** 2
        elif (spc_name[i] == "weapdetail"):
            pass
        elif (spc_name[i] == "propcomment"):
            pass
        elif (spc_name[i] == "addnotes"):
            pass
    """
    
    return math.sqrt(res)

def readData():
    with open("data/data_tagged.txt", "r", encoding = "UTF-8") as f:
        for s in f.readline()[1:-1].split("\t"):
            data_name.append(s)
        global n_str, n_int, n_spc, n_sample, weight_str, weight_int, weight_spc, int_sum
            
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

def calcCurrentAccuracy():
    """
    fake_ans = 0
    for i in weight_str:
        fake_ans += i
    for i in weight_int:
        fake_ans += i
        print("\r  - %4d" % (fake_ans), end = "", flush = True)
    print()
    return fake_ans
    """
    cnt = 0
    for i in range(test_time):
        t = terr[math.floor(random.random() * len(terr))]
        if (t.gname == unknown):
            cnt += 1
        else:
            min_dist = INT_MAX
            min_s = ""
            for s in sample:
                dist = calcDist(sample[s], t)
                if (dist < min_dist):
                    min_dist = dist
                    min_s = s
            if (min_s == t.gname):
                cnt += 1
        print("\r  %4.1f%% acc = %4.1f%%" % (100 * (i+1) / test_time, 100*cnt/test_time), end = "", flush = True)
    print()
    return cnt / test_time

def randomWeight():
    for i in range(n_int):
        weight_int[i] = random.random()
    for i in range(n_str):
        weight_str[i] = random.random()

def backupWeight():
    global w_str_bak, w_int_bak, w_spc_bak
    w_str_bak = weight_str[:]
    w_int_bak = weight_int[:]

def recoverWeight():
    global weight_str, weight_int, weight_spc
    weight_str = w_str_bak[:]
    weight_int = w_int_bak[:]

def recordCurrentBestWeight():
    global cur_w_str, cur_w_int, cur_w_spc
    cur_w_str = weight_str[:]
    cur_w_int = weight_int[:]
    
def recordAnsWeight():
    global ans_w_str, ans_w_int, ans_w_spc
    ans_w_str = weight_str[:]
    ans_w_int = weight_int[:]

def moveWeight(radius):
    for i in range(n_int):
        ri = min(radius, weight_int[i], 1 - weight_int[i])
        weight_int[i] += (2 * random.random() - 1) * ri
    for i in range(n_str):
        ri = min(radius, weight_str[i], 1 - weight_str[i])
        weight_str[i] += (2 * random.random() - 1) * ri

def moveToBestWeight():
    global weight_str, weight_int, weight_spc
    weight_str = cur_w_str[:]
    weight_int = cur_w_int[:]

def printWeight():
    for i in weight_str:
        print("%.2f" % (i), end = " ")
    print()
    for i in weight_int:
        print("%.2f" % (i), end = " ")
    print("\n")

def printAnsWeight():
    for i in ans_w_str:
        print("%.2f" % (i), end = " ")
    print()
    for i in ans_w_int:
        print("%.2f" % (i), end = " ")
    print("\n")
    print(ans_w_str)
    print(ans_w_int)

acc_max = 0

def printAnsWeightToFile():
    with open("data/weight.txt", "w") as f:
        print("#Accuracy = %.2f%%\n" % (acc_max * 100), file = f)
        print("weight_str = ", weight_str, file = f)
        print("weight_int = ", weight_int, file = f)

def calcDistWeight():
    global weight_str, weight_int, weight_spc, acc_max
    weight_str =  [1.679932767872194e-09, 0.3704009839146038, 0.6198627429579228, 0.5329647442403873, 4.833526957807098e-05, 0.9999296185737507, 0.6215364011714778, 0.7048992097000968, 0.9994941401858789, 0.574701883805357, 4.60615995920149e-06, 0.28958048902410954, 0.9999703914875008, 0.9896142018290407, 0.00014987590577285873, 0.003948580461515993, 0.2236955095955647, 0.43450336974047293, 0.9999148363615032, 0.48174636775076146, 0.9990643011719138, 2.994676151604018e-07, 0.6006115505115993, 0.829572159516621, 0.5011895835796714, 0.3615057380743315, 0.9999941803193416, 0.9998678817352761, 0.002241354560088799, 0.8837849275184249]
    weight_int =  [0.001350784426728233, 0.9999806971696831, 0.5724756993371293, 0.5542503338398189, 0.2170025987518881, 7.245285523419161e-07, 5.06502439872725e-06, 0.9999764822649871, 5.593771392522118e-07]
    acc_max = calcCurrentAccuracy()
    printAnsWeightToFile()
    recordAnsWeight()
    try_times_r = math.ceil(math.log(radius_min / start_radius, r_drop))
    
    for try1 in range(try_times_1):
        radius = 0.5
        randomWeight()
        tr = 0
        while (radius > radius_min):
            cur_best_acc = calcCurrentAccuracy()
            recordCurrentBestWeight()
            for try2 in range(try_times_2):
                backupWeight()
                moveWeight(radius)
                cur_acc = calcCurrentAccuracy()
                if (cur_acc > cur_best_acc):
                    recordCurrentBestWeight()
                    cur_best_acc = cur_acc
                    if (cur_acc > acc_max):
                        acc_max = cur_best_acc
                        recordAnsWeight()
                        printAnsWeightToFile()
                print("%4d : " % (try1 * try_times_r * try_times_2 + tr * try_times_2 + try2), end = "")
                #print(" / %4d" % (try_times_2 * try_times_1 * try_times_r), ":", end = "")
                print("%.5f %.5f %.5f" % (cur_acc, cur_best_acc, acc_max))
                recoverWeight()
                moveToBestWeight()
            tr += 1
            radius *= r_drop
        if (cur_best_acc > acc_max):
            acc_max = cur_best_acc
            recordAnsWeight()
            printAnsWeightToFile()
    printAnsWeight()

def findSeverityAndSuspect():
    cnt = 0
    print(len(sample))
    for t in terr:
        print(cnt, ":", t.spc_info[0])
        cnt += 1
        if (True):#(t.gname == unknown):
            for s in sample:
                dist = calcDist(sample[s], t)
                t.suspect[dist] = s
                sample[s].severity += 1.0 / dist
    top_severity = {}
    for s in sample:
        top_severity[sample[s].severity] = s
    for i, v in sorted(top_severity.items()):
        print(v, i)

if __name__ == "__main__":
    readData()
    calcDistWeight()
    #findSeverityAndSuspect()
