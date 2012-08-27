from __future__ import division
import numpy as np,scipy
import itertools as it
from scipy.optimize import fmin_bfgs
from matplotlib import pyplot as plt

#
# Simple Weighted Monte Carlo engine 
# ziggy.jonsson.nyc@gmail.com

np.set_printoptions(suppress=True)

class WMC(object):
    '''WMV(g,C)
    
        g is a N x V matrix of derivatives payouts
        C is a 1 x N matrix of derivative prices
        
        N = number of instruments
        V = number of paths
        
        Once initiated call .solve to calculate optimal lambdas
        Resulting probabilities are stored in variable p
    '''

    def __init__(self,g,C):
        self.g=np.matrix(g)  # N x V
        self.C=np.matrix(C)  # 1 x N
        self.v =g.shape[0]   
        self.last=None
        
    def recalc(self,l):
        if self.last != tuple(l.tolist()):
            l=np.matrix(l)
            self.egl = np.exp(self.g*l.T)
            self.Z=np.sum(self.egl)
            self.p=((1/self.Z)*self.egl).T
            self.w=float(np.log(self.Z)-self.C*l.T+self.e/2 * (l*l.T))
            self.fPrime = np.array((self.p*self.g-self.C+self.e*l))[0]
            self.last=tuple(l.tolist())
            
    def _objective(self,l):
        self.recalc(l)
        return self.w
        
    def _fPrime(self,l):
        self.recalc(l)
        return self.fPrime
    
    def solve(self,fPrime=True,e=0.00001,disp=True):
        ''' fPrime = True/False (use gradiant)
            e      =  "weight" in the least squares implementation
            disp   = Print optimization convergence
        '''
        self.e=e
        if fPrime:
            lmd = fmin_bfgs(self._objective,np.zeros(self.C.shape[1]),fprime=self._fPrime,disp=disp)
        else:
            lmd = fmin_bfgs(self._objective,np.zeros(self.C.shape[1]))
            
        self.l=np.matrix(lmd)   # Store lambdas
        self.P=self.p*self.g    # Store resulting prices of calibrated instruments
        self.pg = np.multiply(self.p.T,self.g)   # probability weighted payoffs
        self.quality = float(1- (np.log(self.v)+self.p*np.log(self.p.T)) / np.log(self.v)) #entropy score
        return self.p

    def beta(self,f,g=None):
        if g==None: 
            g=self.g
        pg = np.multiply(self.p.T,g)
        pf = np.multiply(self.p.T,f)
        return (np.linalg.inv(pg.T*pg)*pg.T*np.multiply(self.p.T,f)).T

def createPaths(spot,vol,dt=1,drift=0,num=10000,volCorr=True):
    dt=np.array(dt).T
    rnd=np.random.normal(size=(num,len(dt)))
    rnd=np.vstack([rnd,-rnd])
    if volCorr:
        paths=(drift-(vol**2)/2)*dt+vol*np.sqrt(dt)*rnd
    else:
        paths=vol*np.sqrt(dt)*rnd    
    return np.matrix(rnd),np.matrix(spot*np.exp(np.cumsum(paths,axis=1)))
    
    
def plot(series,bins,weights=None):
    (x,y) = np.histogram(series,bins=bins,weights=weights)
    plt.plot(y[1:],x)
    plt.hold(True)
   
def plotScenarios(prices,step=0.002):
    equal=w.p.T/w.p.T/w.v
    for a in range(len(dt)):
        plt.subplot(3,2,a+1)
        plot(prices[:,a],weights=w.p.T,bins=np.arange(1.0,2,step))
        plot(prices[:,a],weights=equal,bins=np.arange(1.0,2,step))
        plt.title("%s days" % dates[a])
        