import numpy as np
import numpy.matlib
def p2index(p, pv, d0 = None, sort = None):
    '''
    find points in p coinciding with pv
    p and pv are 2 dimensional arrays. each row is a point
    pv = 2 dimensional array. each row is a point
    '''

    ds = p2segment(p, pv)
    if d0 is not None:
        bc = ds <= d0
    else:
        bc = ds <= np.finfo(float).eps*1E6
    bcInd = np.where(bc)[0]
    if sort is not None:
        dis = np.sqrt((p[bcInd,0] -  pv[0,0])**2 + (p[bcInd,1] -  pv[0,1])**2)
        ind = sorted(range(len(dis)), key=lambda k: dis[k])
        bcs = bcInd[ind]
    else:
        bcs = bcInd
            
    return np.int32(bcs)
def inpolygon(p, pv):
    ds = p2segment(p, pv)
    onboun = np.where(ds == 0)[0]
    linex = p[:,0]
    liney = p[:,1]
    polyx = pv[:,0]
    polyy = pv[:,1]   
    """Simple method to detect points on the interior or exterior of a closed 
    polygon.  Returns a boolean for single points, or an array of booleans for a 
    line masking the segment(s) of the line within the polygon.
    For each point, operates via a ray-casting approach -- the function projects 
    a semi-infinite ray parallel to the positive horizontal axis, and counts how 
    many edges of the polygon this ray intersects.  For a simply-connected 
    polygon, this determines whether the point is inside (even number of crossings) 
    or outside (odd number of crossings) the polygon, by the Jordan Curve Theorem.
    """
    """Calculate whether given points are within a 2D simply-connected polygon.
    Returns a boolean 
    ARGS:
        polyx: array-like.
            Array of x-coordinates of the vertices of a polygon.
        polyy: array-like.
            Array of y-coordinates of the vertices of a polygon.  Must match 
            dimension of polyx.
        linex: array-like or float.
            x-coordinate(s) of test point(s).
        liney: array-like or float.
            y-coordiante(s) of test point(s).  Must match dimension of linex.
    RETURNS:
        mask: boolean or array of booleans.
            For each (linex,liney) point, True if point is in the polygon, 
            else False.
    """
    single_val = True
    try:
        iter(linex)
    except TypeError:
        linex = np.asarray([linex],dtype=float)
    else:
        linex = np.asarray(linex,dtype=float)
        single_val = False

    try:
        iter(liney)
    except TypeError:
        liney = np.asarray([liney],dtype=float)
    else:
        liney = np.asarray(liney,dtype=float)
        single_val = False

    if linex.shape != liney.shape:
        raise ValueError("linex, liney must be of same shape")
    
    # generator for points in polygon
    def lines():
        p0x = polyx[-1]
        p0y = polyy[-1]
        p0 = (p0x,p0y)
        for i,x in enumerate(polyx):
            y = polyy[i]
            p1 = (x,y)
            yield p0,p1
            p0 = p1

    mask = np.array([False for i in range(len(linex))])
    for i,x in enumerate(linex):
        y = liney[i]
        result = False

        for p0,p1 in lines():
            if ((p0[1] > y) != (p1[1] > y)) and (x < ((p1[0]-p0[0])*(y-p0[1])/(p1[1]-p0[1]) + p0[0])):
                result = not result 
        mask[i] = result

    # recast mask -- single Boolean if single_val inputs, else return array of booleans
    if single_val:
        mask = mask[0]
    mask[onboun] = True

    return mask
def ismember(A, B):
    return [ np.sum(a == B) for a in A ]
def projection(A,B,M):
    dis1 = np.sqrt(sum((M - A)**2))
    dis2 = np.sqrt(sum((M - B)**2))
    if dis1 < np.finfo(float).eps*1E3:
        N = A; flag = 1; dis = 0
    elif dis2 < np.finfo(float).eps*1E3:
        N = B; flag = 1; dis = 0
    else:
        AB = np.sqrt(sum((B - A)**2))
        tanvec = (B - A)/AB
        a1, b1 = -tanvec[1], tanvec[0]
        c1 = -a1*A[0] - b1*A[1]
        
        a2, b2 = tanvec[0], tanvec[1]
        c2 = -a2*M[0] - b2*M[1]
        if (a1 == 0 and b1 == 0) or (a2 == 0 and b2 == 0):
            print('something wrong in intersection. please check')
            xn, yn = A
        elif a1 == 0 and b2 == 0:
            xn, yn = -c2/a2, -c1/b1
        elif b1 == 0 and a2 == 0:
            xn, yn = -c1/a1, -c2/b2
        elif a1 == 0:
            xn, yn = (-c2 + b2*c1/b1)/a2, -c1/b1
        elif b1 == 0:
            xn, yn = -c1/a1, (-c2 + a2*c1/a1)/b2
        elif a2 == 0:
            xn, yn = (-c1 + b1*c2/b2)/a1, -c2/b2
        elif b2 == 0:
            xn, yn = -c2/a2, (-c1 + a1*c2/a2)/b1
        else:
            xn, yn = -(c1/b1 - c2/b2)/(a1/b1 - a2/b2), -(c1/a1 - c2/a2)/(b1/a1 - b2/a2)
        N = np.array(([xn, yn]))
        dis = np.sqrt(sum((M - N)**2))
        if dis < np.finfo(float).eps*1E3:
            if abs(np.sqrt(sum((A - N)**2)) + np.sqrt(sum((B - N)**2)) - AB) < np.finfo(float).eps*1E3:
                flag = 2 # N belong to AB
            else:
                flag = 0 # N dose not belong to AB
        else:
            dir1 = np.sign(N - A)
            dir2 = np.sign(N - B)
            if (dir1[0] == 0 and dir1[1] == 0) or (dir2[0] == 0 and dir2[1] == 0):
                flag = 1 # N == A or N == B
            elif dir1[0] == -dir2[0] and dir1[1] == -dir2[1]:
                flag = 2 # N belong to AB
            else:
                flag = 0
    return N, flag, dis
def area(X, Y):
    if len(X.shape) == 2:
        l1 = np.sqrt((X[:,1] - X[:,0])**2 + (Y[:,1] - Y[:,0])**2)
        l2 = np.sqrt((X[:,2] - X[:,0])**2 + (Y[:,2] - Y[:,0])**2)
        l3 = np.sqrt((X[:,1] - X[:,2])**2 + (Y[:,1] - Y[:,2])**2)
    if len(X.shape) == 1:
        l1 = np.sqrt((X[1] - X[0])**2 + (Y[1] - Y[0])**2)
        l2 = np.sqrt((X[2] - X[0])**2 + (Y[2] - Y[0])**2)
        l3 = np.sqrt((X[1] - X[2])**2 + (Y[1] - Y[2])**2)
    s = (l1+l2+l3)/2
    areatri = np.sqrt(s*(s-l1)*(s-l2)*(s-l3))     
    return areatri
def angle(p1,p0,p2):
    p20 = p2 - p0
    p10 = p1 - p0
    l20 = np.sqrt(sum(p20**2))
    l10 = np.sqrt(sum(p10**2))
   
    if l10*l20 == 0:
        ang = 0
    else:
        n1 = p20/l20
        n2 = p10/l10
        ang = np.arctan2(abs(n1[0]*n2[1] - n1[1]*n2[0]),n1[0]*n2[0] + n1[1]*n2[1])
    return ang
