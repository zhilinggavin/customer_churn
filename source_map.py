"""
AI in Education Policies – Global Map (Whitepaper Style)

Requirements:
    pip install pandas matplotlib geopandas
"""

import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd

# ========== 1. Load your data ==========

# 替换为你的实际文件名 / 路径
excel_path = "Worksheet in AI for Science in Education.xlsx"

df = pd.read_excel(excel_path)

# 这里假设你的列名为：
#   区域, 国家/组织, 项目名称, 政策层级, 来源机构, 执行平台, 链接, 总结
# 如果有变化，在这里修改列名即可
country_col = "国家/组织"

# 统计每个国家 / 组织出现的政策数量，用于节点大小
label_counts = df[country_col].value_counts()

# ========== 2. Define approximate coordinates for each label ==========

coords = {
    "UNESCO": (2.3, 48.85),                  # Paris
    "OECD": (2.3, 48.85),                    # Paris
    "EU": (4.35, 50.85),                     # Brussels
    "USA": (-98, 39),
    "Canada": (-106, 56),
    "Google": (-122.08, 37.42),              # California
    "Microsoft": (-122.13, 47.64),           # Redmond
    "Microsoft / IDC": (-122.13, 47.64),
    "APEC": (103.85, 1.3),                   # Singapore (APEC secretariat)
    "World Bank": (-77.04, 38.9),            # Washington, DC
    "Brookings": (-77.04, 38.9),             # Washington, DC
    "Germany": (10, 51),
    "France": (2, 46),
    "Finland": (25, 65),
    "Sweden": (15, 62),
    "Denmark": (10, 56),
    "Estonia": (25, 58),
    "Netherlands": (5, 52),
    "Ireland": (-8, 53),
    "Spain": (-3, 40),
    "Austria": (14, 47),
    "Central & Eastern Europe": (20, 50),    # stylised regional point
    "Australia": (134, -25),
    "South Korea": (127, 36),
    "Singapore": (104, 1.3),
    "UKRI": (-1, 52),
    "UK Parliament": (-0.13, 51.5),
    "The Alan Turing Institute": (-0.13, 51.5),
    "STEM Learning": (-1.1, 54),
    # 如果你有“教育部”这样模糊的条目，可以按实际情况改成对应国家
    "教育部": (116.4, 39.9),                 # placeholder: Beijing
}

# ========== 3. Load a world basemap (GeoPandas) ==========

world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))

# ========== 4. Plot – Whitepaper style ==========

fig, ax = plt.subplots(figsize=(12, 6))

# 1) 世界地图底图（简洁、白皮书风格）
world.plot(ax=ax, edgecolor="black", linewidth=0.5, facecolor="white")

# 2) 在地图上叠加节点
for label, count in label_counts.items():
    if label not in coords:
        # 如果某条没有预定义坐标，可以选择跳过或者打印提示
        # print(f"Missing coords for: {label}")
        continue
    x, y = coords[label]
    # 节点大小与政策数量成比例，你可以按需要调整缩放系数
    size = 60 * count
    ax.scatter(x, y, s=size)

    # 标签简短一点，避免太乱；B 风格一般只写名字，不写数量
    ax.text(x, y, label,
            fontsize=7,
            ha="center",
            va="center")

# 3) 版式美化：去掉坐标轴，设置范围
ax.set_title("AI in Education Policies – Global Map (Whitepaper Style)", fontsize=14)
ax.set_xlim(-140, 150)
ax.set_ylim(-55, 75)
ax.axis("off")

fig.tight_layout()

# 4) 保存图像
plt.savefig("ai_education_global_map_whitepaper.png", dpi=300)
plt.show()