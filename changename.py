import os

def add_prefix_to_files(folder_path, prefix="a"):
    files = os.listdir(folder_path)
    for filename in files:
        old_path = os.path.join(folder_path, filename)
        if os.path.isfile(old_path):
            new_name = prefix + filename
            new_path = os.path.join(folder_path, new_name)
            os.rename(old_path, new_path)
            print(f"重命名: {filename} → {new_name}")

if __name__ == "__main__":
    folder = r"D:\桌面\百度小车\image_set2\image_set2"  # 改成你的文件夹路径
    add_prefix_to_files(folder, prefix="a")
