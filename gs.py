# TODO: fix notation so that it's similar to the blog post
#
# Notation-wise this implementation follows the description of the
# Groth-Sahai proof system presented in "Malleable Proof Systems and
# Applications" by Chase et al., Appendix A.1.
# - https://eprint.iacr.org/2012/012.pdf
#
# This only affects the notation, as the proving system is essentially the same
# as in the original paper, "Efficient Non-interactive Proof Systems for
# Bilinear Groups".
# - https://eprint.iacr.org/2007/155.pdf
#
# Another useful resource for understanding GS proofs is "Groth-Sahai Proofs
# Revisited".
# - https://eprint.iacr.org/2009/599.pdf

import random
from typing import (Tuple)
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




######################################################
# Datatypes
######################################################

P1 = Point2D[FQ]
P2 = Point2D[FQ2]

# Samples a random coefficient in the order of the elliptic curve
def rpnt():
    return random.randrange(BLS.curve_order-1)

# Element of V_1 = G_1^2
@dataclass
class V1Elem:
    v1: list[P1] # length 2

# Element of V_2 = G_2^2
@dataclass
class V2Elem:
    v2: list[P2] # length 2

# The language description.
@dataclass
class Instance:
    m: int # Size of vector X \in G_1^m
    n: int # Size of vector Y \in G_2^n
    # List of matrices \Gamma, each corresponding to a pairing equation
    gammaT: list[list[list[int]]]
    # A \in (G_1 \cup \bot)^m.
    # When the second integer is -1, the pair is treated as \bot
    a: list[Tuple[P1,int]]
    # B \in (G_2 \cup \bot)^n
    b: list[Tuple[P2,int]]


# Setup parameters, contains U_1 \in V_1^2, U_2 \in V_2^2
@dataclass
class Params:
    u1: list[V1Elem]
    u2: list[V2Elem]


# Commitment to X \in G_1^n and Y \in G_2^m
@dataclass
class Com:
    com_c: list[V1Elem]
    com_d: list[V2Elem]

# Proof contains 2 V1 elements and 2 V2 elements
@dataclass
class Proof:
    theta: list[V1Elem]
    phi: list[V2Elem]



######################################################
# Proof creation & verification
######################################################


# The following two functions implement the ~= check, i.e. that the
# commitments to X and Y contain certain vectors in "clear", as defined by a and b.
def comAlike1(com_c: list[V1Elem], a: list[Tuple[P1,int]]):
    for i in range(len(a)):
        if (a[i][1] != -1 and
            (com_c[i].v1[0] != Z1 or
             com_c[i].v1[1] != a[i][0])):
            print("comAlike1: %d" % i)
            return False
    return True

def comAlike2(com_d: list[V2Elem], b: list[Tuple[P2,int]]):
    for i in range(len(b)):
        if (b[i][1] != -1 and
            (com_d[i].v2[0] != Z2 or
             com_d[i].v2[1] != b[i][0])):
            print("comAlike2: %d" % i)
            return False
    return True

# This wraps multiply to support multiplication with negative scalars.
def multiply(pt: Point2D[Field], n: int) -> Point2D[Field]:
    if n < 0:
        return neg(BLS.multiply(pt,-n))
    else:
        return BLS.multiply(pt,n)

# A convenient wrapper to build parameters from exponent vectors (parameter coefficients).
def buildParams(par_c: list[list[list[int]]]):
    # subspaces should not be in form (0,a)? This is from CKLM
    assert not (par_c[0][0][0] == 0 and
                par_c[0][1][0] == 0 and
                par_c[0][0][1] == par_c[0][1][1]), "buildParams 1"
    assert not (par_c[1][0][0] == 0 and
                par_c[1][1][0] == 0 and
                par_c[1][0][1] == par_c[1][1][1]), "buildParams 2"

    r = Params([V1Elem([Z1,Z1]),V1Elem([Z1,Z1])],
               [V2Elem([Z2,Z2]),V2Elem([Z2,Z2])])

    for i in range(2):
        for j in range(2):
            r.u1[i].v1[j] = multiply(G1, par_c[0][i][j]);
            r.u2[i].v2[j] = multiply(G2, par_c[1][i][j]);

    return r

# Parameters random sampling
def sampleParams():
    par_c = [[[0,0],[0,0]],[[0,0],[0,0]]]
    for i in range(2):
        for j in range(2):
            for k in range(2):
                par_c[i][j][k] = rpnt()
    return buildParams(par_c)

