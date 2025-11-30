import os

# 要合并的 Dart 文件目录
source_dir = "/Users/zhangxuefeng/AndroidStudioProjects/southgobipeimei/lib"
# 输出文件
output_file = "./merge.txt"

# 获取所有 Dart 文件路径，按字母排序
dart_files = []
for root, dirs, files in os.walk(source_dir):
    for file in files:
        if file.endswith(".dart"):
            dart_files.append(os.path.join(root, file))

dart_files.sort()  # 可按需求排序

with open(output_file, "w", encoding="utf-8") as outfile:
    for file_path in dart_files:
        file_name = os.path.basename(file_path)
        outfile.write(f"// {file_name}\n")
        with open(file_path, "r", encoding="utf-8") as infile:
            outfile.write(infile.read())
        outfile.write("\n\n")  # 文件之间空行分隔

print(f"合并完成，共 {len(dart_files)} 个 Dart 文件，输出到 {output_file}")