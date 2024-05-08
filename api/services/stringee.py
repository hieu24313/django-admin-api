import jwt
from datetime import datetime, timedelta

from core.settings import STRINGEE_APP_ID, STRINGEE_APP_SECRET


def get_access_token(user_id):
    now = datetime.utcnow()
    exp = now + timedelta(days=30)

    header = {"cty": "stringee-api;v=1"}
    payload = {
        "jti": f"{STRINGEE_APP_ID}-{int(now.timestamp())}",
        "iss": STRINGEE_APP_ID,
        "exp": exp,
        "userId": user_id
    }

    token = jwt.encode(payload, STRINGEE_APP_SECRET, algorithm='HS256', headers=header)
    return token, exp