def p2segment(p, pv):
    # To find the distance of our point p  to the line segment between points A and B,
    # we need the closest point on the line segment. We can represent such a point q on the segment by:
    # q = A + t(B - A)
    # => t = (Ap.AB)/AB^2
    # if t > 1 => q = B
    # if t < 0 => q = A
    # else => q locates between A and B
    # distance = pq
    if len(p.shape) == 1:
        p = p.reshape(1,2)
    d = np.empty((p.shape[0], pv.shape[0]-1))
    ds = np.empty((p.shape[0], 1))
    for i in range(pv.shape[0]-1):
        A0 = pv[i,0] * np.ones(p.shape[0])
        A1 = pv[i,1] * np.ones(p.shape[0])
        B0 = pv[i+1,0] * np.ones(p.shape[0])
        B1 = pv[i+1,1] * np.ones(p.shape[0])
        q = np.empty((p.shape[0], 2))
        VecAB = pv[i+1,:] - pv[i,:]
        DotAB = VecAB[0]**2 + VecAB[1]**2
        if DotAB == 0:
            q[:,0] = A0
            q[:,1] = A1
        else:
            Ap = np.empty((p.shape[0], 2))
            Ap[:,0] = p[:,0] - A0
            Ap[:,1] = p[:,1] - A1
            t = (Ap[:,0]*VecAB[0] + Ap[:,1]*VecAB[1])/DotAB
            id1 = t < 0 
            id2 = t > 1 
            id3 = np.logical_and(t <= 1.0, t >= 0.0) 
            q[id1,0] = A0[id1]
            q[id1,1] = A1[id1]
            q[id2,0] = B0[id2]
            q[id2,1] = B1[id2]
            q[id3,0] = A0[id3] + t[id3] * VecAB[0]
            q[id3,1] = A1[id3] + t[id3] * VecAB[1]
        d[:,i] = np.sqrt((p[:,0] - q[:,0])**2 + (p[:,1]- q[:,1])**2)
    ds[:,0] = d.min(1)
    return ds

def fillgap(pv):
    """ Fill a region that has been deleted and only was replaced by rosette """
    def unique_rows(a):
        a = np.ascontiguousarray(a)
        unique_a = np.unique(a.view([('', a.dtype)]*a.shape[1]))
        return unique_a.view(a.dtype).reshape((unique_a.shape[0], a.shape[1]))

    from shapely.geometry import Polygon
    polygon = Polygon(pv)
    arepol = polygon.area
    areele = 0
    numnod = pv.shape[0] - 1
    edge1 = pv[:2,:]
    i = 0
    j = 1
    edgind = [0, 1]
    t = np.zeros((1,3),np.int32)
    while arepol > np.sum(areele):
        ang1 = angle(edge1[0,:],pv[i+2,:],edge1[1,:])
        ang2 = angle(edge1[0,:],pv[numnod-j,:],edge1[1,:])
        if ang1 > ang2:
            ti = np.array([edgind[0], edgind[1], i+2],np.int32)
            p13 = (pv[ti[0],:] + pv[ti[2],:])/2 ; p13 = p13.reshape(1,2)
            d13 = p2segment(p13, pv)
            p23 = (pv[ti[1],:] + pv[ti[2],:])/2 ; p23 = p23.reshape(1,2)
            d23 = p2segment(p23, pv)               
            if d13 > np.finfo(float).eps*1e5:
                edgind = [ti[0], ti[2]]
   
            if d23 > np.finfo(float).eps*1e5:
                edgind = [ti[1], ti[2]]
                
            i = i + 1
        else:
            ti = np.array([edgind[0], edgind[1], numnod-j])
            p13 = (pv[ti[0],:] + pv[ti[2],:])/2 ; p13 = p13.reshape(1,2)
            d13 = p2segment(p13, pv)
            p23 = (pv[ti[1],:] + pv[ti[2],:])/2 ; p23 = p23.reshape(1,2)
            d23 = p2segment(p23, pv)   
            if d13 > np.finfo(float).eps*1e5:
                edgind = [ti[0], ti[2]]
                
            if d23 > np.finfo(float).eps*1e5:
                edgind = [ti[1], ti[2]]
                
            j = j + 1
        t = np.concatenate((t,ti.reshape(1,3)),axis = 0)
        xcoord = np.zeros((t.shape[0]-1,3))
        xcoord[:,0] = pv[t[1:,0],0]; xcoord[:,1] = pv[t[1:,1],0]; xcoord[:,2] = pv[t[1:,2],0]
        ycoord = np.zeros((t.shape[0]-1,3))
        ycoord[:,0] = pv[t[1:,0],1]; ycoord[:,1] = pv[t[1:,1],1]; ycoord[:,2] = pv[t[1:,2],1]
        areele = area(xcoord,ycoord)
        edge1 = pv[edgind,:]
    t2 = np.delete(t,0,axis = 0)
    t2 = unique_rows(t2)
    p2 = pv[:-1,:]
    return p2,t2
def assemblymesh(p1, t1, p2, t2):
    """ assembly mesh p1-t1 to mesh p2-t2"""
    # find duplicate points p1 index - p2 index. format: p1 index - 1/0 - p2 index
    p = np.copy(p2)
    tnew = np.copy(t1)
    duppoi = np.zeros((p1.shape[0],3),np.int32)
    duppoi[:,0] = np.arange(p1.shape[0]); count = 0
    for i in range(p1.shape[0]):
        dis = np.sqrt( (p1[i,0] - p2[:,0])**2 + (p1[i,1] - p2[:,1])**2 )
        inddup = np.where(dis < np.finfo(float).eps*1E5)[0]
        if len(inddup) > 0:
            duppoi[i,1] = 1; duppoi[i,2] = inddup
        else:
            duppoi[i,2] = np.max(t2) + 1 + count
            p = np.append(p,p1[i,:].reshape(1,2),axis = 0)
            count = count + 1
    
    duppoi[duppoi[:,2].argsort()[::-1],:]
    for i in range(duppoi.shape[0]):
        ii, jj = np.where(t1 == duppoi[i,0])
        tnew[ii,jj] = duppoi[i,2]
        
    t = np.concatenate((t2,tnew), axis = 0)
    return p, t, tnew
def removeduplicatenode(p, t, gap = None):
    """ Check and remove duplicate nodes"""
    if gap is None:
        gap = 0
    index = np.zeros((1,2),np.int32)
    for k in range(p.shape[0],1,-1):
        pk = p[k-1,:]
        dis = np.sqrt( (p[:k-1,0] - pk[0])**2 + (p[:k-1,1] - pk[1])**2)
        local = np.where(dis < gap + np.finfo(float).eps*1e7)[0]
        if len(local) != 0:
            index = np.append(index, np.array(([k-1, local[0]])).reshape(1,2), axis = 0)
            
    index = np.delete(index, 0, axis = 0)
    if len(index) > 0:
        p0 = (p[index[:,0],:] + p[index[:,1],:])/2
        p[index[:,1],:] = p0
        p = np.delete(p,index[:,0],axis = 0)
        for ni in range(index.shape[0]):
            id1,id2 = np.where(t == index[ni,0])
            for mi in range(len(id1)):
                t[id1[mi],id2[mi]] = index[ni,1]
                
    tca = np.unique(t)
    tcb = np.unique(t)
    while max(tca) > len(tca)-1:
        t1 = tca[1::]
        t2 = tca[:-1]
        t0 = t1 - t2
        t0 = np.insert(t0,0,0)
        index = np.where(t0>1)[0]
        tca[index] = tca[index] - 1
        
    for ni in range(len(tca)):
        id1,id2 = np.where(t == tcb[ni])
        for mi in range(len(id1)):
            t[id1[mi],id2[mi]] = tca[ni]  
            
    return p, t
