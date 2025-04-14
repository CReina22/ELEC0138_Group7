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
