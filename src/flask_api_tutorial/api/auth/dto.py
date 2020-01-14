"""Parsers and serializers for /auth API endpoints."""
from flask_restplus import Model
from flask_restplus.fields import String, Boolean
from flask_restplus.inputs import email
from flask_restplus.reqparse import RequestParser


auth_reqparser = RequestParser(bundle_errors=True)
auth_reqparser.add_argument(
    name="email", type=email(), location="form", required=True, nullable=False
)
auth_reqparser.add_argument(
    name="password", type=str, location="form", required=True, nullable=False
)

user_model = Model(
    "User",
    {
        "email": String,
        "public_id": String,
        "admin": Boolean,
        "registered_on": String(attribute="registered_on_str"),
        "token_expires_in": String,
    },
)
