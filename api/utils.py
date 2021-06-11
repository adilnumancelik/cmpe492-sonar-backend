from django.contrib.auth import authenticate
import json
import jwt
import requests
import os

def jwt_get_username_from_payload_handler(payload):
    username = payload.get('sub').replace('|', '.')
    authenticate(remote_user=username)
    return username

def jwt_decode_token(token):
    header = jwt.get_unverified_header(token)
    jwks = requests.get('https://{}/.well-known/jwks.json'.format(os.environ.get('JWR_ISSUER_FORMAT'))).json()
    public_key = None
    for jwk in jwks['keys']:
        if jwk['kid'] == header['kid']:
            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))

    if public_key is None:
        raise Exception('Public key not found.')

    issuer = 'https://{}/'.format(os.environ.get('JWR_ISSUER_FORMAT'))
    return jwt.decode(token, public_key, audience=os.environ.get('JWT_AUDIENCE'), issuer=issuer, algorithms=['RS256'])