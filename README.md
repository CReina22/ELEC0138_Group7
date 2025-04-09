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


### Anomaly Detection by Fingerprinting
To enable this feature ensure the variable FINGERPRINTING is set to true in app.py. 

Then log in across multiple devices that are commonly used with one holdout. 

The first 5 logins do not perform anomaly detection to build a profile of the user. After this the ML model will look for anomalies in the sign in and reject anomalous ones. There is currently no mechanism such as 
a OTP to allow the user to login once classed as an anomaly on device.

To clear the existing fingerprints of the account run in the terminal:
                'python fingerprint_clear.py'