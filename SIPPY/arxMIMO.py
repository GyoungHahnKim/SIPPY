# -*- coding: utf-8 -*-
"""
Created on Sat Aug 12 2017

@author: Giuseppe Armenise
"""
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from builtins import range
from builtins import object
from past.utils import old_div
from .functionset import *
import sys

def ARX_MISO_id(y,u,na,nb,theta):
    nb=np.array(nb)
    theta=np.array(theta)
    u=1.*np.atleast_2d(u)
    ylength=y.size
    ystd,y=rescale(y)
    [udim,ulength]=u.shape
    if nb.size!=udim:
        sys.exit("Error! nb must be a matrix, whose dimensions must be equal to yxu")
#        return np.array([[1.]]),np.array([[0.]]),np.array([[0.]]),np.inf
    elif theta.size!=udim:
        sys.exit("Error! theta matrix must have yxu dimensions")
#        return np.array([[1.]]),np.array([[0.]]),np.array([[0.]]),np.inf
    else:
        nbth=nb+theta
        Ustd=np.zeros(udim)
        for j in range(udim):
            Ustd[j],u[j]=rescale(u[j])
        val=max(na,np.max(nbth))
        N=ylength-val
        phi=np.zeros(na+np.sum(nb[:]))
        PHI=np.zeros((N,na+np.sum(nb[:])))
        for k in range(N):
            phi[0:na]=-y[k+val-1::-1][0:na]
            for nb_i in range(udim):
                phi[na+np.sum(nb[0:nb_i]):na+np.sum(nb[0:nb_i+1])]=u[nb_i,:][val+k-1::-1][theta[nb_i]:nb[nb_i]+theta[nb_i]]
            PHI[k,:]=phi
        THETA=np.dot(np.linalg.pinv(PHI),y[val::])
        Vn=old_div((np.linalg.norm((np.dot(PHI,THETA)-y[val::]),2)**2),(2*N))
        DEN=np.zeros((udim,val+1))
        NUMH=np.zeros((1,val+1))
        NUMH[0,0]=1.
        DEN[:,0]=np.ones(udim)
        NUM=np.zeros((udim,val))
        for k in range(udim):
            THETA[na+np.sum(nb[0:k]):na+np.sum(nb[0:k+1])]=THETA[na+np.sum(nb[0:k]):na+np.sum(nb[0:k+1])]*ystd/Ustd[k]
            NUM[k,theta[k]:theta[k]+nb[k]]=THETA[na+np.sum(nb[0:k]):na+np.sum(nb[0:k+1])]
            DEN[k,1:na+1]=THETA[0:na]
        return DEN,NUM,NUMH,Vn

#MIMO function
def ARX_MIMO_id(y,u,na,nb,theta,tsample=1.):
    na=np.array(na)
    nb=np.array(nb)
    theta=np.array(theta)
    [ydim,ylength]=y.shape
    [udim,ulength]=u.shape
    [th1,th2]=theta.shape
    if na.size!=ydim:
        sys.exit("Error! na must be a vector, whose length must be equal to y dimension")
#        return 0.,0.,0.,0.,np.inf
    elif nb[:,0].size!=ydim:
        sys.exit("Error! nb must be a matrix, whose dimensions must be equal to yxu")
#        return 0.,0.,0.,0.,np.inf
    elif th1!=ydim:
        sys.exit("Error! theta matrix must have yxu dimensions")
#        return 0.,0.,0.,0.,np.inf
    elif (np.issubdtype((np.sum(nb)+np.sum(na)+np.sum(theta)),int) and np.min(nb)>=0 and np.min(na)>=0 and np.min(theta)>=0)==False:
        sys.exit("Error! na, nb, theta must contain only positive integer elements")
#        return 0.,0.,0.,0.,np.inf
    else:
        Vn_tot=0.
        NUMERATOR=[]
        DENOMINATOR=[]
        DENOMINATOR_H=[]
        NUMERATOR_H=[]
        for i in range(ydim):
            DEN,NUM,NUMH,Vn=ARX_MISO_id(y[i,:],u,na[i],nb[i,:],theta[i,:])
            DENOMINATOR.append(DEN.tolist())
            NUMERATOR.append(NUM.tolist())
            NUMERATOR_H.append(NUMH.tolist())
            DENOMINATOR_H.append([DEN.tolist()[0]])
            Vn_tot=Vn_tot+Vn
        G=cnt.tf(NUMERATOR,DENOMINATOR,tsample)
        H=cnt.tf(NUMERATOR_H,DENOMINATOR_H,tsample)
        return DENOMINATOR,NUMERATOR,G,H,Vn_tot

#creating object ARX MIMO model
class ARX_MIMO_model(object):
    def __init__(self,na,nb,theta,ts,NUMERATOR,DENOMINATOR,G,H,Vn):
        self.na=na
        self.nb=nb
        self.theta=theta
        self.ts=ts
        self.NUMERATOR=NUMERATOR
        self.DENOMINATOR=DENOMINATOR
        self.G=G
        self.H=H
        self.Vn=Vn