def adjustmesh(g, tips, dc = None):
    if dc is None:
        dc = 1E-2
    p = g.nodes
    t = g.cell_nodes().indices.reshape((3, g.num_cells), order='f').T
    p = p[[0,1],:].T
    # nodaro = p[g.get_boundary_nodes(),:]
    cbl = np.intersect1d(np.where(p[:,0] == min(p[:,0]))[0], np.where(p[:,1] == min(p[:,1]))[0])[0]
    cbr = np.intersect1d(np.where(p[:,0] == max(p[:,0]))[0], np.where(p[:,1] == min(p[:,1]))[0])[0]
    ctl = np.intersect1d(np.where(p[:,0] == min(p[:,0]))[0], np.where(p[:,1] == max(p[:,1]))[0])[0]
    ctr = np.intersect1d(np.where(p[:,0] == max(p[:,0]))[0], np.where(p[:,1] == max(p[:,1]))[0])[0]
    nodaro = p[[cbl, cbr, ctr, ctl, cbl],:]
    
    px = numpy.matlib.repmat(p[:,0].reshape(p.shape[0],1),1,p.shape[0])
    py = numpy.matlib.repmat(p[:,1].reshape(p.shape[0],1),1,p.shape[0])
    ds = np.sqrt( (px - px.T)**2 + (py - py.T)**2 )
    idi, idj = np.where(ds < np.finfo(float).eps*1E5)
    index = np.where(idi != idj)[0]
    fraind = np.zeros(shape = (len(index),2))
    fraind[:,0] = idi[index]
    fraind[:,1] = idj[index]
    fraind = np.int32(np.unique(np.sort(fraind, axis = 1), axis = 0))
    tips_nod = []
    if tips is not None:
        for i in range(tips.shape[0]):
            tip = tips[i,:]
            id1 = np.where(np.isclose(p[:,0],tip[0]))[0]
            id2 = np.where(np.isclose(p[:,1],tip[1]))[0]
            tipind = np.intersect1d(id2,id1)[0]
            tips_nod.append(tipind)
            
        face_ind = np.reshape(g.face_nodes.indices, (g.dim, -1), order='F').T
        face_nor = g.face_normals.T; face_nor = face_nor[:,[0,1]]
        frac_fac = np.where(g.tags['fracture_faces'])[0]  
        node_adj_old = []
        for i in range(len(frac_fac)):
            index = face_ind[frac_fac[i],:]
            ele = np.intersect1d(np.where(t == index[0])[0], np.where(t == index[1])[0])
            index0 = np.setdiff1d(t[ele,:], index)[0]
            A, B = p[index,:]
            M = p[index0,:]
            N,_,_= projection(A,B,M)
            normi = (N - M); normi = normi/np.sqrt(sum(normi**2))
            node_adj = np.setdiff1d(np.setdiff1d(index,tips_nod),node_adj_old)
            p[node_adj,:] = p[node_adj,:] - normi*dc/2
            node_adj_old = np.concatenate((node_adj_old,node_adj))
            
    return p, t
def before_processing_fracture(p, t, tips, fracture, gap):
    # nodaro = p[g.get_boundary_nodes(),:]
    cbl = np.intersect1d(np.where(p[:,0] == min(p[:,0]))[0], np.where(p[:,1] == min(p[:,1]))[0])[0]
    cbr = np.intersect1d(np.where(p[:,0] == max(p[:,0]))[0], np.where(p[:,1] == min(p[:,1]))[0])[0]
    ctl = np.intersect1d(np.where(p[:,0] == min(p[:,0]))[0], np.where(p[:,1] == max(p[:,1]))[0])[0]
    ctr = np.intersect1d(np.where(p[:,0] == max(p[:,0]))[0], np.where(p[:,1] == max(p[:,1]))[0])[0]
    nodaro = p[[cbl, cbr, ctr, ctl, cbl],:]
    px = numpy.matlib.repmat(p[:,0].reshape(p.shape[0],1),1,p.shape[0])
    py = numpy.matlib.repmat(p[:,1].reshape(p.shape[0],1),1,p.shape[0])
    ds = np.sqrt( (px - px.T)**2 + (py - py.T)**2 )
    idi, idj = np.where(ds < gap + np.finfo(float).eps*1E5)
    index = np.where(idi != idj)[0]
    fraind = np.zeros(shape = (len(index),2))
    fraind[:,0] = idi[index]
    fraind[:,1] = idj[index]
    fraind = np.int32(np.unique(np.sort(fraind, axis = 1), axis = 0))
    tips_nod = []; tipcra = []; roscra = []; moucra = []
    if tips is not None:
        for i in range(tips.shape[0]):
            tip = tips[i,:]
            id1 = np.where(np.isclose(p[:,0],tip[0]))[0]
            id2 = np.where(np.isclose(p[:,1],tip[1]))[0]
            tipind = np.intersect1d(id2,id1)[0]
            tips_nod.append(tipind) 
            
        nodcra = []
        for i in range(tips.shape[0]):
            tip = tips[i,:]
            id1 = np.where(np.isclose(p[:,0],tip[0]))[0]
            id2 = np.where(np.isclose(p[:,1],tip[1]))[0]
            tipind = np.intersect1d(id2,id1)[0]
            elearotip = np.where(t == tipind)[0]
            indarotip = t[elearotip,:]
            indarotip = np.setdiff1d(np.unique(indarotip),tipind)
            id0 = np.intersect1d(indarotip,fraind)
            P1 = p[tipind,:]
            P2 = ( p[id0[0],:] + p[id0[1],:] )/2
            P31 = p[id0[0],:]
            d01 = (P2[0] - P1[0])*(P31[1] - P1[1]) - (P2[1] - P1[1])*(P31[0] - P1[0]) 
            if d01 > 0:
                P1Ind = id0[0]
                P2Ind = id0[1]
            else:
                P1Ind = id0[1]
                P2Ind = id0[0]
                
            A1Ind = np.intersect1d(np.setdiff1d(np.unique(fraind[np.where(fraind == P1Ind)[0],:]),np.array([tipind,P1Ind])),fraind)[0]
            A2Ind = np.intersect1d(np.setdiff1d(np.unique(fraind[np.where(fraind == P2Ind)[0],:]),np.array([tipind,P2Ind])),fraind)[0]
            nodcra.append(p[[A1Ind, P1Ind, tipind, P2Ind, A2Ind],:])
        
        tipcra.append(tips[0,:]); tipcra.append(tips[1,:]) 
        roscra.append([]); roscra.append([])
        moucra.append([]); moucra.append([])
    return p, t, nodaro, tipcra, moucra, roscra, nodcra
def fracture_node(p, fracture, gap):
    indfra = []
    for i in range(len(fracture)):
        ds = p2segment(p, fracture[i])
        ind = np.where(ds < gap + np.finfo(float).eps*1e5)[0]
        indfra = np.append(indfra, ind)
    return np.int32(indfra)
