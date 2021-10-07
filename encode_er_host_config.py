import base64

with open("er_host_config.json", "rb") as fh:
    encoded = base64.b64encode(fh.read())
    print(encoded)