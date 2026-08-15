"""Paper-derived reproduction of the 3DSFF color-image encryption scheme."""

from .config import CipherConfig, LMMParameters
from .cipher import decrypt_array, encrypt_array
from .key_schedule import KeyMaterial

__version__ = "0.1.0"

__all__ = ["CipherConfig", "LMMParameters", "KeyMaterial", "encrypt_array", "decrypt_array"]
