import uuid


def generate_tracking_id():
    """Generates a unique tracking ID for orders."""
    return str(uuid.uuid4()).replace("-", "")[:25]  # Ensures uniqueness and fits within 25 characters
