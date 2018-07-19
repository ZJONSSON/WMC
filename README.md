# WMC - Weighted Monte Carlo

## Background
This git is the basis for a simple weighted-monte-carlo engine in Python.   The included example is a recreation of the FX options example in [Avelleneda et al] [1], with a twist.  To examine the strength of the WMC methodology we start with a uniform prior and examine if spot/forward restrictions are enough to ensure a martingale.  Findings indicate that specific martingale restrictions need to be placed, i.e. E(  random_t1 * random_t2 ) = 0      

## Analysis
For each of the dates the absolute price is RND[0,1] +1  (so uniform in the area 1.0-2.0) with no relationship between any consecutive dates.   (horrible prior)   I use 1 million paths and a linear least-squares weight of 10^-4


For me, the best way to understand if the paths are well behaved is to look at the probability weighted correlation matrix of the „random variable“ behind the process, either by looking at the rnd variable itself (if created as random walk) or (here) by taking log difference of prices adjusted by forward carry (should also have expectation of being zero, with fwd restrictions in place)

### Correlations without optimization:
When I take the price difference between dates (adjusted for cost of carry) I get (not surprisingly for uniform) the following correlation matrix:

    [[ 1.        , -0.70656293, -0.00188757,  0.00180384,  0.00087913],
     [-0.70656293,  1.        , -0.49829579, -0.00248809,  0.00053002],
     [-0.00188757, -0.49829579,  1.        , -0.49854834, -0.00133974],
     [ 0.00180384, -0.00248809, -0.49854834,  1.        , -0.49993861],
     [ 0.00087913,  0.00053002, -0.00133974, -0.49993861,  1.        ]]

(each row and column stands for each of the option maturities, i.e. 30/60/90/180/270 days)

### Correlation with optimization (Spot forward restrictions):
If I optimize with regular forward restrictions the correlations go down but are still significant:

      [[ 1.        , -0.58799939,  0.03659394, -0.02800753,  0.02183336],
       [-0.58799939,  1.        , -0.52914431, -0.00374825,  0.0017899 ],
       [ 0.03659394, -0.52914431,  1.        , -0.43120378, -0.00525967],
       [-0.02800753, -0.00374825, -0.43120378,  1.        , -0.52192153],
       [ 0.02183336,  0.0017899 , -0.00525967, -0.52192153,  1.        ]]

### Correlation with optimization (Forward starting forwards)
When I change the forward restrictions to forward starting, i.e. E(priceT+1)  =  priceT * exp(-1.64%*dt) I get slightly better results for consecutive dates, but slightly worse for dates further apart from each other:

     [[ 1.        , -0.57044388, -0.01808925, -0.02308182,  0.03208339],
      [-0.57044388,  1.        , -0.50096637, -0.00180821, -0.01450118],
      [-0.01808925, -0.50096637,  1.        , -0.44453141,  0.01145468],
      [-0.02308182, -0.00180821, -0.44453141,  1.        , -0.53093579],
      [ 0.03208339, -0.01450118,  0.01145468, -0.53093579,  1.        ]]

### Correlation with optimization (Spot fwd + combined martingale restrictions):
Finally I start with a combination of all the dates  as pairs: [1,2],[1,3],[1,4],[1,5],[2,3],[2,4],[2,5],[3,4],[3,5],[4,5] and for each pair I add the restriction that E(  random[a] * random[b] ) = 0      (by „random“ I mean the zero-mean random variable behind price movements across time) 

     [[ 1.        , -0.02098924, -0.02514469,  0.01020891, -0.03614042],
      [-0.02098924,  1.        ,  0.00662175,  0.0144592 ,  0.03226708],
      [-0.02514469,  0.00662175,  1.        , -0.04688758, -0.0516021 ],
      [ 0.01020891,  0.0144592 , -0.04688758,  1.        , -0.05072448],
      [-0.03614042,  0.03226708, -0.0516021 , -0.05072448,  1.        ]]

And here is the relative price fit as a percentage of option PV , i.e.   (Calculated Price – Calibrated price) / Calibrated Price

    matrix([[-0.02276719, -0.02100991,  0.01974781,  0.02319515, 0.00672846,
             0.01470705, -0.0202395 ,  0.00905647,  0.02811023,  0.0189954 ,
             0.06311824,  0.02943987,  0.01516166,  0.05183629,  0.12494329,
             0.03300863,  0.00487053,  0.00297626,  0.00208457,  0.04756106,
             0.02986835,  0.03540541,  0.01244186,  0.0380617 ,  0.08836308,
                 inf,        -inf,         inf,         inf,         inf,
                -inf,        -inf,        -inf,        -inf,        -inf,
                -inf,        -inf,        -inf,        -inf,        -inf]])

This is the closest to martingale so far, using broad based measures (forwards and products of zero-mean random variables).   There could be hidden relationships (i.e. spot dependent expectations) not captured, but managing them can quickly become very complex. 

I found that if I only conditioned the E( random[a] * random[b] ) = 0 on consecutive dates I still ended up with significant correlations for the dates that are further apart. 

## Few thoughts

 - Forward starting contracts are better than spot-fwd for calibration, but do not strictly enforce conditional martingale

 - Important to look at the var/covar or correlation matrix of the probability weighted „random variable“ behind the process across dates 

 - If significant correlations are present,  a firmer martingale condition needs to be added (i.e. expected product of two zero-mean random variables should be zero)

 - It might be important to use variable weights with hard-martingale conditions as there can be a balance between ensuring the martingale principle, vs matching prices.  I simply used a multiplier in the constraints to find a balance.

The whole exercise is probably not necessary for any calculations where the prior is a martingale and the resulting distribution doesn’t deviate far from the prior.   But it’s probably better to be on the lookout for any persistent correlations.   I‘m presently surprised being able to go from a simple uniform distribution to a full martingale process that explains the prices of all options/forwards.  Terminal distributions look strikingly similar to the lognormal prior.

The two attached distribution pictures attached show the terminal distributions for each maturity.  The green line is the prior distribution and the blue line is the resulting distribution after optimization.   In addition to the uniform prior I ran the model with lognormal prior (static 14% vol) and resulting distributions look similar.     The 500 paths image shows top probable paths from the uniform distribution for (i) unconstrained, (ii) fwd/opt constrained (still heavy negative correlation and (iii) with the extra martingale constraints.
## Figures
#### Figure 1: Uniform Prior -> WMC results
![Alt text](http://zjonsson.github.com/WMC/Distribution_uniformPrior.png "UniformPrior")
#### Figure 2: Lognormal Prior -> WMC results
![Alt text](http://zjonsson.github.com/WMC/Distribution_LognormalPrior.png "UniformPrior")
#### Figure 3: Uniform Paths and the top 500 paths by weight
![Alt text](http://zjonsson.github.io/WMC/500%20paths%20uniform.png)



  [1]: http://www.math.nyu.edu/faculty/avellane/weightedmontecarlo.pdf        "WEIGHTED MONTE CARLO: A NEW TECHNIQUE FOR CALIBRATING ASSET-PRICING MODELS"
