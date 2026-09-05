import os, re, shutil
base = r'C:\Users\Bola\Documents\Shack_Project\Data\deals'
for folder in ('outputs', 'packs'):
    d = os.path.join(base, folder)
    for fn in list(os.listdir(d)):
        p = os.path.join(d, fn)
        if not os.path.isfile(p):
            continue
        m = re.match(r'(DEAL-[A-Z0-9]+)_S\d', fn)
        if not m:
            continue
        sub = os.path.join(d, m.group(1))
        os.makedirs(sub, exist_ok=True)
        shutil.move(p, os.path.join(sub, fn))
    print(folder, 'tidied')