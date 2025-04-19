# #Following script will create a self signed root ca cert.
# from OpenSSL import crypto, SSL
# from os.path import join
# import random

# CN = input("Enter the common name of the certificate you want: ")
# pubkey = "%s.crt" % CN #replace %s with CN
# privkey = "%s.key" % CN # replcate %s with CN

# pubkey = join(".", pubkey)
# privkey = join(".", privkey)

# k = crypto.PKey()
# k.generate_key(crypto.TYPE_RSA, 2048)
# serialnumber=random.getrandbits(64)

# # create a self-signed cert
# cert = crypto.X509()
# cert.get_subject().C = input("Country: ")
# cert.get_subject().ST = input("State: ")
# cert.get_subject().L = input("City: ")
# cert.get_subject().O = input("Organization: ")
# cert.get_subject().OU = input("Organizational Unit: ")
# cert.get_subject().CN = CN
# cert.set_serial_number(serialnumber)
# cert.gmtime_adj_notBefore(0)
# cert.gmtime_adj_notAfter(31536000)#315360000 is in seconds.
# cert.set_issuer(cert.get_subject())
# cert.set_pubkey(k)
# cert.sign(k, 'sha512')
# pub=crypto.dump_certificate(crypto.FILETYPE_PEM, cert)
# priv=crypto.dump_privatekey(crypto.FILETYPE_PEM, k)
# open(pubkey,"wt").write(pub.decode("utf-8"))
# open(privkey, "wt").write(priv.decode("utf-8") )

#####
#####

# -*- coding: latin-1 -*-
#
# Copyright (C) AB Strakt
# Copyright (C) Jean-Paul Calderone
# See LICENSE for details.

"""
Certificate generation module.
"""

from OpenSSL import crypto
import random

TYPE_RSA = crypto.TYPE_RSA
TYPE_DSA = crypto.TYPE_DSA
TYPE_ECDSA = crypto.TYPE_EC

issuerCert = 'Certificates\\root.cer'
issuerKey = 'Certificates\\root.key'

def createKeyPair(type, bits):
    """
    Create a public/private key pair.

    Arguments: type - Key type, must be one of TYPE_RSA and TYPE_DSA
               bits - Number of bits to use in the key
    Returns:   The public/private key pair in a PKey object
    """
    pkey = crypto.PKey()
    pkey.generate_key(type, bits)
    return pkey

def createCertRequest(pkey, digest="SHA256"):
    """
    Create a certificate request.

    Arguments: pkey   - The key to associate with the request
               digest - Digestion method to use for signing, default is md5
               **name - The name of the subject of the request, possible
                        arguments are:
                          C     - Country name
                          ST    - State or province name
                          L     - Locality name
                          O     - Organization name
                          OU    - Organizational unit name
                          CN    - Common name
                          emailAddress - E-mail address
    Returns:   The certificate request in an X509Req object
    """
    req = crypto.X509()
    # subj = req.get_subject()

    # for (key,value) in name.items():
    #     setattr(subj, key, value)

    req.get_subject().C = input("Country: ")
    req.get_subject().ST = input("State: ")
    req.get_subject().L = input("City: ")
    req.get_subject().O = input("Organization: ")
    req.get_subject().OU = input("Organizational Unit: ")
    req.get_subject().CN = input("Common Name: ")

    req.set_pubkey(pkey)
    req.sign(pkey, digest)
    return req

def createCertificate(req, issuerCert, issuerKey, serial, digest="SHA256"):
    """
    Generate a certificate given a certificate request.

    Arguments: req        - Certificate reqeust to use
               issuerCert - The certificate of the issuer
               issuerKey  - The private key of the issuer
               serial     - Serial number for the certificate
               notBefore  - Timestamp (relative to now) when the certificate
                            starts being valid
               notAfter   - Timestamp (relative to now) when the certificate
                            stops being valid
               digest     - Digest method to use for signing, default is md5
    Returns:   The signed certificate in an X509 object
    """
    cert = crypto.X509()
    serial=random.getrandbits(64)
    cert.set_serial_number(serial)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(31536000) # A year in seconds.
    cert.set_issuer(issuerCert.get_subject())
    cert.set_subject(req.get_subject())
    cert.set_pubkey(req.get_pubkey())
    cert.sign(issuerKey, digest)
    return cert

if __name__ == '__main__':
    
    pkey = createKeyPair(TYPE_ECDSA, 256)

    req = createCertRequest(pkey, digest="SHA256")

    cert = createCertificate(req, issuerCert, issuerKey, digest="SHA256")