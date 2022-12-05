def get_file_lines(path: str) -> int:

  def blocks(files, size = 65536):
    while True:
      b = files.read(size)
      if not b: break
      yield b

  ans = 0
  with open(path, 'r', encoding = 'utf-8', errors = 'ignore') as f:
    for b in blocks(f):
      ans += b.count('\n')

  return ans
