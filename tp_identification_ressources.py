# Parameter identification

import math
import sys

import donnees_identification.my_gmshparser as gmp
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import scipy.sparse as sp
import scipy.sparse.linalg as spl


"""
Utility : progress bar
Found on https://handhikayp.medium.com/creating-terminal-progress-bar-using-python-without-external-library-b51dd907129c
"""
def progress_bar(iteration, total, prefix='', suffix='', length=30, fill='#'):
    percent = ("{0:.1f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    sys.stdout.write(f'{prefix} |{bar}| {percent}% {suffix}\r')
    sys.stdout.flush()

"""
Interpolates a scalar field U from mesh1 to mesh2
"""
def meshInterpolate( u1, mesh1, mesh2 ):

   # Extract simple connectivity lists
   coords1, nnodes1 = coordsNodes( mesh1 )
   coords2, nnodes2 = coordsNodes( mesh2 )
   elemen1, nelems1 = connectivity( mesh1 )
   
   u2 = np.zeros( nnodes2 )
   
   x1 = coords1[elemen1[:,0],0]; y1 = coords1[elemen1[:,0],1]
   x2 = coords1[elemen1[:,1],0]; y2 = coords1[elemen1[:,1],1]
   x3 = coords1[elemen1[:,2],0]; y3 = coords1[elemen1[:,2],1]
   
   for i in range(nnodes2):
      x = coords2[i,0]; y = coords2[i,1]
       
      D1 = (x2-x)*(y3-y) - (x3-x)*(y2-y) # Those are term-to-term products because I do vectorize stuff
      D2 = (x3-x)*(y1-y) - (x1-x)*(y3-y)
      D3 = (x1-x)*(y2-y) - (x2-x)*(y1-y)
      D0 = D1+D2+D3

      j1 = np.argwhere(D0*D1 >= 0)
      j2 = np.argwhere(D0*D2 >= 0)
      j3 = np.argwhere(D0*D3 >= 0)
      j  = np.intersect1d( np.intersect1d(j1,j2,assume_unique=True), j3, assume_unique=True )

      # A node can be at a frontier, in that case, choose a random element (the first one in the list)
      if np.size(j) >= 1: # Otherwise, the value is zero
         j = j[0]
         
         elt = elemen1[j,:]
         a = D1[j]/D0[j]; b = D2[j]/D0[j]; d = D3[j]/D0[j]

         u2[i] = a*u1[elt[0]] + b*u1[elt[1]] + d*u1[elt[2]]

   return u2

"""
Divides the elements of a mesh into cells of a regular grid
 @inputs :
  mesh : the mesh in question
  Nx   : Nb of horizontal regions
  Ny   : Nb of vertical regions
 @output :
  W : matrix such that Wij=1 iff center of element i belongs to cell j
"""
def meshDivide( mesh, Nx, Ny ):

   # Extract simple connectivity lists
   coords, nnodes = coordsNodes( mesh )
   elemen, nelems = connectivity( mesh )
   
   # Bounds
   xmax = np.max(coords[:,0])
   xmin = np.min(coords[:,0])
   ymax = np.max(coords[:,1])
   ymin = np.min(coords[:,1])
   
   # List of nodes coordinates, then element coordinates
   x1 = coords[elemen[:,0],0]; y1 = coords[elemen[:,0],1]
   x2 = coords[elemen[:,1],0]; y2 = coords[elemen[:,1],1]
   x3 = coords[elemen[:,2],0]; y3 = coords[elemen[:,2],1]
   xe = 1/3 * (x1+x2+x3)
   ye = 1/3 * (y1+y2+y3)
   
   W = np.zeros((nelems,Nx*Ny))
   
   for i in range(Nx):
      for j in range(Ny):
         mij = i*Ny + j # Multi-index
         xi = xmin + i*(xmax-xmin)/Nx # Inferior bound
         xs = xmin + (i+1)*(xmax-xmin)/Nx # Superior bound
         yi = ymin + i*(ymax-ymin)/Ny # Inferior bound
         ys = ymin + (i+1)*(ymax-ymin)/Ny # Superior bound
         
         ix = np.where(xe>xi)
         sx = np.where(xe<=xs)
         iy = np.where(ye>yi)
         sy = np.where(ye<=ys)
         
         intersect = np.intersect1d( np.intersect1d(ix,sx) , np.intersect1d(iy,sy) )
         W[ intersect, mij ] = 1
         
   # TODO: for safety, one should check each line of W has only one non-zero value...
   return W

"""
Unify the nodes list (forget nodes entities)
"""
def coordsNodes( mesh ):
   nnodes = mesh.get_number_of_nodes()
   coords = np.zeros( (nnodes,2) )
   #tags = 
   
   inc = 0
   for entity in mesh.get_node_entities():
      for node in entity.get_nodes():
         #entity.get_tag()
         ncoords = node.get_coordinates()
         coords[inc,0] = ncoords[0]
         coords[inc,1] = ncoords[1]
         inc += 1
         
   return coords, nnodes # TODO: maybe, return tags as well. Tags are supposed to be ordered 1->nnodes
   
"""
Unify the elements list (forget elements entities)
"""
def connectivity( mesh ):
   # Get total numbers of elements
   nelems = 0
   for entity in mesh.get_element_entities():
      if entity.get_element_type() == 2:       # Triangle elements only
         nelems += entity.get_number_of_elements()
   
   tri = np.zeros( (nelems,3), dtype=int )

   # Populate tri
   inc = 0
   for entity in mesh.get_element_entities():
      eltype = entity.get_element_type()
      if eltype == 1: # 2-nodes segment
         eltype=0
      elif eltype == 2: # 3-nodes triangle
         for element in entity.get_elements():
            elcon = element.get_connectivity()
            tri[inc,:] = elcon
            inc += 1
   
   tri = tri-1  # tri-1 because gmsh starts at 1 and python at 0
   
   return tri, nelems

"""
Plots the mesh, and if requested, a scalar field U on top of it
 @inputs
  mesh : mesh to plot
  U    : (optionnal) scalar field at nodes (mutually exclusive with S)
  S    : (optionnal) scalar field at elements (mutually exclusive with U)
  rmin : (optionnal) minimal range of value
  rmax : (optionnal) maximal range of value
"""
def plotMesh( mesh, U=None, S=None, rmin=None, rmax=None ):
        
   coords, nnodes = coordsNodes( mesh )
   tri   , nelems = connectivity( mesh )
   
   plt.figure()
   
   if (not(U is None)):
      plt.tricontourf( coords[:,0], coords[:,1], tri, U, cmap='jet', levels=256 )
      plt.colorbar()
   elif (not(S is None)):
      plt.tripcolor( coords[:,0], coords[:,1], tri, facecolors=S, cmap='jet' )
      plt.colorbar()
   else:
      plt.triplot( coords[:,0], coords[:,1], tri, color='black' )
   
   plt.axis('equal')
   plt.axis('off')
   plt.tight_layout()
   if (not(rmin is None) and not (rmax is None)): # Set range
      plt.clim(rmin,rmax)
   plt.show()
   
   #plt.tripcolor( coords[:,0], coords[:,1], tri, V, cmap='jet', levels=256 )
   
   
"""
Computes elementary FE matrices for scalar fields
/!\ This function only handles T3 elements /!\
Output as a list of tri-vector sparse matrices

input  : mesh
         deriv : if 0, Mass matrices are computed (\int vu dV), if 1, Stiffness (\int grad(v)grad(u) dV for Laplace equation).
output : ind, list of indices I
         jnd, list of indices J
         Kel, list of corresponding coefficients
         elset : list of elsets corresponding to each elementary matrix
"""
def ElMats( mesh, deriv=1 ):

   coords, nnodes = coordsNodes( mesh )
   
   nelems = 0
   for entity in mesh.get_element_entities():
      if entity.get_element_type() == 2:       # Triangle elements only
         nelems += entity.get_number_of_elements()
         
   ind   = np.zeros( (nelems,9), dtype=int )
   jnd   = np.zeros( (nelems,9), dtype=int )
   Kel   = np.zeros( (nelems,9) )
   elset = np.zeros( nelems, dtype=int )

   elt = 0
   for entity in mesh.get_element_entities():
      if entity.get_element_type() == 2:
         for element in entity.get_elements():
            elcon = element.get_connectivity()
            
            n1 = elcon[0]-1   # Numbering starts at 1 on GMSH, hence the (-1)
            n2 = elcon[1]-1
            n3 = elcon[2]-1
            
            x1 = coords[n1,0]; x2 = coords[n2,0]; x3 = coords[n3,0]
            y1 = coords[n1,1]; y2 = coords[n2,1]; y3 = coords[n3,1]
            
            S  = .5*((x2-x1)*(y3-y1)-(x3-x1)*(y2-y1)) # Element surface
                       
            if deriv == 0:
               Be = 1/3 * np.array( [[1,1,1]] )
            else:
               Be = np.array( [[y2-y3,y3-y1,y1-y2],[x3-x2,x1-x3,x2-x1]] ) / (2*S) # Gradient matrix
               
            Ke = abs(S)*(Be.T@ Be);
            
            ind[elt,:] = np.array( [n1,n2,n3,n1,n2,n3,n1,n2,n3] )
            jnd[elt,:] = np.array( [n1,n1,n1,n2,n2,n2,n3,n3,n3] )
            Kel[elt,:] = Ke.flatten()
            
            elset[elt] = entity.get_tag()
            
            elt += 1
            
   # IMPORTANT NOTE: in a "normal" FE code, we would want to build the stiffness matrix right now
   # However, in the current context of inverse problem, the material property will change all the time
   # So the proper building will be done in a separate function
   # And the costly pre-building here will be done once for all
         
   return ind, jnd, Kel, elset
   
"""
Builds the stiffness matrix
"""
def assemK( mesh, ind, jnd, Kel, elset, paramdict ):

   nelem = np.shape(Kel)[0]
   inK = []
   jnK = []
   vnK = []
   
   for elt in range(nelem):
      entity = elset[elt]
      v = paramdict[ entity ]
   
      inK.extend(np.ndarray.tolist(ind[elt,:]))
      jnK.extend(np.ndarray.tolist(jnd[elt,:]))
      vnK.extend(np.ndarray.tolist(v*Kel[elt,:]))
   
   nnodes = mesh.get_number_of_nodes()
   K0 = sp.csr_matrix((vnK, (inK,jnK)), shape=(nnodes, nnodes))
   
   return K0
   
"""
Computes constraint matrix and right hand side for Dirichlet

input : mesh
        dirichletdict : dictionnary {physical_index : value}
        zerozero : if True, a Dirichlet condition at value 0 is added at node 0 (for Neumann-only computations)
output : C and d such that Cu=d
"""
def DirichletScalar( mesh, dirichletdict, zerozero=False ):
   inC = []
   jnC = []
   vnC = [] # Prepare lists for sparse matrix
   
   ind = []
   vnd = []
   
   noeq = 0 # Iterator (index of the current equation)
   
   for entity in mesh.get_element_entities():
      if entity.get_element_type() == 1:
         physical = mesh.physdict1[ entity.get_tag() ] # Get the physical set the entity belongs to
         v = dirichletdict.get( physical )
         
         if v != None:
            mynodes = set() # In sets, duplicates will be automatically removed
            for element in entity.get_elements():
               elcon = element.get_connectivity()
               mynodes.add( elcon[0]-1 )  # Numbering starts at 1 on GMSH, hence the (-1)
               mynodes.add( elcon[1]-1 )
               
            for node in mynodes: # Build C and d (sparse trivector format)
               inC.append(noeq)
               jnC.append(node)
               vnC.append(1.)
               ind.append(noeq) # Yeah, it's a ducplicate of inC
               vnd.append(v)
               
               noeq += 1 # increment nb of equations
   
   if zerozero:
      if len(inC) != 0: # Warn. TODO: proper warning
         print("You are imposing node 0 at 0 while there are other Dirichlet BCs. Probably not what you want (unless you know what you do).")
         
      inC.append(noeq)
      jnC.append(0)
      vnC.append(1.)
      ind.append(noeq)
      vnd.append(0.)
      noeq += 1
      
   jnd = [0]*len(ind) # Row in vector is 0 everywhere
   
   # Actually define and return sparse matrices
   nnodes = mesh.get_number_of_nodes()
   C = sp.csr_matrix((vnC, (inC,jnC)), shape=(noeq, nnodes))
   d = sp.csr_matrix((vnd, (ind,jnd)), shape=(noeq, 1))
   
   return C, d
   
"""
Computes Rhs corresponding to Neumann BCs

input : mesh
        neumanndict : dictionnary {physical_index : value}
output : f (sparse format)
"""
def NeumannNormal( mesh, neumanndict ):

   coords, nnodes = coordsNodes( mesh )

   inf = []
   vnf = []

   for entity in mesh.get_element_entities():
      if entity.get_element_type() == 1:
         physical = mesh.physdict1[ entity.get_tag() ] # Get the physical set the entity belongs to
         v = neumanndict.get( physical )
         
         if v != None:
            for element in entity.get_elements():
               elcon = element.get_connectivity()
               n1 = elcon[0]-1
               n2 = elcon[1]-1
               
               x1 = coords[n1,0]
               x2 = coords[n2,0]
               y1 = coords[n1,1]
               y2 = coords[n2,1]
               
               l = math.sqrt( (x2-x1)**2 + (y2-y1)**2 )
               
               inf.append(n1)
               vnf.append(v*l/2)
               inf.append(n2)
               vnf.append(v*l/2)
               
   jnf = [0]*len(inf) # Row in vector is 0 everywhere
   
   f = sp.csr_matrix((vnf, (inf,jnf)), shape=(nnodes, 1))
   
   return f
   
"""
Transforms min_{Cx=d} .5 x^TK0x - x^Tf0 into Kx = f
With separated projection method
(idea is to separately project the minimization into the kernel of C and its image)
"""
def minCstr( K0, f0, C, d ):
   
   kappa = np.max(K0.diagonal()) # Ponderation parameter (not so important until K has >10^16 terms)
   P, ImP, CCC = PImPnCCC( C )
   
   K  = ImP @ (K0 @ ImP) + kappa*P  # TODO: check somewhere that C and K0 have compatible sizes
   fd = CCC @ d
   f  = ImP @ (f0 - K0 @ fd) + kappa * fd
   
   return K, f
   
"""
Computes projectors for minCstr
"""
def PImPnCCC( C ):

   myshape = C.shape[1]
   
   # This builds the projectors (P and ImP)
   CC = C @ C.T
   CC = CC.todense() # This matrix is actually dense
   CC1 = np.linalg.pinv(CC)
   CC1 = sp.csr_matrix(CC1) # Use csr for P to be naturally csr
   CCC = C.T @ CC1
   P = CCC @ C
   ImP = sp.identity(myshape) - P # 1-P
   
   return P, ImP, CCC
   
"""
Simulates the measurement by performing a FE computation with imposed pressure
Returns inwards fluxes, whole displacement and projector Pi

The output of this function can be used 4 ways (only 3 and 4 are practically meaningful) :
1) Identification problems use same Dirichlet BCs to identify parameters using u
2) Identification problems use phi1 to phi4 Neumann BCs to identify parameters using u
3) Identification problems use same Dirichlet BCs to identify parameters using phi1 to phi4
4) Identification problems use phi1 to phi4 Neumann BCs to identify parameters using P1 to P4. In that case, Pi is such that Pi u = [P1,P2,P3,P4]
"""
def simulateMeasurement( dirichletdict, paramdict, mesh, noise=0 ):

   # FE computation
   ind, jnd, Kel, elset = ElMats( mesh )
   C, d = DirichletScalar( mesh, dirichletdict )
   f0 = NeumannNormal( mesh, {} ) # No Neumann bounds
   K0 = assemK( mesh, ind, jnd, Kel, elset, paramdict )
   K, f = minCstr( K0, f0, C, d )
   u = spl.spsolve(K,f)
   
   # Compute nodal exterior fluxes
   fext = K0 @ u # All exterior forces
   C1 = DirichletScalar( mesh, {1:0} )[0] # Projectors
   C2 = DirichletScalar( mesh, {2:0} )[0]
   C3 = DirichletScalar( mesh, {3:0} )[0]
   C4 = DirichletScalar( mesh, {4:0} )[0]
   f1 = C1 @ fext # Nodal fluxes
   f2 = C2 @ fext
   f3 = C3 @ fext
   f4 = C4 @ fext
   phi1 = np.sum(f1) # Total resulting inwards flux
   phi2 = np.sum(f2)
   phi3 = np.sum(f3)
   phi4 = np.sum(f4)
   
   # TODO maybe : add noise to u
   
   # Compute projector such that Pi u = [P1,P2,P3,P4]
   s1 = C1.shape[0]
   s2 = C2.shape[0]
   s3 = C3.shape[0]
   s4 = C4.shape[0]
   on1 = np.ones((1,s1)) / s1 # Multiplication by this on1 will perform mean on rows
   on2 = np.ones((1,s2)) / s2
   on3 = np.ones((1,s3)) / s3
   on4 = np.ones((1,s4)) / s4
   Pi1 = sp.csr_matrix( on1 @ C1 )
   Pi2 = sp.csr_matrix( on2 @ C2 )
   Pi3 = sp.csr_matrix( on3 @ C3 )
   Pi4 = sp.csr_matrix( on4 @ C4 )
   Pi = sp.vstack( [Pi1,Pi2,Pi3,Pi4] )
   
   return phi1, phi2, phi3, phi4, u, Pi
   
"""
Reads a set of measurements generated by simulateMeasurement

filename    contains "normal" arrays.
filename_Pi contains the sparse array, which has its own save/load methods

example :
phi1, phi2, phi3, phi4, um, Pi, Pm = readMeasurement( "measure_sb.npz", "measure_sb_Pi.npz" )
"""
def readMeasurement( filename, filename_Pi ):
   
   with np.load( filename ) as data:
      phi1 = data['phi1']
      phi2 = data['phi2']
      phi3 = data['phi3']
      phi4 = data['phi4']
      um   = data['um']
      
   Pi = sp.load_npz(filename_Pi)
   
   #print(np.shape(Pi))
   #print(np.shape(um))
      
   Pm = Pi @ um[:,np.newaxis] # Just a shortcut
   #Pm = Pm[:,np.newaxis] # Transform it into a column vector
      
   return phi1, phi2, phi3, phi4, um, Pi, Pm

"""
Computes u^T \nabla K \lambda (the gradient)
if fullField is True, there is 1 parameter per element
else, there is 1 parameter per elset.
"""
def computeGradient( u, lambd, ind, jnd, Kel, elset, fullField=False ):
     
   nelems = np.shape(Kel)[0]
   nnodes = np.shape(u) # TODO: check lambd has same shape
   
   if fullField:
      g = np.array([[0.]*nelems]) # Initialize the gradient
   else:
      nset = np.max(elset) # Get number of elsets
      g = np.array([[0.]*nset]) # Initialize the gradient
   g = g.T # Row vector

   for elt in range(nelems):
      n1 = ind[elt,0] # Nodes
      n2 = ind[elt,1]
      n3 = ind[elt,2]
      
      uloc = np.array([ [u[n1]], [u[n2]], [u[n3]] ]) # Local U and Lambda
      lloc = np.array([ [lambd[n1]], [lambd[n2]], [lambd[n3]] ])
      
      # Kel is equal to the local \nabla K (because it has to be multiplied by the parameter to be equal to the local stiffness matrix)
      
      Kloc = np.reshape( Kel[elt,:], (3,3) )
      gloc = uloc.T @ (Kloc @ lloc)
   
      if fullField:
         entity = elt
      else:
         entity = elset[elt] - 1 # elset number starts at 1
      
      g[entity,0] += gloc
      
   return g
   
"""
Quick line-search function
 @inputs
  x0     : initial guess
  J0     : value of the cost function at x0 (to save CPU in case its known). If None, re-evaluation is performed
  d      : direction
  step0  : initial guess for the step
  np      : number of increasing steps allowed
  nm      : number of decreasing steps allowed
  functJ  : function reference for evaluation of cost function
  argJ    : extra arguments for functJ (that won't be optimized on)

 @outputs
  x     : best point found
  J     : value of the cost function at x
  step  : best step. x = x0+step*d
  extra : extra stuff given by function `functJ` at x

 Note on functJ: it has 3 outputs:
  J the value of the cost function
  extra: extra stuff
  a potentially modified version of x (for example by projection)
  for constrained optimization, functJ must include projection step before the evaluation
"""
def searchOnLine( x0, J0, d, step0, np, nm, functJ, *argJ ): # TODO: handle argJ correctly. TODO: make stuff optional
   
   if J0 == None: # Re-evaluaton needed
      J0, dummy0, dummy1 = functJ(x0,*argJ)
      
   # Initialize exponent
   expo   = 0
   expot  = expo
   expott = expo
   
   # First candidate
   xt = x0 + step0*d * 2**expo
   Jt, extrat, xt = functJ(xt,*argJ)
   
   if Jt < J0: # Solution is better than previously: increase step to see if we can do even better
      for nl in range(np):
         expott = expott+1 # Increase step (x2)
         
         xtt = x0 + step0*d * 2**expott
         Jtt, extratt, xtt = functJ(xtt,*argJ)

         if Jtt < Jt: # Better residual: store and continue increasing
            expot = expott
            xt = xtt
            Jt = Jtt
            extrat = extratt
         else: # Previous solution was better: cancel and stop increasing
            break

   else: # Jt >= J0: decrease the step until it is better
      for nl in range(nm):
         expot = expot-1 # Decrease step (/2)
         
         xt = x0 + step0*d * 2**expot
         Jt, extrat, xt = functJ(xt,*argJ)

         if Jt < J0: # Better residual: break
            break

   # TODO: now it would be great to dichotomize further between the two best steps.
   
   # Copy right solution
   x = xt
   extra = extrat
   J = Jt
   expo = expot
   step = step0*2**expo
   
   return x, J, step, extra
   
"""
Computes the FE Gradient matrix from a given triangulation
such that G@f is the gradient of the field f
This shares some similarities with the FE matrices construction functions
"""
def GradMat( coords, elemen ):

   #print(elemen)

   nnodes = np.shape(coords)[0]
   nelems = np.shape(elemen)[0]
         
   ind   = np.zeros( (nelems*6), dtype=int )
   jnd   = np.zeros( (nelems*6), dtype=int )
   Gel   = np.zeros( (nelems*6) )

   for e in range(nelems):    
      n1 = elemen[e,0]; n2 = elemen[e,1]; n3 = elemen[e,2]
      
      x1 = coords[n1,0]; x2 = coords[n2,0]; x3 = coords[n3,0]
      y1 = coords[n1,1]; y2 = coords[n2,1]; y3 = coords[n3,1]
      
      S  = .5*((x2-x1)*(y3-y1)-(x3-x1)*(y2-y1)) # Element surface
                 
      #Be = np.sqrt(abs(S)) * np.array( [[y2-y3,y3-y1,y1-y2],[x3-x2,x1-x3,x2-x1]] ) / (2*S) # Elementary Gradient matrix
      Be = np.array( [[y2-y3,y3-y1,y1-y2],[x3-x2,x1-x3,x2-x1]] ) / (2*S) # Elementary Gradient matrix. TODO: decide who is best
      
#      print(ind[6*e:6*e+6])
#      print([2*e,2*e,2*e,2*e+1,2*e+1,2*e+1])
#      print([n1,n2,n3,n1,n2,n3])
      
      ind[6*e:6*e+6] = np.array( [2*e,2*e,2*e,2*e+1,2*e+1,2*e+1] )
      jnd[6*e:6*e+6] = np.array( [n1,n2,n3,n1,n2,n3] )
      Gel[6*e:6*e+6] = Be.flatten()
      
   G = sp.csr_matrix((Gel, (ind,jnd)), shape=(2*nelems, nnodes))

   return G

if __name__ == "__main__" :

   # FE Computation example
   mesh = gmp.parse("meshes/quad_sb.msh") # Choose the mesh
   # plotMesh( mesh ) # Display mesh
   ind, jnd, Kel, elset = ElMats( mesh ) # Define elementary FE matrices (no material property at this point)
   dirichletdict = {1:1, 2:0} # This imposes pressure=1 on boundary 1 and pressure=0 on boundary 2
   C, d = DirichletScalar( mesh, dirichletdict ) # Build operators imposing those Dirichlet BCs
   neumanndict = {3:1, 4:-1} # This imposes normal fluxes on boundaries 3 and 4
   f0 = NeumannNormal( mesh, neumanndict ) # Build corresponding Rhs
   paramdict = {1:1,2:.1} # This gives the value of the conductivity parameter in each physical set 1 and 2
   K0 = assemK( mesh, ind, jnd, Kel, elset, paramdict ) # Actually assemble FE matrix
   K, f = minCstr( K0, f0, C, d ) # Take Dirichlet BCs into account
   u = spl.spsolve(K,f) # Solve linear algebra system
   plotMesh( mesh, u ) # Display solution (pressure)
   # End FE Computation example
   
   # Generate data
   P1 = 1
   P2 = 0
   P3 = 0
   P4 = 0
   dirichletdict = {1:P1, 2:P2, 3:P3, 4:P4}
   paramdict = {1:1,2:2}
   phi1, phi2, phi3, phi4, um, Pi = simulateMeasurement( dirichletdict, paramdict, mesh, noise=0 )
   plotMesh( mesh, um )