# Commitment function. r,s are randomness vectors.
def commit(inst: Instance,
           params: Params,
           x: list[P1],
           y: list[P2],
           r: list[list[int]],
           s: list[list[int]]):

    com_c = []
    com_d = []

    for i in range(inst.m):
        com_c.append(V1Elem([Z1,Z1]))
    for i in range(inst.n):
        com_d.append(V2Elem([Z2,Z2]))

    for i in range(inst.m):
        for vv in range(2):
            com_c[i].v1[vv] = add(multiply(params.u1[0].v1[vv], r[i][0]),
                                 multiply(params.u1[1].v1[vv], r[i][1]))
        com_c[i].v1[1] = add(com_c[i].v1[1], x[i]);

    for i in range(inst.n):
        for vv in range(2):
            com_d[i].v2[vv] = add(multiply(params.u2[0].v2[vv], s[i][0]),
                                 multiply(params.u2[1].v2[vv], s[i][1]))
        com_d[i].v2[1] = add(com_d[i].v2[1], y[i]);

    return Com(com_c,com_d)

# Produces a Proof per each \Gamma_i matrix in the instance. ts is a list of T matrices,
# one per each \Gamma_i.
def prove(inst: Instance,
          params: Params,
          com: Com,
          x: list[P1],
          y: list[P2],
          r: list[list[int]],
          s: list[list[int]],
          ts: list[list[list[int]]]):

    proofs = []


    for ii in range(len(inst.gammaT)):
        gammaT = inst.gammaT[ii]
        theta = [V1Elem([Z1,Z1]),V1Elem([Z1,Z1])]
        phi = [V2Elem([Z2,Z2]),V2Elem([Z2,Z2])]

        # theta, v1[0] and v1[1]
        for i in range(2):
            # T U_1
            for vv in range(2):
                for j in range(2):
                    theta[i].v1[vv] = add(theta[i].v1[vv],
                                          multiply(params.u1[j].v1[vv], ts[ii][i][j]));

            # s^T \Gamma^T \iota_1(X), only for vv = 1 because of \iota_1(X)
            for j in range(inst.n):
                for k in range(inst.m):
                    theta[i].v1[1] = add(theta[i].v1[1],
                                         multiply(multiply(x[k], gammaT[j][k]),
                                                  s[j][i]));

        # phi, v2[0] and v2[1]
        for vv in range(2):
            for i in range(2):
                # r^T \Gamma D
                for j in range(inst.m):
                    for k in range(inst.n):
                        phi[i].v2[vv] = add(phi[i].v2[vv],
                                multiply(
                                    multiply(com.com_d[k].v2[vv],gammaT[k][j]),
                                    r[j][i]));

                # -T^T U_2
                for j in range(2):
                    phi[i].v2[vv] = add(phi[i].v2[vv],
                                        neg(multiply(params.u2[j].v2[vv], ts[ii][j][i])));

        proofs.append(Proof(theta,phi))

    return proofs

# Checks whether the proof is valid.
def verifyProof(inst: Instance,
                params: Params,
                com: Com,
                proofs: [Proof]):

   print("* Checking commitment consistency")
   if (not comAlike1(com.com_c, inst.a)):
       return False;
   if (not comAlike2(com.com_d, inst.b)):
       return False;

   p1 = []
   p2 = []
   for i in range(inst.m+4):
       p1.append(Z1)
       p2.append(Z2)

   for ii in range(len(inst.gammaT)):
       gammaT = inst.gammaT[ii]
       proof = proofs[ii]
       print("* Equation %d/%d" % (ii+1,len(inst.gammaT)))

       for vv1 in range(2):
           for vv2 in range(2):
               for i in range(inst.m):
                   p1[i] = com.com_c[i].v1[vv1];
                   p2[i] = Z2;
                   for j in range(inst.n):
                       p2[i] = add(p2[i],
                                   multiply(com.com_d[j].v2[vv2], gammaT[j][i]));

               for i in range(2):
                   p1[inst.m+i] = neg(params.u1[i].v1[vv1]);
                   p2[inst.m+i] = proof.phi[i].v2[vv2];

               for i in range(2):
                   p1[inst.m+2+i] = proof.theta[i].v1[vv1];
                   p2[inst.m+2+i] = neg(params.u2[i].v2[vv2]);

               print("** Verification, pairings %d/4" % (vv1 * 2 + vv2 + 1))
               pairing_v = FQ12.one();
               #pairing_v_prev = FQ12.one();
               for i in range(inst.m+4):
                   pairing_v = pairing_v * pairing(p2[i],p1[i])
                   #print("*** Pairing value after step %d/%d:" % (i+1,inst.m+4))
                   #print("Same" if pairing_v == pairing_v_prev else pairing_v)
                   #pairing_v_prev = pairing_v

               if pairing_v != FQ12.one():
                   return False

   return True


