import numpy as np
import time
from scipy.sparse import csc_matrix, linalg, csr_matrix, lil_matrix, coo_matrix
from scipy.sparse.linalg import spsolve
import calfem.core as cfc



def Check(x,dc,H):
    
    #Settings
    Timers=True
    tic = time.perf_counter()
    nElem=np.size(x)
    new_dc=np.zeros([nElem,1])


    #new_dc=np.transpose((np.sum(np.transpose(x)*H[:,:]*np.transpose(dc), axis=1))/(np.transpose(x[:])*np.sum(H[:,:], axis=1)))
    #breakpoint()
    #breakpoint()
    #breakpoint()
    for elem in range(nElem):

        new_dc[elem]=(sum(dc.reshape(len(dc))*H[:,elem].toarray().reshape(len(dc))*x.reshape(len(dc))))/(np.sum(H[elem,:]*x[elem][0]))
        #new_dc[elem]=(x*np.sum(H, axis=1).tolist()/(x[elem]*np.sum(H, axis=1).tolist()))*dc[elem]
        
    #    new_dc[elem]=dc[elem]*((H[elem,:]*x[:])/((x[elem])*np.sum(H[elem,:])))

    #new_dc=new_dc.reshape(np.size(new_dc),1)
    
    
    if Timers:
        toc = time.perf_counter()  
        print('Check Time: '+str(toc-tic))
    return new_dc






























