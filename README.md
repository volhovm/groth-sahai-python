# Groth-Sahai Proof System

This is an implementation of Groth-Sahai proof system, designed in particular to illustrate the language of "Knowledge of Elgamal Ciphertext that encrypts zero or one", as presented in the blog post https://crypto.ethereum.org/blog/groth-sahai-blogpost.

Notation-wise the implementation follows the description of the Groth-Sahai proof system presented in "Malleable Proof Systems and Applications" by Chase et al., Appendix A.1. [1]

This only affects the notation, as the proving system is essentially the same as in the original paper, "Efficient Non-interactive Proof Systems for Bilinear Groups" [2].

Another useful resource for understanding GS proofs is "Groth-Sahai Proofs Revisited" [3].


## How To Run This

For `nix` users, preparing the setup is easy, just run `nix-shell shell.nix`.
Otherwise, the only non-standard library it uses is [py_ecc](https://github.com/ethereum/py_ecc) which can be installed from your package manager or from `pip`.

Then, simply run `groth_sahai.py`, which contains both the library and some examples / tests.
```
>>> python groth_sahai.py
- Preparing the setup
- Committing
- Creating the proof
- Verifying the proof
 * Checking commitment consistency
 * Equation 1/4
 ** Verification, pairings 1/4
 ** Verification, pairings 2/4
 ** Verification, pairings 3/4
 ** Verification, pairings 4/4
 * Equation 2/4
 ** Verification, pairings 1/4
 ** Verification, pairings 2/4
 ** Verification, pairings 3/4
 ** Verification, pairings 4/4
 * Equation 3/4
 ** Verification, pairings 1/4
 ** Verification, pairings 2/4
 ** Verification, pairings 3/4
 ** Verification, pairings 4/4
 * Equation 4/4
 ** Verification, pairings 1/4
 ** Verification, pairings 2/4
 ** Verification, pairings 3/4
 ** Verification, pairings 4/4
Proof verifies:  True
```

### References

1. https://eprint.iacr.org/2012/012.pdf
2. https://eprint.iacr.org/2007/155.pdf
3. https://eprint.iacr.org/2009/599.pdf
