from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
import datetime

# Load cert key
with open("backend\key.pem", "rb") as key_file:
    key = serialization.load_pem_private_key(
    key_file.read(),
    password=b"passphrase",
    )

# Here is our root key
with open('backend\Certificates\\root.key', "rb") as key_file:
    root_key = serialization.load_pem_private_key(
    key_file.read(),
    password=None,
    )

# Here is our root cert
with open('backend\Certificates\\root.cer', "r") as key_file:
    root_cert = x509.load_pem_x509_certificate(key_file.read().encode('ascii'))

# Get the attributes
# co = root_cert.subject.get_attributes_for_oid(NameOID.COUNTRY_NAME)[0].value
# sn = root_cert.subject.get_attributes_for_oid(NameOID.STATE_OR_PROVINCE_NAME)[0].value
# ln = root_cert.subject.get_attributes_for_oid(NameOID.LOCALITY_NAME)[0].value
# on = root_cert.subject.get_attributes_for_oid(NameOID.ORGANIZATION_NAME)[0].value
cn = root_cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value

# Various details about who we are. For a self-signed certificate the
# subject and issuer are always the same.
# subject = issuer = x509.Name([
#     # x509.NameAttribute(NameOID.COUNTRY_NAME, co),
#     # x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, sn),
#     # x509.NameAttribute(NameOID.LOCALITY_NAME, ln),
#     # x509.NameAttribute(NameOID.ORGANIZATION_NAME, on),
#     x509.NameAttribute(NameOID.COMMON_NAME, cn),
# ])

subject = issuer = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "California"),
    x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, "My Company"),
    x509.NameAttribute(NameOID.COMMON_NAME, "mysite.com"),
])

cert = x509.CertificateBuilder().subject_name(
    subject
).issuer_name(
    root_cert.issuer
).public_key(
    key.public_key()
).serial_number(
    x509.random_serial_number()
).not_valid_before(
    datetime.datetime.now(datetime.timezone.utc)
).not_valid_after(
    # Our certificate will be valid for 10 days
    datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365)
).add_extension(
    x509.SubjectAlternativeName([x509.DNSName("localhost")]),
    critical=False,
# Sign our certificate with our private key
).sign(root_key, hashes.SHA256())
# Write our certificate out to disk.
with open("backend\certificate.pem", "wb") as f:
    f.write(cert.public_bytes(serialization.Encoding.PEM))