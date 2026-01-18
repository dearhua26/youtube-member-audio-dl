import re

log_file = r"d:\YouTube\audio\Vip\未下载成功.txt"
output_file = r"d:\YouTube\audio\Vip\failed_ids.txt"

with open(log_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern to capture the ID after "ERROR: [youtube] " and before ":"
pattern = r"ERROR: \[youtube\] ([a-zA-Z0-9_-]{11}):"
ids = re.findall(pattern, content)

# Remove duplicates while preserving order
unique_ids = list(dict.fromkeys(ids))

print(f"Found {len(unique_ids)} unique IDs.")

with open(output_file, 'w', encoding='utf-8') as f:
    for vid_id in unique_ids:
        f.write(f"https://www.youtube.com/watch?v={vid_id}\n")

print(f"Saved URLs to {output_file}")
