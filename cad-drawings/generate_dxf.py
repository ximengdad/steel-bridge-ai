#!/usr/bin/env python3
"""
生成柳林桥演示DXF文件（简化版）
"""
import sys
sys.path.insert(0, '/usr/local/lib/python3.12/dist-packages')

import ezdxf
from ezdxf import units
from pathlib import Path

BASE_DIR = Path("/root/.openclaw/workspace/一航局课题交付包/cad-drawings/柳林桥DXF图纸")

# 图纸数据
DRAWINGS = [
    ("主桥/1图纸/S2-1-2-5 柳林桥主桥 主拱Z1节段构造", 8500, 1200, 20, [
        (1000, 600, 25), (3000, 600, 25), (5500, 600, 25), (7500, 600, 25)
    ]),
    ("主桥/1图纸/S2-1-2-7 柳林桥主桥 主拱Z3节段构造", 9200, 1350, 22, [
        (1200, 675, 30), (3500, 675, 30), (5700, 675, 30), (8000, 675, 30)
    ]),
    ("主桥/1图纸/S2-1-2-6,8～14 柳林桥主桥 主拱Z2,Z4～Z10节段构造", 8800, 1280, 20, [
        (1100, 640, 25), (3300, 640, 25), (5500, 640, 25), (7700, 640, 25)
    ]),
    ("主桥/1图纸/S2-1-2-15~19 柳林桥主桥 次拱C1-C5节段构造", 6500, 900, 16, [
        (800, 450, 20), (2200, 450, 20), (4300, 450, 20), (5700, 450, 20)
    ]),
    ("主桥/1图纸/S2-1-3-5~7 柳林桥主桥 主梁节段构造", 12000, 2800, 24, [
        (1500, 1400, 30), (4000, 1400, 30), (8000, 1400, 30), (10500, 1400, 30)
    ]),
    ("主桥/1图纸/S2-1-3-8~9 柳林桥主桥 主梁拱梁结合段构造", 15000, 3200, 30, [
        (2000, 1600, 35), (5000, 1600, 35), (10000, 1600, 35), (13000, 1600, 35)
    ]),
    ("主桥/1图纸/S2-1-2-22 23  柳林桥主桥 拱肋横撑HC1 HC2构造", 4500, 600, 14, [
        (500, 300, 20), (2250, 300, 20), (4000, 300, 20)
    ]),
]


def create_dxf(filepath, length, width, thickness, holes):
    """创建DXF文件"""
    doc = ezdxf.new('R2018')
    doc.units = units.MM
    msp = doc.modelspace()
    
    # 图层
    doc.layers.add("轮廓线", color=7)
    doc.layers.add("标注", color=3)
    
    # 外轮廓
    points = [(0, 0), (length, 0), (length, width), (0, width), (0, 0)]
    msp.add_lwpolyline(points, close=True, dxfattribs={"layer": "轮廓线"})
    
    # 内腔
    t = thickness
    inner = [(t, t), (length-t, t), (length-t, width-t), (t, width-t), (t, t)]
    msp.add_lwpolyline(inner, close=True, dxfattribs={"layer": "轮廓线"})
    
    # 圆孔
    for x, y, r in holes:
        msp.add_circle((x, y), r, dxfattribs={"layer": "轮廓线"})
    
    # 文字标注
    name = filepath.split('/')[-1]
    msp.add_text(name, height=min(150, length/50)).set_placement((length/2, width + 500), align="MIDDLE_CENTER")
    msp.add_text(f"长度: {length}mm", height=100).set_placement((length/2, width + 300))
    msp.add_text(f"宽度: {width}mm", height=100).set_placement((length/2, width + 100))
    msp.add_text(f"板厚: {thickness}mm", height=100).set_placement((length/2, -300))
    msp.add_text(f"材料: Q345qD", height=100).set_placement((length/2, -500))
    msp.add_text(f"螺栓孔: {len(holes)}个, 直径{holes[0][2]*2}mm", height=100).set_placement((length/2, -700))
    
    # 保存
    full_path = BASE_DIR / f"{filepath}.dxf"
    full_path.parent.mkdir(parents=True, exist_ok=True)
    doc.saveas(str(full_path))
    return full_path


print("=" * 60)
print("生成柳林桥演示DXF文件")
print("=" * 60)
print()

generated = []
for filepath, length, width, thickness, holes in DRAWINGS:
    try:
        path = create_dxf(filepath, length, width, thickness, holes)
        size = path.stat().st_size / 1024
        generated.append((filepath.split('/')[-1], size))
        print(f"✅ {filepath.split('/')[-1][:40]}... ({size:.1f} KB)")
    except Exception as e:
        print(f"❌ {filepath}: {e}")

print()
print("=" * 60)
print(f"生成完成: {len(generated)} 个文件")
print("=" * 60)