def fracture_infor(fracture):
    def tip_edge_fracture(fracture):
        cou = 0
        edges = np.array([0, 0]).reshape(1,2)
        tips = np.array([0, 0]).reshape(1,2)
        tips_fraci = np.vstack((fracture[0,:], fracture[-1,:]))
        tips = np.concatenate((tips, tips_fraci), axis = 0)
        for j in range(fracture.shape[0] - 1):
            indedg = np.array([[cou, cou+1]])
            edges = np.concatenate((edges, indedg), axis = 0)
            cou = cou + 1
        tips = np.delete(tips, 0, 0)
        edges = np.delete(edges, 0, 0)  
        return tips, edges
    
    cou = 0; frac_pts = np.array([0, 0]).reshape(1,2); tips = np.array([0, 0]).reshape(1,2); frac_edges = np.array([0, 0]).reshape(1,2)
    for i in range(len(fracture)):
        frac_pts = np.concatenate((frac_pts,fracture[i]), axis = 0)
        tipsi, edgei = tip_edge_fracture(fracture[i])
        tips = np.concatenate((tips, tipsi), axis = 0)
        frac_edges = np.concatenate((frac_edges,edgei + cou), axis = 0)
        cou = np.max(edgei)+1
        
    tips = np.delete(tips, 0, 0)
    frac_edges = np.delete(frac_edges, 0, 0)     
    frac_pts = np.delete(frac_pts, 0, 0)      
    return tips, frac_pts, frac_edges
''' -----------------------------QPE from here------------------------------'''
def remesh_at_tip(gb, fracture, newfrac):
    gap = 1E-2
    '''based on 2d grid with fractures from PorePy (gb)
       1. remesh at tip that propagates by rosettle elements
       2. defined split face
       3. update 2 dimensional grid in PorePy
       4. return a dictionary that specify which 1d grid and which face need to be slipted
       
   Example:
       fracture1 = np.array([[0.4, 0.6], [0.5, 0.65], [0.6, 0.6]])
       fracture2 = np.array([[0.45, 0.2], [0.55, 0.2]])
       fracture = np.array([fracture1, fracture2])
       
       newfrac = np.array([[0.6, 0.6], [0.63, 0.65]])

       #newfrac = np.array([[0.4, 0.6], [0.37, 0.65]])

       mesh_size = 0.07
       mesh_args = { "mesh_size_frac": mesh_size, "mesh_size_min": 1 * mesh_size, "mesh_size_bound": 5 * mesh_size } 
       box = {"xmin": 0, "ymin": 0, "xmax": 1, "ymax": 1}  
       
       tips, frac_pts, frac_edges = meshing.fracture_infor(fracture)
       network = pp.FractureNetwork2d(frac_pts.T, frac_edges.T, domain=box)
       gb = network.mesh(mesh_args)       
       pp.contact_conditions.set_projections(gb)
        
       dic_split = meshing.remesh_at_tip(gb, fracture, newfrac)
       pp.propagate_fracture.propagate_fractures(gb, dic_split)
       
       '''
    # fractures informations
    g_2d = gb.grids_of_dimension(2)[0]
    tips, frac_pts, frac_edges = fracture_infor(fracture)
    
    ''' Refinement and remesh by QPE. return: nodes coordinates, cell indices, faces- nodes, cells - faces '''
    p, t, fn, cf = do_remesh(g_2d, fracture, newfrac, gap)
    
    ''' after remesh, defined informations that need to be updated on the porepy gridbucket '''
    # define contact faces
    confacglo = []
    
    faccen = (p[fn[:,0],:] + p[fn[:,1],:])/2
    xx = np.tile(faccen[:,0].reshape(faccen.shape[0],1), [1,faccen.shape[0]])
    yy = np.tile(faccen[:,1].reshape(faccen.shape[0],1), [1,faccen.shape[0]])
    dis = np.sqrt( (xx - xx.T)**2 + (yy - yy.T)**2 )
    np.fill_diagonal(dis, 100)
    indi, indj = np.where(dis < gap + np.finfo(float).eps*1E5)
    confac = np.vstack((indi, indj)).T
    confac = np.unique( np.sort(confac, axis = 1), axis = 0)
    delconfac = []
    for i in range(confac.shape[0]):
        fac0, fac1 = confac[i,:]
        if np.any(np.sum(np.concatenate((cf == fac0, cf == fac1), axis = 1), axis=1) == 2):
           delconfac.append(i)
    confac = np.delete(confac,delconfac, axis = 0)    
    
    count = 0
    for i in range(len(fracture)):
        frai = fracture[i]
        if frai.shape[0] > 2:
            for j in range(frai.shape[0] - 1):
                faconfac = np.where(p2segment(faccen[confac[:,0],:],frai[[j, j+1],:]) < gap + np.finfo(float).eps*1E5)[0]
                confacglo.append(confac[faconfac,:])
                ds = p2segment(newfrac[0,:],frai[[j, j+1],:])
                if ds < np.finfo(float).eps*1E5:
                    split_1d = count
                count = count + 1     
        else:
            faconfac = np.where(p2segment(faccen[confac[:,0],:],frai) < gap + np.finfo(float).eps*1E5)[0]
            confacglo.append(confac[faconfac,:])
            ds = p2segment(newfrac[0,:],frai)
            if ds < np.finfo(float).eps*1E5:
                split_1d = count
            count = count + 1  
    
    # define contact nodes
    xx = np.tile(p[:,0].reshape(p.shape[0],1), [1,p.shape[0]])
    yy = np.tile(p[:,1].reshape(p.shape[0],1), [1,p.shape[0]])
    dis = np.sqrt( (xx - xx.T)**2 + (yy - yy.T)**2 )
    np.fill_diagonal(dis, 100)
    indi, indj = np.where(dis < gap + np.finfo(float).eps*1E5)
    connod = np.vstack((indi, indj)).T
    connod = np.unique( np.sort(connod, axis = 1), axis = 0)
    
    # define data faces - nodes
    datfn = np.zeros(fn.shape[0]*2) == 0
    
    # define data cells - faces
    datcf = np.copy(cf)*0
    check = [np.max(cf) + 10]
    for e in range(cf.shape[0]):
        for i in range(cf.shape[1]):
            idi = cf[e,i]
            if any(idi == check):
                datcf[e,i] = -1
            else:
                datcf[e,i] = 1
            check.append(idi)
    
    for i in range(confac.shape[0]):
        ii, jj = np.where(cf == confac[i,1])
        datcf[ii,jj] = -1
    
    # define faces on fracture
    facfra = np.zeros(fn.shape[0]) == 1; facfra[confac] = True   
    
    # find faces connect to tips   
    factipind = []
    for i in range(tips.shape[0]):
        tipi = tips[i,:]
        indtip = np.where(np.sqrt((p[:,0] - tipi[0])**2 + (p[:,1] - tipi[1])**2) < np.finfo(float).eps*1E5)[0]
        factipind = np.append(factipind, np.where(fn ==  indtip)[0])
    factipind = np.int32(factipind)
    factip = np.zeros(fn.shape[0]) == 1; #factip[factipind] = True  
    
    # find faces on boundary, for rectangular domain only
    cbl = np.intersect1d(np.where(p[:,0] == min(p[:,0]))[0], np.where(p[:,1] == min(p[:,1]))[0])[0]
    cbr = np.intersect1d(np.where(p[:,0] == max(p[:,0]))[0], np.where(p[:,1] == min(p[:,1]))[0])[0]
    ctl = np.intersect1d(np.where(p[:,0] == min(p[:,0]))[0], np.where(p[:,1] == max(p[:,1]))[0])[0]
    ctr = np.intersect1d(np.where(p[:,0] == max(p[:,0]))[0], np.where(p[:,1] == max(p[:,1]))[0])[0]
    nodaro = p[[cbl, cbr, ctr, ctl, cbl],:]
    facbouind = p2index( faccen, nodaro)
    facbou = np.zeros(fn.shape[0]) == 1; facbou[facbouind] = True
    
    # find nodes on fracture
    nodfraind = []
    for i in range(len(fracture)):
        fraci = fracture[i]
        nodfraind = np.append(nodfraind, p2index( p, fraci, d0 = gap))
    nodfraind = np.int32(nodfraind)
    nodfra = np.zeros(p.shape[0]) == 1; nodfra[nodfraind] = True
    
    # Find nodes tips
    nodtipind = []
    for i in range(tips.shape[0]):
        tipi = tips[i,:]
        indtip = np.where(np.sqrt((p[:,0] - tipi[0])**2 + (p[:,1] - tipi[1])**2) < np.finfo(float).eps*1E5)[0]
        nodtipind = np.append(nodtipind, indtip)
    nodtipind = np.int32(nodtipind)
    nodtip = np.zeros(p.shape[0]) == 1; #nodtip[nodtipind] = True  
    
    # find nodes on boundary
    nodbouind = p2index( p, nodaro)
    nodbou = np.zeros(p.shape[0]) == 1; nodbou[nodbouind] = True  
    
    dis = np.sqrt( (p[:,0] - newfrac[0,0])**2 + (p[:,1] - newfrac[0,1])**2 )
    ind0 = np.argmin(dis)
    dis = np.sqrt( (p[:,0] - newfrac[1,0])**2 + (p[:,1] - newfrac[1,1])**2 )
    ind1 = np.argmin(dis)
    p[ind1,:] = newfrac[1,:]
    split_face = np.intersect1d(np.where(fn[:,0] == min(ind0, ind1)), np.where(fn[:,1] == max(ind0, ind1)))[0]
    
    # close the crack
    px = numpy.matlib.repmat(p[:,0].reshape(p.shape[0],1),1,p.shape[0])
    py = numpy.matlib.repmat(p[:,1].reshape(p.shape[0],1),1,p.shape[0])
    ds = np.sqrt( (px - px.T)**2 + (py - py.T)**2 )
    idi, idj = np.where(ds < gap + np.finfo(float).eps*1E5)
    index = np.where(idi != idj)[0]
    fraind = np.zeros(shape = (len(index),2))
    fraind[:,0] = idi[index]
    fraind[:,1] = idj[index]
    fraind = np.int32(np.unique(np.sort(fraind, axis = 1), axis = 0))
    p0 = ( p[fraind[:,0],:] + p[fraind[:,1],:])/2
    p[fraind[:,0],:] = p0; p[fraind[:,1],:] = p0  

    ''' now update Porepy gridbucket ''' 
    g_2d.num_cells = t.shape[0]
    g_2d.num_faces = fn.shape[0]
    g_2d.num_nodes = p.shape[0]    
    g_2d.global_point_ind = np.arange(p.shape[0], dtype = np.int32)
    
    g_2d.cell_faces.indices = cf.reshape(t.shape[0]*3)
    g_2d.cell_faces.indptr = np.arange(0,(cf.shape[0] + 1)*3,3, dtype = np.int32)
    g_2d.cell_faces.data = datcf.reshape(t.shape[0]*3)
    g_2d.cell_faces._shape = (fn.shape[0],t.shape[0])
    
    g_2d.face_nodes.indices = fn.reshape(fn.shape[0]*2)
    g_2d.face_nodes.indptr = np.arange(0,(len(fn)+1)*2,2, dtype = np.int32)
    g_2d.face_nodes.data = datfn
    g_2d.face_nodes._shape = (p.shape[0],fn.shape[0])
    
    g_2d.nodes = np.concatenate((p,0*p[:,0].reshape(p.shape[0],1)), axis = 1).T
    
    g_2d.tags['fracture_0_faces'] = facfra
    g_2d.tags['fracture_1_faces'] = facfra
    g_2d.tags['fracture_2_faces'] = facfra
    g_2d.tags['fracture_faces'] = facfra
    g_2d.tags['tip_faces'] = factip
    g_2d.tags['domain_boundary_1_faces'] = facbou
    g_2d.tags['domain_boundary_2_faces'] = facbou
    g_2d.tags['domain_boundary_3_faces'] = facbou
    g_2d.tags['domain_boundary_4_faces'] = facbou
    g_2d.tags['domain_boundary_5_faces'] = facbou
    g_2d.tags['domain_boundary_6_faces'] = facbou
    g_2d.tags['domain_boundary_faces'] = facbou
    
    g_2d.tags['fracture_nodes'] = nodfra
    g_2d.tags['tip_nodes'] = nodtip
    g_2d.tags['domain_boundary_nodes'] = nodbou
    
    
    import scipy.sparse as sps
    count = 0
    for e, d_e in gb.edges_of_node(g_2d):
        confac = confacglo[count]
        face_cells_new = np.full((confac.shape[0], g_2d.num_faces), False)
        for i  in range(confac.shape[0]):
            face_cells_new[i, confac[i,:]] = np.array([True, True])
        face_cells_new = sps.csr_matrix(face_cells_new)
        # face_cells = d_e["face_cells"]
        row, col, sgn = sps.find(face_cells_new)
        face_cells_new = sps.csc_matrix((sgn, (row, col)), shape=(confac.shape[0], g_2d.num_faces))
        d_e["face_cells"] = face_cells_new
        
        count = count + 1
    
    g_2d.compute_geometry()
    g_1d = gb.grids_of_dimension(1)
    dic_split = {}
    for i in range(len(g_1d)):
        if i == split_1d:
            d = { g_1d[i]: split_face }
        else:
            d = { g_1d[i]: np.array([], dtype=np.int) }
        dic_split.update(d)  
    return dic_split
