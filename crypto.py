from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from base64 import b64encode, b64decode


B_KEY = b"e3ded030ce294235047550b8f69f5a28"  # md5(b"hk.edu.cuhk.ClassTT").hexdigest().encode("utf-8")
B_IV = b"e0b2ea987a832e24"  # md5(b"www.cuhk.edu.hk").hexdigest()[8:24].encode("utf-8")


def encrypt(data: str):
    backend = default_backend()
    padder = padding.PKCS7(128).padder()

    b_data = data.encode("utf-8")
    b_data = padder.update(b_data) + padder.finalize()

    cipher = Cipher(algorithms.AES(B_KEY), modes.CBC(B_IV), backend=backend)
    encryptor = cipher.encryptor()
    ct = encryptor.update(b_data) + encryptor.finalize()
    ct_out = b64encode(ct).decode("utf-8")
    return ct_out


def decrypt(data: str):
    backend = default_backend()
    unpadder = padding.PKCS7(128).unpadder()

    b_data = b64decode(data)

    cipher = Cipher(algorithms.AES(B_KEY), modes.CBC(B_IV), backend=backend)
    decryptor = cipher.decryptor()
    plain = decryptor.update(b_data) + decryptor.finalize()
    plain = unpadder.update(plain) + unpadder.finalize()
    return plain.decode("utf-8")
