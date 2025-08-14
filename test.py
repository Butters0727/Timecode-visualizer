import subprocess, json

def get_timecode_ffprobe(path):
    cmd = ["ffprobe","-v","error",
           "-show_entries","format_tags=timecode",
           "-show_entries","stream=index,codec_type,codec_tag_string,codec_name,tags",
           "-of","json", path]
    out = subprocess.check_output(cmd, text=True)
    j = json.loads(out)

    # 1) format 级别
    tc = j.get("format",{}).get("tags",{}).get("timecode")
    if tc: return tc

    # 2) 流级别（视频/数据/tmcd）
    for s in j.get("streams",[]):
        tags = s.get("tags",{}) or {}
        if "timecode" in tags:
            return tags["timecode"]
        # 有些是 tmcd data 流
        if (s.get("codec_type")=="data" and 
            (s.get("codec_tag_string")=="tmcd" or s.get("codec_name")=="tmcd")):
            # 有的 tmcd 流的 timecode 也会放在 tags 里
            if "timecode" in tags:
                return tags["timecode"]
    return None

print(get_timecode_ffprobe("GX010183.MP4"))


