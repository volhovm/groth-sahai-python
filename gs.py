from py_ecc.bls import G2ProofOfPossession as bls_pop

private_key = 5566
public_key = bls_pop.SkToPk(private_key)

message = b'\xab' * 32  # The message to be signed

# Signing
signature = bls_pop.Sign(private_key, message)

# Verifying
assert bls_pop.Verify(public_key, message, signature)

print("bla")