def do_remesh(g_2d, fracture, newfrac, gap):
    ''' 1. Refinement at new fracture
        2. replace elements around new fracture by rosette elements, one face matchs with new fracture
        3. define new faces-nodes, cells - faces '''
    if gap is None:
        gap = 5E-2
    tips, frac_pts, frac_edges = fracture_infor(fracture)
    # open the crack to avoid confusion between fracture's faces
    p, t = adjustmesh(g_2d, tips, gap) 
    
    A0 = np.min(g_2d.cell_volumes); lmin = np.min(g_2d.face_areas)
    p, t = refinement( p, t, fracture, newfrac, A0, lmin, gap)
    tip = newfrac[0,:]; tipnew = newfrac[1,:]
    indfra = fracture_node(p, fracture, gap)
    # define tip mouth index: tip index, p1 bellow index, p2 upper index
    indtip = np.where(np.sqrt((p[:,0] - tip[0])**2 + (p[:,1] - tip[1])**2) < np.finfo(float).eps*1E5)[0]
    eleros = np.where(t == indtip)[0]
    indros = np.setdiff1d(np.unique(t[eleros,:]), indtip)
    indmou = np.intersect1d(indros, indfra)
    cel1 = np.intersect1d(np.where(t == indtip)[0], np.where(t == indmou[0])[0])[0]
    cel2 = np.intersect1d(np.where(t == indtip)[0], np.where(t == indmou[1])[0])[0]
    C1 = p[np.setdiff1d(t[cel1,:],[indtip, indmou[0]])[0],:]
    C2 = p[np.setdiff1d(t[cel2,:],[indtip, indmou[1]])[0],:]
    CO = tip - (C1 + C2)/2; CC = C2 - (C1 + C2)/2
    d01 = CO[0]*CC[1] - CO[1]*CC[0]
    if d01 < 0:
        flag = cel1
        cel1 = cel2
        cel2 = flag
        indP1 = indmou[1]
        indP2 = indmou[0]
    else:
        indP1 = indmou[0]
        indP2 = indmou[1]
    
    P1 = p[indP1,:]
    P2 = p[indP2,:]
    #       ------------------>
    #      / thetha
    #     /
    #    /
    #   /
    # p2-p1
    P11 = np.array([1,0])
    P00 = np.array([0,0])
    P22 = (P1 + P2)/2 - tip
    thetha = angle(P11,P00,P22) # inclination of the crack
    # define direction of the crack
    x1, y1 = 1, 0
    x2, y2 = 0, 0
    x3, y3 = P1 - tip
    d0 = (x2 - x1)*(y3 - y1) - (y2 - y1)*(x3 - x1)
    if d0 == 0:
        rota = -1
    else:
        rota = -np.sign(d0)
    r = np.sqrt( np.sum( (tipnew - tip)**2 ) )
    # remesh around tip by n element
    n = 6
    angle0 = angle(P1,tip,P2)
    alpha = [i*(2*np.pi - angle0)/n + angle0/2 for i in range(n+1)] 
    xin = r*np.cos(alpha + rota*thetha) + tip[0]
    yin = r*np.sin(alpha + rota*thetha) + tip[1]
    coord1 = np.concatenate((xin.reshape(len(xin),1),yin.reshape(len(xin),1)), axis=1)
    prose = np.concatenate((tip.reshape(1,2),coord1), axis=0)
    prose[1,:] = P1; prose[-1,:] = P2
    id1 = np.arange(0,n) + 1
    id2 = np.arange(1,n+1) + 1
    id0 = np.concatenate(( id1.reshape(len(id1),1), id2.reshape(len(id2),1) ), axis=1)
    trose = np.ones((id0.shape[0],3),np.int32)*0
    trose[:,1] = id0[:,0]
    trose[:,2] = id0[:,1]
    indoutrose = np.arange(n+1,0,-1)  # index of rose nodes   
    # defined a region around elements's tip, defined by pv
    n = 12
    r2 = np.sqrt( np.sum( (P1 - tip)**2 ) )
    alpha = [i*(2*np.pi - angle0)/n + angle0/2 for i in range(n+1)] 
    alpha = np.delete(alpha,[1,n-1])
    r0 = alpha*0 + r*1.6; r_control = r2*1.4; r0[0] = r_control; r0[-1] = r_control # This based on experiments
    xin = r0*np.cos(alpha + rota*thetha) + tip[0]
    yin = r0*np.sin(alpha + rota*thetha) + tip[1]
    pv = np.concatenate((xin.reshape(len(xin),1), yin.reshape(len(xin),1)), axis=1)
    isinside = inpolygon(p, pv)
    nodclo = np.where(isinside)[0]
    nodclo = np.setdiff1d(nodclo,[indP1, indP2])
    tt = np.copy(t)
    nodclo = np.union1d(nodclo,indtip)
    eleclo = np.where(np.array([ismember(t[:,0],nodclo), 
                                ismember(t[:,1],nodclo), 
                                ismember(t[:,2],nodclo)]) == 1)[1]
    eleclo = np.unique(eleclo)
    nodaro = t[eleclo,:]
    nodaro = np.unique(nodaro)
    test = np.array([ismember(t[:,0],nodaro), 
                     ismember(t[:,1],nodaro), 
                     ismember(t[:,2],nodaro)])
    eledel = np.where(np.sum(test,axis = 0) == 3)[0]
    tt = np.delete(tt, eledel, 0); tt = np.unique(tt)
    nodoutdel = np.intersect1d(nodaro,tt)
    noddel = np.unique(np.setdiff1d(nodaro,nodoutdel))
    bar = np.concatenate((t[:,[0,1]], t[:,[0,2]], t[:,[1,2]]), axis = 0)
    bar = np.unique(bar,axis = 0)
    indoutdel = indP1
    nodoutdel = np.setdiff1d(nodoutdel,np.array([indP1,indP2]))
    while len(nodoutdel) > 0:
        ii, jj = np.where(bar == indP1)
        nodex = bar[ii,:]; nodex = np.setdiff1d(np.unique(nodex), indP1)
        indP1 = np.intersect1d(nodoutdel,nodex)
        if len(indP1) >= 2:
            id0 = np.intersect1d(indP1, indfra)[0]
            iii, jjj = np.where(bar == id0)
            nod2 = bar[iii,:]; nod2 = np.setdiff1d(np.unique(nod2), id0)
            indP1 = np.intersect1d(nodoutdel,nod2)
            nodoutdel = np.setdiff1d(nodoutdel,np.array([indP1,id0]))
            indoutdel = np.append(indoutdel,id0)
            indoutdel = np.append(indoutdel,indP1)
        else:   
            indoutdel = np.append(indoutdel,indP1)
            nodoutdel = np.setdiff1d(nodoutdel,indP1)
    indoutdel = np.append(indoutdel,indP2)
    facout = np.concatenate(( indoutdel[0:-1].reshape(len(indoutdel)-1,1), 
                              indoutdel[1::].reshape(len(indoutdel)-1,1) ), axis = 1)
    facout.sort(axis = 1)
    pv1 = prose[indoutrose[-1],:]; pv1 = pv1.reshape(1,len(pv1))
    pv2 = p[indoutdel,:]
    pv3 = prose[indoutrose,:]
    pv = np.concatenate((pv1,pv2,pv3), axis = 0)
    inddel = np.where(np.sqrt(np.sum((pv[1:] - pv[:-1])**2, axis = 1)) < np.finfo(float).eps*1E5)[0]
    pv = np.delete(pv,inddel,axis = 0) 
    # generate a grid bewtween elements's tip and pv   
    ptran, ttran = fillgap(pv) 
    # Then connect to elements's tip
    p12, t12, t12new = assemblymesh(prose, trose, ptran, ttran)
    # delete faces, cells inside of remesh region
    p = np.delete(p, noddel, 0)
    t = np.delete(t, eledel, 0)
    p0 = np.copy(p)
    t0 = np.copy(t)
    for k in range(len(noddel),0,-1):
        t0[t0 > noddel[k-1]] = t0[t0 > noddel[k-1]] - 1 
    
    # finally, connect all grid together
    p, t, tnew = assemblymesh(p12,t12,p0,t0)
    
    # define faces - nodes
    fn = np.concatenate( (t[:,[0,1]], t[:,[0,2]], t[:,[1,2]] ), axis = 0)
    fn.sort(axis = 1)
    fn = np.unique(fn, axis = 0)
    
    # define cells-faces
    cf = np.zeros((t.shape[0],3), dtype = np.int32)
    for e in range(cf.shape[0]):
        fac1 = np.sort(t[e,[0,1]]); fac2 = np.sort(t[e,[0,2]]); fac3 = np.sort(t[e,[1,2]])
        cf[e,0] = np.intersect1d(np.where(fn[:,0] == fac1[0]), np.where(fn[:,1] == fac1[1]))[0]
        cf[e,1] = np.intersect1d(np.where(fn[:,0] == fac2[0]), np.where(fn[:,1] == fac2[1]))[0]
        cf[e,2] = np.intersect1d(np.where(fn[:,0] == fac3[0]), np.where(fn[:,1] == fac3[1]))[0]

    return p, t, fn, cf
