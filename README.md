# EarthRanger Map Server API
Python based flask application for hosting track data for the ER embeddable map

Using Zappa for deployment.

## Zappa Setting
The primary settings are configured the the following environment variables
~~~
"environment_variables": {
            "LOGIN_TOKEN": "<login token used by the map>",
            "ER_TOKEN": "<er server token, tied to the account with track data>",
            "SERVER_URL": "",
            "ER_HOST": "https://<er server address>",
            "SUBJECTS_BUCKET": "<s3 bucket name>"  //S3 bucket to store cached subject tracks
        }
~~~

### Server certificate
Follow the instructions in Zappa docs on settting up AWS certificate. The certificate arn is recorded in the zappa_settings.json. Also the "zappa certify" command installs the certificate.

## Setup for deployment
1. create a virtual environment on the deployment machine. From the root of this project execute the following commands
~~~~
python3.7 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
~~~~
2. Make a copy of zappa config file, zappa_settings.config so that we can add the site specific tokens and secrets. Do no check this into source control.
3. Rename the "prod" config to something identifiable in AWS Lambda. Prefer the sitename.
4. Update the config inserting secrets and tokens for the site
5. Deploy to AWS Lambda. This assumes you already have AWS command line access keys setup appropriately and you have permission to add a Lambda config on AWS
~~~~
zappa deploy <configname from step 3 above>
~~~~
6. Need to make updates to the config? do that and then
~~~~
zappa update <configname>
~~~~
7. Bring the zappa process down or remove it?
~~~~
zappa undeploy <configname>
~~~~
