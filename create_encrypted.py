import pyzipper

with pyzipper.AESZipFile('real_encrypted.zip', 'w', compression=pyzipper.ZIP_LZMA, encryption=pyzipper.WZ_AES) as zf:
    zf.setpassword(b'abc')
    zf.writestr('secret.txt', 'This is a secret message.')

print("Created real_encrypted.zip with password 'abc'")
