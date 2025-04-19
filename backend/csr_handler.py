from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.backends import default_backend
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes

# # Generate our key
# key = rsa.generate_private_key(
#     public_exponent=65537,
#     key_size=2048,
# )

# # Write our key to disk for safe keeping
# with open("backend\key.pem", "wb") as f:
#     f.write(key.private_bytes(
#         encoding=serialization.Encoding.PEM,
#         format=serialization.PrivateFormat.TraditionalOpenSSL,
#         encryption_algorithm=serialization.BestAvailableEncryption(b"passphrase"),
#     ))

with open("backend\key.pem", "rb") as key_file:
    key = serialization.load_pem_private_key(
    key_file.read(),
    password=b"passphrase",
    )

# Generate a CSR
csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
    # Provide various details about who we are.
    x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "California"),
    x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, "My Company"),
    x509.NameAttribute(NameOID.COMMON_NAME, "mysite.com"),
])).add_extension(
    x509.SubjectAlternativeName([
        # Describe what sites we want this certificate for.
        x509.DNSName("mysite.com"),
        x509.DNSName("www.mysite.com"),
        x509.DNSName("subdomain.mysite.com"),
    ]),
    critical=False,
# Sign the CSR with our private key.
).sign(key, hashes.SHA256())
# Write our CSR out to disk.
with open("backend\csr.pem", "wb") as f:
    f.write(csr.public_bytes(serialization.Encoding.PEM))