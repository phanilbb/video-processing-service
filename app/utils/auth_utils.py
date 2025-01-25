from app import auth

tokens = {
    'your_api_token': 'user1',
}

@auth.verify_token
def verify_token(token):
    if token in tokens:
        return tokens[token]
    return None