def refinement( p, t, fracture, tips, A0, lmin, gap):
    """ Mesh refinement around crack tips"""
    cbl = np.intersect1d(np.where(p[:,0] == min(p[:,0]))[0], np.where(p[:,1] == min(p[:,1]))[0])[0]
    cbr = np.intersect1d(np.where(p[:,0] == max(p[:,0]))[0], np.where(p[:,1] == min(p[:,1]))[0])[0]
    ctl = np.intersect1d(np.where(p[:,0] == min(p[:,0]))[0], np.where(p[:,1] == max(p[:,1]))[0])[0]
    ctr = np.intersect1d(np.where(p[:,0] == max(p[:,0]))[0], np.where(p[:,1] == max(p[:,1]))[0])[0]
    nodaro = p[[cbl, cbr, ctr, ctl, cbl],:]
    xc = (p[t[:,0],:] + p[t[:,1],:] + p[t[:,2],:])/3
    eleref1 = [] # find elements at tips
    eleref2 = [] # find elements around rossete
    for i in range(tips.shape[0]):
        tip = tips[i]
        tipind = np.where(np.sqrt((p[:,0] - tip[0])**2 + (p[:,1] - tip[1])**2) < np.finfo(float).eps*1E5)[0]
        eleclo = np.where(t == tipind)[0]
        eleref1 = np.concatenate((eleref1,eleclo))
        
        dt = np.sqrt((xc[:,0] - tip[0])**2 + (xc[:,1] - tip[1])**2)
        eleclo = np.where(dt < lmin*4)[0]
        eleref2 = np.concatenate((eleref2,eleclo))
        
    if len(eleref1) > 0:
        eleref1 = eleref1.astype(int)
        xcoord = np.zeros((len(eleref1),3))
        xcoord[:,0] = p[t[eleref1,0],0]
        xcoord[:,1] = p[t[eleref1,1],0]
        xcoord[:,2] = p[t[eleref1,2],0]
        ycoord = np.zeros((len(eleref1),3))
        ycoord[:,0] = p[t[eleref1,0],1]
        ycoord[:,1] = p[t[eleref1,1],1]
        ycoord[:,2] = p[t[eleref1,2],1]
        areele1 = area(xcoord,ycoord)
        eleref1 = eleref1[np.where(areele1 > 4*A0)[0]]

    if len(eleref2) > 0:
        eleref2 = eleref2.astype(int)    
        xcoord = np.zeros((len(eleref2),3))
        xcoord[:,0] = p[t[eleref2,0],0]
        xcoord[:,1] = p[t[eleref2,1],0]
        xcoord[:,2] = p[t[eleref2,2],0]
        ycoord = np.zeros((len(eleref2),3))
        ycoord[:,0] = p[t[eleref2,0],1]
        ycoord[:,1] = p[t[eleref2,1],1]
        ycoord[:,2] = p[t[eleref2,2],1]
        areele2 = area(xcoord,ycoord)
        eleref2 = eleref2[np.where(areele2 > 6*A0)[0]]   
        
    eleref = np.int32(np.concatenate((eleref1,eleref2)))
    eleref = np.unique(eleref)
    if len(eleref) > 0:
        p, t = divideelement(p, t, eleref)
        nodfix = p2index(p,nodaro)
        for i in range(len(fracture)):
            craindi = p2index(p,fracture[i],gap)
            nodfix = np.concatenate((nodfix,craindi))
        p, t = smoothing(p, t, nodfix)
    return p, t
