# model/__init__.py

# Import the Base object so that all models inherit from the same metadata
from db.base import Base

# Import all individual model files. 
# The act of importing these classes registers them with Base.metadata.
from .models import User


# Optional: Define __all__ for clean imports elsewhere in your app.
__all__ = [
    "Base",
    "User"
]