#!/usr/bin/env python

import sys
import fileinput
import string
import os

def codegen(src,pattern,stencil_size,radius,model,dim):
    src.write('void '+pattern+str(radius)+'(cl::sycl::queue & q, const size_t n, ')
    if (dim==2):
        src.write('cl::sycl::buffer<double, 2> & d_in, ')
        src.write('cl::sycl::buffer<double, 2> & d_out)\n')
    else:
        src.write('cl::sycl::buffer<double> & d_in, ')
        src.write('cl::sycl::buffer<double> & d_out)\n')
    src.write('{\n')
    src.write('  q.submit([&](cl::sycl::handler& h) {\n')
    src.write('    auto in  = d_in.get_access<cl::sycl::access::mode::read>(h);\n')
    src.write('    auto out = d_out.get_access<cl::sycl::access::mode::read_write>(h);\n')
    if (dim==2):
        for r in range(1,radius+1):
            src.write('    cl::sycl::id<2> dx'+str(r)+'(cl::sycl::range<2> {'+str(r)+',0});\n')
            src.write('    cl::sycl::id<2> dy'+str(r)+'(cl::sycl::range<2> {0,'+str(r)+'});\n')
    src.write('    h.parallel_for<class '+pattern+str(radius)+'_'+str(dim)+'d>(')
    src.write('{n-'+str(2*radius)+',n-'+str(2*radius)+'}, ')
    src.write('{'+str(radius)+','+str(radius)+'}, ')
    src.write('[=] (auto it) {\n')
    if (dim==2):
        src.write('        cl::sycl::id<2> xy = it.get_id();\n')
        src.write('        out[xy] += ')
    else:
        # 1D indexing the slow way
        #src.write('        auto i = it[0];\n')
        #src.write('        auto j = it[1];\n')
        #src.write('        out[i*n+j] += ')
        # 1D indexing the fast way
        src.write('        out[it[0]*n+it[1]] += ')
    if pattern == 'star':
        for i in range(1,radius+1):
            if (dim==2):
                if i > 1:
                    src.write('\n')
                    src.write(19*' ')
                src.write('+in[xy+dx'+str(i)+'] * '+str(+1./(2.*i*radius)))
                src.write('\n'+19*' ')
                src.write('+in[xy-dx'+str(i)+'] * '+str(-1./(2.*i*radius)))
                src.write('\n'+19*' ')
                src.write('+in[xy+dy'+str(i)+'] * '+str(+1./(2.*i*radius)))
                src.write('\n'+19*' ')
                src.write('+in[xy-dy'+str(i)+'] * '+str(-1./(2.*i*radius)))
            else:
                # 1D indexing the slow way
                #if i > 1:
                #    src.write('\n')
                #    src.write(22*' ')
                #src.write('+in[i*n+(j+'+str(i)+')] * '+str(+1./(2.*i*radius)))
                #src.write('\n'+22*' ')
                #src.write('+in[i*n+(j-'+str(i)+')] * '+str(-1./(2.*i*radius)))
                #src.write('\n'+22*' ')
                #src.write('+in[(i+'+str(i)+')*n+j] * '+str(+1./(2.*i*radius)))
                #src.write('\n'+22*' ')
                #src.write('+in[(i-'+str(i)+')*n+j] * '+str(-1./(2.*i*radius)))
                # 1D indexing the fast way
                if i > 1:
                    src.write('\n')
                    src.write(30*' ')
                src.write('+in[it[0]*n+(it[1]+'+str(i)+')] * '+str(+1./(2.*i*radius)))
                src.write('\n'+30*' ')
                src.write('+in[it[0]*n+(it[1]-'+str(i)+')] * '+str(-1./(2.*i*radius)))
                src.write('\n'+30*' ')
                src.write('+in[(it[0]+'+str(i)+')*n+it[1]] * '+str(+1./(2.*i*radius)))
                src.write('\n'+30*' ')
                src.write('+in[(it[0]-'+str(i)+')*n+it[1]] * '+str(-1./(2.*i*radius)))
            if i == radius:
                src.write(';\n')
    else:
        print('grid not implemented\n')
    src.write('    });\n')
    src.write('  });\n')
    src.write('}\n\n')

def instance(src,model,pattern,r):
    if pattern == 'star':
        stencil_size = 4*r+1
    else:
        stencil_size = (2*r+1)**2
    codegen(src,pattern,stencil_size,r,model,1)
    codegen(src,pattern,stencil_size,r,model,2)

def main():
    for model in ['sycl']:
      src = open('stencil_'+model+'.hpp','w')
      #for pattern in ['star','grid']:
      for pattern in ['star']:
        for r in range(1,6):
          instance(src,model,pattern,r)
      src.close()

if __name__ == '__main__':
    main()

