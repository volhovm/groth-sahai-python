from dataclasses import dataclass
from py_ecc.typing import (
    Field,
    GeneralPoint,
    Point2D,
)
from py_ecc.fields import (
    bls12_381_FQ as FQ,
    bls12_381_FQ2 as FQ2,
    bls12_381_FQ12 as FQ12,
    bls12_381_FQP as FQP,
)
from py_ecc.bls12_381 import ( G1, G2, Z1, Z2, pairing, neg, multiply, add )
import py_ecc.bls12_381 as BLS

P1 = Point2D[FQ]
P2 = Point2D[FQ2]

@dataclass
class V1Elem:
    v1: list[P1]

@dataclass
class V2Elem:
    v2: list[P2]

@dataclass
class Com:
    com1: list[V1Elem]
    com2: list[V2Elem]

@dataclass
class Params:
    u1: list[V1Elem]
    u2: list[V2Elem]


@dataclass
class Proof:
    theta: list[V1Elem]
    phi: list[V2Elem]

@dataclass
class Instance:
    m: int
    n: int
    gammaT: list[list[int]]
    a: list[int]
    b: list[int]


def comAlike1(u: list[V1Elem], e: list[int]):
    for i in range(len(e)):
        if (e[i] != -1 and (u[i].v1[0] != Z1 or
                            u[i].v1[1] != multiply(G1, e[i]))):
            return False
    return True

def comAlike2(u: list[V2Elem], e: list[int]):
    for i in range(len(e)):
        if (e[i] != -1 and (u[i].v2[0] != Z2 or
                            u[i].v2[1] != multiply(G2, e[i]))):
            return False
    return True



def buildParams(rand: list[list[list[int]]]):
    # subspaces should not be in form (0,a)? This is from CKLM
    assert not (rand[0][0][0] == 0 and rand[0][1][0] == 0 and rand[0][0][1] == rand[0][1][1]), "buildParams 1"
    assert not (rand[1][0][0] == 0 and rand[1][1][0] == 0 and rand[1][0][1] == rand[1][1][1]), "buildParams 2"

    r = Params([V1Elem([Z1,Z1]),V1Elem([Z1,Z1])],
               [V2Elem([Z2,Z2]),V2Elem([Z2,Z2])])

    for i in range(2):
        for j in range(2):
            r.u1[i].v1[j] = multiply(G1, rand[0][i][j]);

    for i in range(2):
        for j in range(2):
            r.u2[i].v2[j] = multiply(G2, rand[1][i][j]);

    return r

def commit(inst: Instance,
           params: Params,
           x: list[P1],
           y: list[P2],
           rs: list[list[list[int]]]):

    com1 = []
    com2 = []

    for i in range(inst.m):
        com1.append(V1Elem([Z1,Z1]))
    for i in range(inst.n):
        com2.append(V2Elem([Z2,Z2]))

    for i in range(inst.m):
        for vv in range(2):
            com1[i].v1[vv] = add(multiply(params.u1[0].v1[vv], rs[0][i][0]),
                                 multiply(params.u1[1].v1[vv], rs[0][i][1]))
        com1[i].v1[1] = add(com1[i].v1[1], x[i]);

    for i in range(inst.n):
        for vv in range(2):
            com2[i].v2[vv] = add(multiply(params.u2[0].v2[vv], rs[1][i][0]),
                                 multiply(params.u2[1].v2[vv], rs[1][i][1]))
        com2[i].v2[1] = add(com2[i].v2[1], y[i]);

    return Com(com1,com2)


######################################################3

inst = Instance(2, 2, [[1,0],[0,-1]], [-1,0], [0,-1]);
c_x = [123, 0];
c_y = [0, 123];
rst = [ [[1235,3462],[0,0]],
        [[0,0],[1924,6258]],
        [[8334,1953],[2342,4935]]
      ];

params = buildParams([[[64321,83371],[12924,62558]],
                     [[83334,19553],[25342,43935]]]);

x = []
y = []
for c in c_x:
    x.append(multiply(G1,c))
for c in c_y:
    y.append(multiply(G2,c))

com = commit(inst,params,x,y,rst)

print(params)
print(com)

##########################################################3


#p = V1Elem([G1])
#
#print(p)
#print(p.v1)
#
#p1 = pairing(G2, G1)
#pn1 = pairing(G2, neg(G1))
#print(p1 * pn1 == FQ12.one())
