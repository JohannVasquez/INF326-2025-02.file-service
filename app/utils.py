import hashlib

def sha256_bytesio(file_like) -> tuple[str, int]:
    sha = hashlib.sha256()
    total = 0
    while True:
        chunk = file_like.read(1024 * 1024)
        if not chunk:
            break
        sha.update(chunk)
        total += len(chunk)
    return sha.hexdigest(), total
