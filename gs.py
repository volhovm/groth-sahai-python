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
from py_ecc.bls12_381 import ( G1, G2, Z1, Z2, pairing, neg, add )
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

def multiply(pt: Point2D[Field], n: int) -> Point2D[Field]:
    if n < 0:
        return neg(BLS.multiply(pt,-n))
    else:
        return BLS.multiply(pt,n)

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


def prove(inst: Instance,
          params: Params,
          com: Com,
          x: list[P1],
          y: list[P2],
          rst: list[list[list[int]]]):

    theta = [V1Elem([Z1,Z1]),V1Elem([Z1,Z1])]
    phi = [V2Elem([Z2,Z2]),V2Elem([Z2,Z2])]

    # theta, v1[0] and v1[1]
    for i in range(2):
        # T U_1
        for vv in range(2):
            for j in range(2):
                theta[i].v1[vv] = add(theta[i].v1[vv], multiply(params.u1[j].v1[vv], rst[2][i][j]));

        # s^T \Gamma^T \iota_1(X), only for vv = 1 because of \iota_1(X)
        for j in range(inst.n):
            for k in range(inst.m):
                theta[i].v1[1] = add(theta[i].v1[1], multiply(multiply(x[k], inst.gammaT[j][k]), rst[1][j][i]));

    # phi, v2[0] and v2[1]
    for vv in range(2):
        for i in range(2):
            # r^T \Gamma D
            for j in range(inst.m):
                for k in range(inst.n):
                    phi[i].v2[vv] = add(phi[i].v2[vv],
                            multiply(multiply(com.com2[k].v2[vv],inst.gammaT[k][j]),rst[0][j][i]));

            # -T^T U_2
            for j in range(2):
                phi[i].v2[vv] = add(phi[i].v2[vv], neg(multiply(params.u2[j].v2[vv], rst[2][j][i])));


    return Proof(theta,phi)

def verifyProof(inst: Instance,
                params: Params,
                com: Com,
                proof: Proof):
        if (not comAlike1(com.com1, inst.a)):
            return False;
        if (not comAlike2(com.com2, inst.b)):
            return False;

        p1 = []
        p2 = []
        for i in range(inst.m+4):
            p1.append(Z1)
            p2.append(Z2)

        for vv1 in range(2):
            for vv2 in range(2):
                for i in range(inst.m):
                    p1[i] = com.com1[i].v1[vv1];
                    for j in range(inst.n):
                        p2[i] = multiply(com.com2[j].v2[vv2], inst.gammaT[j][i]);

                for i in range(2):
                    p1[inst.m+i] = neg(params.u1[i].v1[vv1]);
                    p2[inst.m+i] = proof.phi[i].v2[vv2];

                for i in range(2):
                    p1[inst.m+2+i] = proof.theta[i].v1[vv1];
                    p2[inst.m+2+i] = neg(params.u2[i].v2[vv2]);

                print("Pairing comp...")
                pairing_v = FQ12.one();
                for i in range(inst.m+4):
                    pairing_v = pairing_v * pairing(p2[i],p1[i])

                if pairing_v != FQ12.one():
                    return False

        return True


######################################################3

inst = Instance(2, 2, [[1,0],[0,-1]], [-1,0], [0,-1])
c_x = [123, 0]
c_y = [0, 123]
rst = [ [[1235,3462],[0,0]],
        [[0,0],[1924,6258]],
        [[8334,1953],[2342,4935]]
      ]

params = buildParams([[[64321,83371],[12924,62558]],
                     [[83334,19553],[25342,43935]]]);

x = []
y = []
for c in c_x:
    x.append(multiply(G1,c))
for c in c_y:
    y.append(multiply(G2,c))

com = commit(inst,params,x,y,rst)
proof = prove(inst,params,com,x,y,rst)
print(verifyProof(inst,params,com,proof))
