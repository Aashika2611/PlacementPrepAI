import re

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def is_valid_email(email):
    return bool(email) and bool(EMAIL_REGEX.match(email.strip()))


def is_valid_password(password):
    """Require at least 8 characters, one letter and one number."""
    if not password or len(password) < 8:
        return False
    has_letter = any(c.isalpha() for c in password)
    has_digit = any(c.isdigit() for c in password)
    return has_letter and has_digit


def require_fields(data, fields):
    """Return a list of missing/empty required fields from a request body."""
    missing = []
    for field in fields:
        value = data.get(field) if data else None
        if value is None or (isinstance(value, str) and not value.strip()):
            missing.append(field)
    return missing
