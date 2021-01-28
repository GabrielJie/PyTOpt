

import numpy as np
import calfem.utils as cfu
import Mesh
import calfem.vis as cfv
import FE
import Opt
import Filter
import matplotlib.pyplot as plt
import calfem.core as cfc


def _Main(g,el_type,force,bmarker):
     
    #Settings
    E=210*1e9
    v=0.3
    ptype=2         #ptype=1 => plane stress, ptype=2 => plane strain
    ep=[ptype,1,2]    #ep[ptype, thickness, integration rule(only used for QUAD)]  
    mp=[E,v]
    change = 2
    loop = 0
    SIMP_penal = 3
    rMin = 0.1
    volFrac = 0.5
    
    """MESHING"""
    _mesh = Mesh.Mesh(g,0.04)
    
    if el_type == 2:
        coords, edof, dofs, bdofs = _mesh.tri()
    elif el_type ==3:
        coords, edof, dofs, bdofs = _mesh.quad()
    else:
        print("Wrong el_type!")
    
    #cfv.drawMesh(coords, edof, 2, el_type)
    nElem=np.size(edof,0)
    x =np.zeros([nElem,1])+0.1
        
    """ Denote forces and boundary conditions """
    nDofs = np.max(edof)
    f = np.zeros([nDofs,1])
    
    bc = np.array([],'i')
    bcVal = np.array([],'f')
    
    bc, bcVal = cfu.applybc(bdofs, bc, bcVal, bmarker, value=0.0, dimension=0)
    
    
    cfu.applyforce(bdofs, f, force[1], force[0], force[2])
    
    
    """ Optimisation """


    
    while change > 0.0001:
        
        loop = loop + 1
        xold = x.copy()
        
        U = FE._FE(x,SIMP_penal,edof,coords,bc,f,ep,mp)
        

        #Check sizes
        nElem=np.size(edof,0)
        nx=coords[:,0]
        ny=coords[:,1]
        
            
        
        #Check element type
        if len(edof[0,:])==6:   #Triangular Element
            Tri=True
            elemX=np.zeros([nElem,3])
            elemY=np.zeros([nElem,3])
        elif len(edof[0,:])==8:
            Tri=False           #Use Quad Instead
            elemX=np.zeros([nElem,4])
            elemY=np.zeros([nElem,4])
        else:
            raise Exception('Unrecognized Element Shape, Check eDof Matrix')
    
    
        #Find The coordinates for each element's nodes
        for elem in range(0,nElem):
            
            nNode=np.ceil(np.multiply(edof[elem,:],0.5))-1
            nNode=nNode.astype(int)
            
            elemX[elem,:]=nx[nNode[0:8:2]]
            elemY[elem,:]=ny[nNode[0:8:2]]
    
        
        #Linear Elastic Constitutive Matrix
        D=cfc.hooke(ptype, E, v)
                        
        dc = xold.copy()      
        if Tri:  #Tri Elements
            for elem in range(0,nElem):  
                Ke=cfc.plante(elemX[elem,:],elemY[elem,:],ep[0:2],D)                    #Element Stiffness Matrix for Triangular Element
                Ue = U[np.ix_(edof[elem,:]-1)]
                dc[elem] = -SIMP_penal*x[elem][0]**(SIMP_penal-1)*np.matmul(np.transpose(Ue), np.matmul(Ke,Ue))
                
        else:    #Quad Elements
            for elem in range(0,nElem):            
                Ke=cfc.plani4e(elemX[elem,:],elemY[elem,:],ep,D)                   #Element Stiffness Matrix for Quad Element
                Ue = U[np.ix_(edof[elem,:]-1)]
                dc[elem] = -SIMP_penal*x[elem][0]**(SIMP_penal-1)*np.matmul(np.transpose(Ue), np.matmul(Ke[0],Ue))

        #breakpoint()
        dc = Filter.Check(edof,coords,dofs,rMin,x,dc)
        #breakpoint()
        try:
            x = Opt.Optimisation().OC(nElem,x,volFrac,dc)
        except:
            print("Optimisation is not yet implemented")
        
        change =np.max(np.max(abs(x-xold)))
        print(change)
        
        if loop == 500:                                                          # If alternating
            break
        
        
    """ Visualisation """
    
    cfv.draw_element_values(x, coords, edof, 2, el_type,displacements=U,
                      draw_elements=True, draw_undisplaced_mesh=False, 
                      title="Density", magnfac=1.0)
    
    cfv.showAndWait()

    