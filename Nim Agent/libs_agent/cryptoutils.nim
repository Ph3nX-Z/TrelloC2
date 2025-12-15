import strutils,sequtils

proc xor_encrypt_decrypt(data: seq[byte], key: seq[byte]): seq[byte] =
  result = newSeq[byte](data.len)
  for i, b in data:
    result[i] = b xor key[i mod key.len]

when isMainModule:
  var plaintext = "hello world"
  var key = "mykey"

  var cipher = xorEncryptDecrypt(cast[seq[byte]](plaintext), cast[seq[byte]](key))
  echo "Cipher (hex): ", cipher.mapIt(it.toHex(2)).join("")

  let decrypted = xorEncryptDecrypt(cipher, cast[seq[byte]](key))
  echo "Decrypted: ", cast[string](decrypted)
