from __future__ import division
import numpy as np,scipy
from wmc import *
   
dates = np.array([30,60,90,180,270])  #number of days until each expiry date
df=np.exp(-0.0427*dates/365)          #discounted factors based on the DEM Rate
dt=np.diff(np.r_[0,dates])/365.0      #difference between each consecutive expiry date as a fraction of one year


num=500000   # We create 500k paths

prices = np.matrix(np.random.rand(num,len(dt)))+1
pricesPrior=np.hstack([np.ones(shape=(num,1))*1.4887,prices[:,0:-1]])   # create a matrix of prior prices (and current spot as first column)
pricesPrior=np.multiply(np.exp(-0.0164*dt),pricesPrior)   # add cost of carry to prior prices to create an expectation for "current price"
rnd = np.log(prices/pricesPrior)    # this would have been the random variable behind a price process (expected value = 0)

#Uncomment the line below to overwrite the prior as a lognormal 14% vol
rnd,prices= createPaths(spot=1.4887,vol=0.14,dt=dt,num=num/2,drift=-0.0164,volCorr=True)

data=np.array([[30,1,1.5421,0.007],
                [30,1,1.531,0.0093],
                [30,1,1.4872,0.0234],
                [30,-1,1.4479,0.0092],
                [30,-1,1.4371,0.0069],
                [60,1,1.5621,0.0094],
                [60,1,1.5469,0.0126],
                [60,1,1.4866,0.0319],
                [60,-1,1.4312,0.0128],
                [60,-1,1.4178,0.01],
                [90,1,1.5764,0.0112],
                [90,1,1.558,0.0149],
                [90,1,1.4856,0.0378],
                [90,-1,1.4197,0.0153],
                [90,-1,1.4038,0.0114],
                [180,1,1.6025,0.0141],
                [180,1,1.5779,0.0191],
                [180,1,1.4823,0.0505],
                [180,-1,1.3902,0.0216],
                [180,-1,1.3682,0.0162],
                [270,1,1.6297,0.0173],
                [270,1,1.5988,0.0226],
                [270,1,1.4793,0.0598],
                [270,-1,1.371,0.0254],
                [270,-1,1.3455,0.019],
                [30,0,1.486695,0],
                [60,0,1.484692,0],
                [90,0,1.482692,0],
                [180,0,1.476708,0],
                [270,0,1.470749,0]])



g=np.matrix(np.zeros(shape=(num,len(data))))    # initialize payoff matrix  ( V x N ) 
C=np.zeros(shape=(len(data)))                   # initialize price vector (N)

# Calculate the PV of payoffs for all the instruments
for no,line in enumerate(data):
    dateidx = dates.tolist().index(line[0])
    # insert the discounted payoffs based on product type
    if line[1]==1:          # Call option (+1)
        g[:,no]=np.maximum(prices[:,dateidx]-line[2],0)*df[dateidx]
    elif line[1]== -1:      # Put option (-1)
        g[:,no]=np.maximum(line[2]-prices[:,dateidx],0)*df[dateidx]
    else:                   # Forward (0)
        g[:,no]=(line[2]-prices[:,dateidx])*df[dateidx]
    C[no]=line[3]           # Current Price added to the price vector


# Create combination pairs of every 2 dates
comb = [a for a in it.combinations(range(0,len(dates)),2)]

EE=np.matrix(np.zeros(shape=(num,len(comb))))  #initialize the E( rnd[timeA] * rnd[timeB] )
EC=np.zeros(len(comb))                          # They should all have a PV of zero
for no,c in enumerate(comb):
    EE[:,no]=np.multiply(rnd[:,c[0]],rnd[:,c[1]])   # fill in the E with product of error vectors


# add the martingale restrictions to the cashflows.  Remove if not needed.
g=np.hstack([g,EE*1])     # multiply by 300 to give increased weight  (art not science)
C=np.hstack([C,EC])         # add the zero PV



w=WMC(g,C)
import time
t=time.time()
w.solve(True,0.00001)
print "...took %s seconds" % (time.time()-t)
print "correlation matrix"
print np.corrcoef(np.multiply(w.p.T,rnd).T)
print "price match: "
print (w.P-w.C)/w.C