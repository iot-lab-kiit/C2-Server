import os
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

class AESCipher:
    """AES encryption/decryption utility"""
    
    def __init__(self, key=None):
        """Initialize with a key or generate a new one"""
        if key:
            
            self.key = key if isinstance(key, bytes) else key.encode()
        else:
            self.key = get_random_bytes(32)
            
        self.encoded_key = base64.b64encode(self.key).decode('utf-8')
    
    def encrypt(self, data):
        """Encrypt data using AES-CBC with a random IV"""
        if isinstance(data, str):
            data = data.encode('utf-8')
            
        iv = get_random_bytes(16)
        
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        encrypted_data = cipher.encrypt(pad(data, AES.block_size))
        
        result = iv + encrypted_data
        
        return base64.b64encode(result).decode('utf-8')
    
    def decrypt(self, encrypted_data):
        """Decrypt data using AES-CBC"""
        if isinstance(encrypted_data, str):
            encrypted_data = base64.b64decode(encrypted_data)
            
        iv = encrypted_data[:16]
        ciphertext = encrypted_data[16:]
        
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        decrypted_data = unpad(cipher.decrypt(ciphertext), AES.block_size)
        
        return decrypted_data.decode('utf-8')
    
    def get_key(self):
        """Return the base64 encoded key"""
        return self.encoded_key
    
    @classmethod
    def from_encoded_key(cls, encoded_key):
        """Create a cipher object from a base64 encoded key"""
        key = base64.b64decode(encoded_key)
        return cls(key)


def generate_key():
    """Generate a new AES key and return it base64 encoded"""
    cipher = AESCipher()
    return cipher.get_key()


def test_encryption():
    """Test the encryption/decryption functionality"""
    cipher = AESCipher()
    print(f"Generated Key: {cipher.get_key()}")
    
    original_data = "This is a test message for encryption!"
    
    encrypted = cipher.encrypt(original_data)
    print(f"Encrypted: {encrypted}")
    
    decrypted = cipher.decrypt(encrypted)
    print(f"Decrypted: {decrypted}")
    
    
    assert decrypted == original_data
    print("Encryption test passed!")


if __name__ == "__main__":
    test_encryption()