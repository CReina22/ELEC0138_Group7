import requests
cert_file_path = "backend\certificate.pem"
#key_file_path = "backend\key.pem"

# url = "https://localhost:5000/employees"
# params = {"id": 1}
# #cert = (cert_file_path, key_file_path)
# cert = (cert_file_path)
# r = requests.get(url, cert=cert)

import requests

x = requests.get('https://localhost:5000/employees', verify=True, cert=cert_file_path)
print(x.status_code)