def divideelement(p, t, eleref):
    """ Divide elements that need to be refined by four sub-elements"""
    numnod = p.shape[0]
    tnew = np.zeros((1,3),np.int32)
    pnew = np.zeros((1,2))
    for j in range(len(eleref)):
        elei = eleref[j]
        index = t[elei,:]
        p1 = (p[index[0],:] + p[index[1],:])/2
        p2 = (p[index[0],:] + p[index[2],:])/2
        p3 = (p[index[1],:] + p[index[2],:])/2
        pi = np.array(([[p1[0],p1[1]],
                        [p2[0],p2[1]],
                        [p3[0],p3[1]]]))
        newele = np.array(([[index[0],numnod+j*3,numnod+j*3+1],
                            [index[1],numnod+j*3,numnod+j*3+2],
                            [index[2],numnod+j*3+1,numnod+j*3+2],
                            [numnod+j*3,numnod+j*3+1,numnod+j*3+2]]))
        tnew = np.append(tnew, newele, axis=0)
        pnew = np.append(pnew, pi, axis=0)
    tnew = np.delete(tnew, 0, axis = 0)
    pnew = np.delete(pnew, 0, axis = 0)
    t = np.delete(t,eleref,axis = 0)
    t = np.append(t, tnew, axis=0)
    p = np.append(p, pnew, axis=0)
    p, t = removeduplicatenode(p, t)
    poi, local = nodeedge(p, t)
    layer = 0
    while len(local) != 0:
        layer = 1
        p, t = removehangingnode(p, t, poi, local,layer)  
        p, t = removeduplicatenode(p, t) 
        poi, local = nodeedge(p, t)
    return p, t
