import os

from job_seach import qian_cheng_wu_you


# 初始化缓存目录
def init_dir():
    default_save_path = "./save"
    default_cache_path = "./cache"
    if not os.path.exists(default_save_path):
        os.makedirs(default_save_path)
    if not os.path.exists(default_cache_path):
        os.makedirs(default_cache_path)


if __name__ == '__main__':
    # 主关键字
    keyword = "python"
    init_dir()

    qc = qian_cheng_wu_you.QCheng(keyword, "01", "03", "030200")
    qc.do_it()
