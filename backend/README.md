### Client Certificate Authentication

Enable this feature by ensuring app.run( debug=True, host=host_ip, port=port, ssl_context=ssl_context, request_handler=PeerCertWSGIRequestHandler ) is uncommented in backend\app.py.

When on the website, you will be asked to present a certificate. This step is optional to access the website, but is necessary to access the API.

Two certificates are provided for this example. The password is "12345678". To use these certificates, you must run the website on Firefox or a broswer than supports .pck12 files:

- backend\Client Certificates\Real_Client_Cert.pcks12 - A certificate signed by the CA and holds the correct private key. This will allow you to enter the website and the API.

- backend\Client Certificates\Client_Cert_Wrong_Private_Key.pcks12 - A certificate signed by the CA but does not hold the correct private key. This will deny you access to the website and API.

Presenting a certificate not signed by the root CA (backend\Certificates\root.pem) denies access to the website and API.

To use the API, visit https://127.0.0.1:5000/customers/Tx, where x is any number. Tx represents the transaction ID of the bank.

### Client Certificate Authentication - Certificate Generation Scripts 

