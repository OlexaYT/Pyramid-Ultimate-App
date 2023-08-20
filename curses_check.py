import os
path = r"C:\Users\tyler\OneDrive\Desktop\pyramid_ultimate_app\Pyramid-Ultimate-App\Resources"
subfolders = [ f.path for f in os.scandir(path) if f.is_dir() ]
no_curses = []
for folder in subfolders:
    flag = 0
    for f in os.listdir(folder):
        if f.startswith('c1'):
            flag = 1
        else:
            pass
    if flag == 0:
        no_curses.append(folder.split('\\')[-1])

for i in no_curses:
    print(i)