def removehangingnode(p, t, poi, local, layer):
    """ Remove hanging nodes on the mesh"""
    numnod = p.shape[0]
    tnew = np.zeros((1,3),np.int32)
    pnew = np.zeros((1,2))
    eledel = np.zeros((1,1),np.int32)
    if layer <= 2:
        cou = 0
        for i in range(len(local)):
            pi = poi[i,:]
            x,y = pi
            for e in range(t.shape[0]):
                pv = p[t[e,:],:]
                pv = np.append(pv,pv[:1,:], axis = 0)
                ds = p2segment(pi.reshape(1,2), pv)
                dv = min((pi[0] - pv[:,0])**2 + (pi[1] - pv[:,1])**2)
                
                if ds <= np.finfo(float).eps*1e5 and dv != 0:
                    eledel = np.append(eledel, e)
                    d01 = p2segment(pi.reshape(1,2), p[t[e,[0,1]],:])
                    d02 = p2segment(pi.reshape(1,2), p[t[e,[0,2]],:])
                    l01 = (p[t[e,0],0] - p[t[e,1],0])**2 + (p[t[e,0],1] - p[t[e,1],1])**2
                    l02 = (p[t[e,0],0] - p[t[e,2],0])**2 + (p[t[e,0],1] - p[t[e,2],1])**2
                    l12 = (p[t[e,1],0] - p[t[e,2],0])**2 + (p[t[e,1],1] - p[t[e,2],1])**2
                    if d01 <= np.finfo(float).eps*1e5:
                        if l01 >= max(l02,l12):
                            te = np.array(([[local[i], t[e,2], t[e,0]],
                                            [local[i], t[e,1], t[e,2]]]))
                            tnew = np.append(tnew,te,axis = 0)
                        elif l02 >= max(l01,l12):
                            p02 = (p[t[e,0],:] + p[t[e,2],:])/2
                            pe = np.array(([[p02[0],p02[1]]]))
                            te = np.array(([[local[i], numnod + cou, t[e,0]],
                                            [local[i], t[e,1], numnod + cou],
                                            [t[e,1], t[e,2], numnod + cou]]))
                            tnew = np.append(tnew,te,axis = 0)
                            pnew = np.append(pnew,pe,axis = 0)
                            cou = cou + 1 
                        else:
                            p12 = (p[t[e,1],:] + p[t[e,2],:])/2
                            pe = np.array(([[p12[0],p12[1]]]))
                            te = np.array(([[local[i], numnod + cou, t[e,0]],
                                            [local[i], t[e,1], numnod + cou],
                                            [t[e,0], numnod + cou, t[e,2]]]))
                            tnew = np.append(tnew,te,axis = 0)
                            pnew = np.append(pnew,pe,axis = 0)
                            cou = cou + 1 
                    elif d02 <= np.finfo(float).eps*1e5:
                        if l02 >= max(l01,l12):
                            te = np.array(([[local[i], t[e,0], t[e,1]],
                                            [local[i], t[e,1], t[e,2]]]))
                            tnew = np.append(tnew,te,axis = 0)
                        elif l01 >= max(l02,l12):
                            p01 = (p[t[e,0],:] + p[t[e,1],:])/2
                            pe = np.array(([[p01[0],p01[1]]]))
                            te = np.array(([[local[i], t[e,0], numnod + cou],
                                            [local[i], numnod + cou, t[e,2]],
                                            [t[e,1], t[e,2], numnod + cou]]))
                            tnew = np.append(tnew,te,axis = 0)
                            pnew = np.append(pnew,pe,axis = 0)
                            cou = cou + 1
                        else:
                            p12 = (p[t[e,1],:] + p[t[e,2],:])/2
                            pe = np.array(([[p12[0],p12[1]]]))
                            te = np.array(([[local[i], t[e,0], numnod + cou],
                                            [local[i], numnod + cou, t[e,2]],
                                            [t[e,0], t[e,1], numnod + cou]]))
                            tnew = np.append(tnew,te,axis = 0)
                            pnew = np.append(pnew,pe,axis = 0)
                            cou = cou + 1
                    else:
                        if l12 >= max(l01,l02):
                            te = np.array(([[local[i], t[e,0], t[e,1]],
                                            [local[i], t[e,2], t[e,0]]]))
                            tnew = np.append(tnew,te,axis = 0)
                        elif l01 >= max(l02,l12):
                            p01 = (p[t[e,0],:] + p[t[e,1],:])/2
                            pe = np.array(([[p01[0],p01[1]]]))
                            te = np.array(([[local[i], numnod + cou, t[e,1]],
                                            [local[i], t[e,2], numnod + cou],
                                            [t[e,2], t[e,0], numnod + cou]]))
                            tnew = np.append(tnew,te,axis = 0)
                            pnew = np.append(pnew,pe,axis = 0)
                            cou = cou + 1
                        else:
                            p02 = (p[t[e,0],:] + p[t[e,2],:])/2
                            pe = np.array(([[p02[0],p02[1]]]))
                            te = np.array(([[local[i], numnod + cou, t[e,1]],
                                            [local[i], t[e,2], numnod + cou],
                                            [t[e,0], t[e,1], numnod + cou]]))
                            tnew = np.append(tnew,te,axis = 0)
                            pnew = np.append(pnew,pe,axis = 0)
                            cou = cou + 1
                    break
    else: # layer = 2,3,4
        cou = 0
        for i in range(len(local)):
            pi = poi[i,:]
            x,y = pi
            for e in range(t.shape[0]):
                pv = p[t[e,:],:]
                pv = np.append(pv,pv[:1,:], axis = 0)
                ds = p2segment(pi.reshape(1,2), pv)
                dv = min((pi[0] - pv[:,0])**2 + (pi[1] - pv[:,1])**2)
                
                if ds <= np.finfo(float).eps*1e5 and dv != 0:
                    eledel = np.append(eledel, e)
                    d01 = p2segment(pi.reshape(1,2), p[t[e,[0,1]],:])
                    d02 = p2segment(pi.reshape(1,2), p[t[e,[0,2]],:])
                    l01 = (p[t[e,0],0] - p[t[e,1],0])**2 + (p[t[e,0],1] - p[t[e,1],1])**2
                    l02 = (p[t[e,0],0] - p[t[e,2],0])**2 + (p[t[e,0],1] - p[t[e,2],1])**2
                    l12 = (p[t[e,1],0] - p[t[e,2],0])**2 + (p[t[e,1],1] - p[t[e,2],1])**2
                    if d01 <= np.finfo(float).eps*1e5:
                        te = np.array(([[local[i], t[e,0], t[e,2]],
                                        [local[i], t[e,1], t[e,2]]]))
                        tnew = np.append(tnew,te,axis = 0)
                        cou = cou + 1 
                    elif d02 <= np.finfo(float).eps*1e5:
                        te = np.array(([[local[i], t[e,0], t[e,1]],
                                        [local[i], t[e,2], t[e,1]]]))
                        tnew = np.append(tnew,te,axis = 0)
                        cou = cou + 1
                    else:
                        te = np.array(([[local[i], t[e,0], t[e,1]],
                                        [local[i], t[e,0], t[e,2]]]))
                        tnew = np.append(tnew,te,axis = 0)
                        cou = cou + 1
                    break
    tnew = np.delete(tnew,0,axis = 0)   
    pnew = np.delete(pnew,0,axis = 0)           
    t = np.append(t, tnew, axis=0)  
    p = np.append(p, pnew, axis=0)            
    t = np.delete(t,eledel[1::],axis = 0) 
    return p, t
def nodeedge(p, t):
    """ Check if a node belong to a edge in the mesh"""
    poi = np.zeros((1,2))
    local = np.zeros((1,1),np.int32)
    for e in range (t.shape[0]):
        pv = p[t[e,:],:]
        pv = np.append(pv,pv[:1,:], axis = 0)
        ds = p2segment(p, pv)
        ind = np.where(ds < np.finfo(float).eps*1e5)[0]
        if len(ind) > 3:
            indp = np.setdiff1d(ind,t[e,:])
            poi = np.append(poi,p[indp,:].reshape(len(indp),2), axis = 0)
            local = np.append(local, indp)
    poi = np.delete(poi, 0, axis = 0)
    local = np.delete(local, 0, axis = 0)
    return poi, local
def smoothing(p, t, nodfix):
    """ Smooth a mesh by using the Laplacian smoothing"""
    nodall = np.int32([i for i in range(p.shape[0])])
    nodche = np.setdiff1d(nodall,nodfix)
    for j in range(2):
        for i in range(len(nodche)):
            nodmov = p[nodche[i],:]
            elearo = np.where(t == nodche[i])[0]
            indaro = t[elearo,:]
            X = p[indaro,0];  Y = p[indaro,1]
            Ae = area(X,Y); Ae = Ae.reshape(len(Ae),1)
            Ae = Ae.reshape(len(Ae),1)
            totare = sum(Ae)
            indaro1 = np.setdiff1d(np.unique(indaro), nodche[i])
            p0 = np.sum(p[indaro1,:],axis = 0)/len(indaro1)
            p[nodche[i],0] = p0[0];p[nodche[i],1] = p0[1]
            
            X = p[indaro,0];  Y = p[indaro,1]
            Ae = area(X,Y); Ae = Ae.reshape(len(Ae),1)
            totare1 = sum(Ae)
            if totare1 > totare:
                p[nodche[i],0] = nodmov[0];p[nodche[i],1] = nodmov[1]
    return p, t