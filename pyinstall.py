import PyInstaller.__main__

PyInstaller.__main__.run([
    'main.py',
    '-i', 'assets\\icon.ico',
    '--onefile'
])