######################################################
# Tests & language descriptions
######################################################

# Runs the evaluation / correctness check, uses global variables (defined below)
def runEvalCheck(c_x, c_y, c_a, c_b, gammas):
    print("Preparing the setup")

    m = len(c_x)
    n = len(c_y)

    x = list(map(lambda c: multiply(G1,c), c_x))
    y = list(map(lambda c: multiply(G2,c), c_y))

    r = list(map(lambda i: [0,0] if c_a[i] != None else [rpnt(),rpnt()], range(m)))
    s = list(map(lambda i: [0,0] if c_b[i] != None else [rpnt(),rpnt()], range(n)))

    t = list(map(lambda i: [[rpnt(),rpnt()],[rpnt(),rpnt()]], range(len(gammas))))

    a = list(map(lambda c: (None,-1) if c == None else (multiply(G1,c),0), c_a))
    b = list(map(lambda c: (None,-1) if c == None else (multiply(G2,c),0), c_b))

    inst = Instance(m, n, gammas, a, b)

    params = sampleParams()
    print("Committing")
    com = commit(inst,params,x,y,r,s)
    print("Creating the proof")
    proof = prove(inst,params,com,x,y,r,s,t)

    print("Verifying the proof")
    print("Proof verifies: ", verifyProof(inst,params,com,proof))


# Toy example
def testToy1():
    # This trivial test makes sure that: e([10]G,[2]H)e([4]G,(-1*)[5]H) = 1
    c_x = [10, 4]
    c_y = [2, 5]

    # The values a,b only hide 2 and 5: "None" means "hide this values under commitment".
    # Non-hidden values must be the same as in X, Y.
    # So essentially it makes sure that \exist W1 W2 s.t.
    #   e(10[G],W1)e(2[G],(-1*)W2) = 1
    c_a = [10,None]
    c_b = [2,None]

    # Note that in the real world, a,b, are not exponent values (c_a)_i, (c_b)_i
    # (like here), but [(c_a)_i]G and [(c_b)_i]H. We do this conversion in
    # runEvalCheck, it's just easier to define it using exponent coefficients here.

    # Instance elements in c_x, c_y are without minuses. Gamma adds (-1)*
    gammaT = [[1,0],[0,-1]]

    runEvalCheck(c_x, c_y, c_a, c_b, [gammaT])


# Toy example 2
def testToy2():
    # This test checks that \exists r,msg  s.t.
    # e([ct]G,H) e(pk,(-1)[r]H) e(G,(-1)[msg]H) = 1
    #
    # Which is essentially

    msg = 4212315
    r = 241423
    sk = 122412 # pk = [sk]G
    ct = sk * r + msg

    c_x = [ct,sk,msg]
    c_a = [ct,sk,None]
    c_y = [r,1]
    c_b = [r,None]

    gammaT = [[0,-1,0],[1,0,-1]]

    runEvalCheck(c_x, c_y, c_a, c_b, [gammaT])


# Elgamal Proof that ciphertext encrypts 0 or 1
def testElgamal():
    msg = 1 # or 0
    r = 14352345
    sk = 36534152
    ct1 = r
    ct2 = sk * r + msg

    w1 = r
    w2 = msg
    w3 = msg

    c_x = [w2, ct1, ct2, sk, 1]
    c_a = [None, ct1, ct2, sk, 1]

    c_y = [w1, w3, 1]
    c_b = [None, None, 1]

    gammaT_E1 = [[0,0,0,0,-1],[0,0,0,0,0],[0,1,0,0,0]]
    gammaT_E2 = [[0,0,0,-1,0],[0,0,0,0,0],[-1,0,1,0,0]]
    gammaT_E3 = [[0,0,0,0,0],[0,0,0,0,-1],[1,0,0,0,0]]
    gammaT_E4 = [[0,0,0,0,0],[1,0,0,0,0],[-1,0,0,0,0]]
    gammas = [gammaT_E1,gammaT_E2,gammaT_E3,gammaT_E4]

    runEvalCheck(c_x, c_y, c_a, c_b, gammas)


######################################################

#testToy1()
#testToy2()
testElgamal()
