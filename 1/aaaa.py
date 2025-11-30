import base64

# 所有片段文件，按顺序排列
parts = [
    "part1.txt",
    "part2.txt",
    "part3.txt",
    "part4.txt",
    "part5.txt",
    "part6.txt",
    "part7.txt",
    "part8.txt",
    "part9.txt",
    "part10.txt",
    "part11.txt",
    "part12.txt",
    "part13.txt",
    "part14.txt",
    "part15.txt",
    "part16.txt",
    "part17.txt"
]

output_zip = "haoyun_peimei_hive_clone.zip"

with open(output_zip, "wb") as f_out:
    for part_file in parts:
        with open(part_file, "r") as f_in:
            data = f_in.read()
            f_out.write(base64.b64decode(data))

print(f"ZIP 文件生成完成: {output_zip}")