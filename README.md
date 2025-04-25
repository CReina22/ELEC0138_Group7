# ELEC0138_Group7
Run the command `conda env create -f environment.yml`

Run the command `conda activate DigitalBank ` to activate the environment.

Install the dependencies `pip install -r requirements.txt `

In terminal, 'cd backend'

             'python app.py'

Use the following command in conda powershell prompt:

             'conda init powershell'

### ℹ️ Dashboard Behavior
- If log in with a **testuser account**, you'll see 40 transactions assigned to that user.
- If log in with a **real account** (registered via email), you'll see the top 100 transactions.



### PHP Captive Portal
To view the captive portal ensure PHP is installed onto your device and then navigate to the CaptivePortal directory. Form here run the following in the terminal:

                'php -S 127.0.0.1:8000'

### Password Cracker
To use the password cracker navigate to the PasswordCracker directory and add the email address of the target. Then fill out the passwords.txt with the passwords to use. Then run main.py in the terminal.

### Anomaly Detection by Fingerprinting
To enable this feature ensure the variable FINGERPRINTING is set to true in app.py. 

Then log in across multiple devices that are commonly used with one holdout. 

The first 5 logins do not perform anomaly detection to build a profile of the user. After this, the ML model will look for anomalies in the sign in and reject anomalous ones. 
When an anomaly is identified it will send a one-time passcode to the registered email (check junk). This approves the current browser allowing the user to log in again.

To view the experimentation of the model along with testing implementation navigate to the Fingerprint Anomaly Detection directory.

### Client Certificate Authentication

Enable this feature by ensuring app.run( debug=True, host=host_ip, port=port, ssl_context=ssl_context, request_handler=PeerCertWSGIRequestHandler ) is uncommented.

When on the website, you will be asked to present a certificate. This step is optional to access the website, but is necessary to access the API.

Two certificates are provided for this example. The password is "12345678". To use these certificates, you must run the website on Firefox or a broswer than supports .pck12 files:

Client Certificates\Real_Client_Cert.pcks12 - A certificate signed by the CA and holds the correct private key. This will allow you to enter the website and the API.

Client Certificates\Client_Cert_Wrong_Private_Key.pcks12 - A certificate signed by the CA but does not hold the correct private key. This will deny you access to the website and API.

Presenting a certificate not signed by the root CA (backend\Certificates\root.pem) denies access to the website and API.

To use the API, visit https://127.0.0.1:5000/customers/Tx, where x is any number. Tx represents the transaction ID of the bank.##

### Man in the middle phishing attack
Code to stimlate the attack is in the file called 'MITM phishing attack'. 
To run the phishing website:  
                              `python phishing_app.py`
Run the legitmate app and phishing app on a local server so the flask apps are accessible in the Kali VM. 
To do that use:
                              `https://<ip-address-of-your-computer>:5002/`
The ip address of your computer can be found by opening the command prompt and entering: `ipconfig`
Your IP address should be the ip address under Wireless LAN adapter WiFi ->  IPv4 Address

### AI based Phishing URL scanner
The dataset used for training and testing the dataset: `https://data.mendeley.com/datasets/vfszbj9b36/1`
All files are under the Phishing URL Dectection folder
In the URL Dectecton folder contains:
- Trained Decision tree model: DT_model.ipynb
- Trained Logistic Regression model: LR model.ipynb
- Trained Random Forest model: ML model RF.ipynb
- Raw phishing dataset: Phishing URLs.csv (other dataset too large to be added to Github)
- Processed dataset: processed_dataset.csv


