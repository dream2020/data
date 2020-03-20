"""
This module implement util classes for reading and visalizing the DREAM dataset using Python 3. 
"""

import json
import io
import numpy as np
from math import sin,cos
from functools import reduce

def open(path):
    with io.open(path) as f:
        return Intervention(json.load(f))

def withlast(iterable):
	i = iter(iterable)
	try:
		v = next(i)
		for vv in i: 
			yield v+(False,) if isinstance(v,tuple) else (v,False)
			v = vv
		yield v+(True,) if isinstance(v,tuple) else (v,True)
	except StopIteration:
		pass

class Intervention(dict):

    def __init__(self, data):
        for key in data:
            self[key] = self.__fixNan(data[key])

    def __fixNan(self,data):
        if data is None:
            return float('nan')
        elif isinstance(data,dict):
            for key in data:
                data[key] = self.__fixNan(data[key])
        elif isinstance(data,list):
            for i, v in enumerate(data):
                data[i] = self.__fixNan(v)
        return data

    def __repr__(self):
        return 'Intervention recording with {} samples'.format(self.sampleCount())

    def sampleCount(self):
        return len(self['skeleton']['head']['x'])

    def structure(self,dic=None,linewidth=50,tab=1):
        if dic is None: dic = self
        s = ['{']
        for key,val,islast in withlast(dic.items()):
            if isinstance(val,dict):
                s.append('"{0}": {1}{2}'.format(key, self.structure(val,linewidth,tab+1), '' if islast else ','))
            elif isinstance(val,list):
                s.append('"{0}": {1}{2}'.format(key, '[]', '' if islast else ','))
            elif isinstance(val,str):
            	s.append('"{0}": "{1}"{2}'.format(key, val, '' if islast else ','))
            elif val is None:
                s.append('"{0}": null{2}'.format(key, '' if islast else ','))
            else:
                s.append('"{0}": {1}{2}'.format(key, val, '' if islast else ','))
        if len(s)==1:
            return "{}"
        elif reduce(lambda n,s: n+len(s),s,0) < linewidth:
            return ''.join(s) + '}'
        else:
            return ('\n'+(' '*4*tab)).join(s) + '\n' + (' '*4*(tab-1)) + '}'

    def gaze(self,distance=1):
        headPose = [np.array([v]).transpose() for v in zip(self['skeleton']['head']['x'],self['skeleton']['head']['y'],self['skeleton']['head']['z'])]
        xrot = [self.xrot(gaze) for gaze in zip(self['head_gaze']['rx'],self['head_gaze']['ry'],self['head_gaze']['rz'])]
        return [np.matmul(rot,pose) for rot,pose in zip(xrot,headPose)]
        
    def xrot(self,gaze):
        v = gaze[0]
        return np.array([[0,0,1],[-sin(v),cos(v),0],[cos(v),sin(v),0]])
