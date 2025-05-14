from cryptography.fernet import Fernet
key_bytes = Fernet.generate_key()
key_string = key_bytes.decode()
print(f"Sua nova SECRET_KEY (copie esta string): {key_string}")
