import os, csv, time, random
import numpy as np
import matplotlib.pyplot as plt
from time import sleep

class myClass:
    def __init__(self):
        self.dealOpenPrice = 0.0
        self.opened = False
        self.Open, self.Low, self.Hight, self.Close, self.Spread = self._GetInf()
        self.bf1,self.bf2,self.bf3,self.bf4,self.bf5,self.bf6,self.bf7,self.bf8,self.bf9,self.bf10 = self._GetIndiInf()
        self.DataLen = len(self.Open)
        #print(self.Open, self.Low, self.Hight, self.Close, self.Spread)
        print(len(self.Open))
        self.state = None
        self.i = 0
        self.currentStep = 0
        self.maxLotTimeBars = 288 #288 = 15min x 3days, max time to keep lot opened
        self.reward=0.0
        self.prev_prof=0.0
        self.dealOpenedAgo = 0
        self.balance=0.0
        self.balance_max=0.0
        self.balance_min=0.0
        self.prof=0.0
        self.prof_next = 0.0
        
    def _GetInf(self):
        try:
            filename = "C:\\Users\\sfc\\AppData\\Roaming\\MetaQuotes\\Terminal\\Common\\Files\\PyTS\\State.csv"
            file_handle=open(filename, 'r')
            reader = csv.reader(file_handle)
            InData = [row for row in reader]
            #print(InData)
            self.test=InData
            file_handle.close()
            a = np.asarray(InData)
            return  np.asfarray(a[:, 1]), np.asfarray(a[:, 2]), np.asfarray(a[:, 3]),np.asfarray(a[:, 4]),np.asfarray(a[:, 5])
        except ValueError:
            print('Numbers only please...')        

    def _GetIndiInf(self):
        try:
            filename = "C:\\Users\\sfc\\AppData\\Roaming\\MetaQuotes\\Terminal\\Common\\Files\\PyTS\\Indi.csv"
            file_handle=open(filename, 'r')
            reader = csv.reader(file_handle)
            InData = [row for row in reader]
            #print(InData)
            self.test=InData
            file_handle.close()
            a = np.asarray(InData)
            return  np.asfarray(a[:, 0]),np.asfarray(a[:, 1]), np.asfarray(a[:, 2]), np.asfarray(a[:, 3]),np.asfarray(a[:, 4]),np.asfarray(a[:, 5]),np.asfarray(a[:, 6]),np.asfarray(a[:, 7]),np.asfarray(a[:, 8]),np.asfarray(a[:, 9])
        except ValueError:
            print('Numbers only please...')
            
    def reset(self):
        values = list(range((self.DataLen-self.maxLotTimeBars-1)))
        #print(values)
        self.i = random.choice(values)
        self.prof = 0.0
        self.currentStep = 0
        self.dealOpenPrice = 0.0
        self.dealOpenedAgo = 0
        self.prev_prof = 0.0
        self.prof_next = 0.0
        self.state = (self.bf1[self.i],self.bf2[self.i],self.bf3[self.i],self.bf4[self.i],self.bf5[self.i],self.bf6[self.i],self.bf7[self.i],self.bf8[self.i],self.bf9[self.i],self.bf10[self.i],
                      0.0, 0, -10) #0=no opened positions
        return np.array(self.state)
        
    def step(self, action): #actions 0-do nothing, 1-Sell Open, 2-Sell Close
        self.i += 1
        self.currentStep += 1
        done = bool(False)
        self.prof = 0.0
        self.prof_next = 0.0
        reward = 0.0
        if self.i >= (self.DataLen-1):
            self.i-=1
            done = bool(True)
            reward = 0.0
        else:
            if self.opened:
                #order opened
                self.prof = (self.dealOpenPrice-self.Close[self.i]-(self.Spread[self.i]*0.00001))#sell?profit            
                self.prof_next = self.dealOpenPrice-self.Close[self.i+1]-(self.Spread[self.i+1]*0.00001)
                self.dealOpenedAgo += 1
                if (self.Close[self.i-1]-self.Close[self.i])>0:
                    self.prev_prof += 0.1
                else:
                    self.prev_prof -= 0.1
                if action == 0:
                    reward = self.prof*10
                    if reward > 10.0:
                        reward = 10.0
                    elif reward < -10.0:
                        reward = -10.0
                    #print("nothing")
                elif action == 1:
                    reward = -10 #if lot opened, cant open again
                    #print("can't open")
                elif (action == 2) or (self.currentStep >= self.maxLotTimeBars): #=========================== CLOSE ======================
                    #print("close")
                    #print(prof)
                    self.opened = False
                    self.balance += (self.prof-(self.Spread[self.i]*0.00001))
                    self.balance_max = self.balance if self.balance > self.balance_max else self.balance_max
                    self.balance_min = self.balance if self.balance < self.balance_min else self.balance_min
                    self.dealOpenPrice=0.0
                    print("Profit %s                 step %s          balance: %s         max: %s       min: %s" % (self.prof, self.currentStep, self.balance, self.balance_max, self.balance_min))
                    if self.prof < 0:
                        reward = self.prof*(-1000)
                    else:
                        reward = self.prof*100
                    if reward > 10.0:
                        reward = 10.0
                    elif reward < -10.0:
                        reward = -10.0                
                    self.dealOpenedAgo = 0
                    self.prev_prof = 0.0
                    done = bool(True)
                    #print(reward)
                    #print("done")
            else:
                self.dealOpenedAgo = 0
                if action == 0:
                    reward = 0.0001
                    #print("nothing")
                elif action == 1:#==================================== OPEN ===============================
                    #print("open")
                    self.dealOpenPrice = self.Close[self.i]
                    self.opened = True
                    self.dealOpenedAgo = 1
                    if self.i < (self.DataLen-1):
                        reward = (self.Close[self.i] - self.Close[self.i+1])*1000
                    if reward > 10.0:
                        reward = 10.0
                    elif reward < -10.0:
                        reward = -10.0
                elif action == 2:
                    #print("can't close")
                    reward = -10 #+10
        #============================================
        if self.opened:
            opened = 10
        else:
            opened = -10
        self.prof = (self.dealOpenPrice-self.Close[self.i]-(self.Spread[self.i]*0.00001))
        self.state = (self.bf1[self.i],self.bf2[self.i],self.bf3[self.i],self.bf4[self.i],self.bf5[self.i],self.bf6[self.i],self.bf7[self.i],self.bf8[self.i],self.bf9[self.i],self.bf10[self.i],
                      (self.prof*1000), self.dealOpenedAgo, opened)
        print(reward)
        #print(action, reward, self.currentStep, self.i)
        return np.array(self.state), reward, done, {}
        
m=myClass()
m.reset()
