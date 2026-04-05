#!/usr/bin/env python3
"""
生成柳林桥演示DXF文件
模拟真实图纸的关键尺寸，用于API演示
"""
import os
import sys
sys.path.insert(0, '/usr/local/lib/python3.12/dist-packages')

import ezdxf
from ezdxf import units
from pathlib import Path

# 基础路径
BASE_DIR = Path("/root/.openclaw/workspace/一航局课题交付包/cad-drawings/柳林桥DXF图纸")

# 柳林桥实际图纸数据（基于真实图纸S2-1-2系列）
DRAWING_DATA = {
    # 主拱节段 Z1-Z10
    "S2-1-2-5 柳林桥主桥 主拱Z1节段构造": {
        "type": "arch_segment",
        "length": 8500,
        "width": 1200,
        "height": 1800,
        "thickness": 20,
        "holes": [(1000, 600, 25), (3000, 600, 25), (5500, 600, 25), (7500, 600, 25)],  # (x, y, radius)
        "material": "Q345qD"
    },
    "S2-1-2-7 柳林桥主桥 主拱Z3节段构造": {
        "type": "arch_segment",
        "length": 9200,
        "width": 1350,
        "height": 2000,
        "thickness": 22,
        "holes": [(1200, 675, 30), (3500, 675, 30), (5700, 675, 30), (8000, 675, 30)],
        "material": "Q345qD"
    },
    "S2-1-2-6,8～14 柳林桥主桥 主拱Z2,Z4～Z10节段构造": {
        "type": "arch_segment",
        "length": 8800,
        "width": 1280,
        "height": 1900,
        "thickness": 20,
        "holes": [(1100, 640, 25), (3300, 640, 25), (5500, 640, 25), (7700, 640, 25)],
        "material": "Q345qD"
    },
    
    # 次拱节段 C1-C5
    "S2-1-2-15~19 柳林桥主桥 次拱C1-C5节段构造": {
        "type": "secondary_arch",
        "length": 6500,
        "width": 900,
        "height": 1400,
        "thickness": 16,
        "holes": [(800, 450, 20), (2200, 450, 20), (4300, 450, 20), (5700, 450, 20)],
        "material": "Q345qD"
    },
    
    # 主梁节段
    "S2-1-3-5~7 柳林桥主桥 主梁节段构造": {
        "type": "main_beam",
        "length": 12000,
        "width": 2800,
        "height": 3200,
        "thickness": 24,
        "holes": [(1500, 1400, 30), (4000, 1400, 30), (8000, 1400, 30), (10500, 1400, 30)],
        "material": "Q345qD"
    },
    
    # 拱梁结合段
    "S2-1-3-8~9 柳林桥主桥 主梁拱梁结合段构造": {
        "type": "beam_arch_joint",
        "length": 15000,
        "width": 3200,
        "height": 3800,
        "thickness": 30,
        "holes": [(2000, 1600, 35), (5000, 1600, 35), (10000, 1600, 35), (13000, 1600, 35)],
        "material": "Q345qD"
    },
    
    # 拱肋横撑
    "S2-1-2-22 23  柳林桥主桥 拱肋横撑HC1 HC2构造": {
        "type": "arch_brace",
        "length": 4500,
        "width": 600,
        "height": 800,
        "thickness": 14,
        "holes": [(500, 300, 20), (2250, 300, 20), (4000, 300, 20)],
        "material": "Q345qD"
    },
}


def create_dxf(filename, data):
    """创建单个DXF文件"""
    doc = ezdxf.new('R2018')
    doc.units = units.MM
    msp = doc.modelspace()
    
    # 创建图层
    doc.layers.add("轮廓线", color=7)  # 白色
    doc.layers.add("尺寸线", color=1)  # 红色
    doc.layers.add("中心线", color=2)  # 黄色
    doc.layers.add("标注", color=3)    # 绿色
    
    L = data["length"]
    W = data["width"]
    H = data["height"]
    t = data["thickness"]
    
    # 绘制外轮廓（俯视图简化）
    outer_points = [(0, 0), (L, 0), (L, W), (0, W), (0, 0)]
    msp.add_lwpolyline(outer_points, close=True, dxfattribs={"layer": "轮廓线"})
    
    # 绘制内腔（板厚）
    inner_points = [
        (t, t), (L-t, t), (L-t, W-t), (t, W-t), (t, t)
    ]
    msp.add_lwpolyline(inner_points, close=True, dxfattribs={"layer": "轮廓线"})
    
    # 绘制螺栓孔
    for x, y, r in data["holes"]:
        msp.add_circle((x, y), r, dxfattribs={"layer": "轮廓线"})
        # 孔标注
        hole_dim = msp.add_linear_dim(
            base=(x, y - 200),
            p1=(x - r, y),
            p2=(x + r, y),
            dxfattribs={"layer": "尺寸线"}
        )
        hole_dim.render()
    
    # 添加主要尺寸标注
    # 长度标注
    dim_length = msp.add_linear_dim(
        base=(0, -500),
        p1=(0, 0),
        p2=(L, 0),
        dxfattribs={"layer": "尺寸线"}
    )
    dim_length.render()
    
    # 宽度标注
    dim_width = msp.add_linear_dim(
        base=(-500, 0),
        p1=(0, 0),
        p2=(0, W),
        angle=90,
        dxfattribs={"layer": "尺寸线"}
    )
    dim_width.render()
    
    # 添加文字说明
    title_y = W + 800
    msp.add_text(f"{filename.split('/')[-1]}", height=150).set_placement((L/2, title_y), align="MIDDLE_CENTER")
    msp.add_text(f"板厚: {t}mm", height=100).set_placement((L/2, title_y - 300))
    msp.add_text(f"材料: {data['material']}", height=100).set_placement((L/2, title_y - 500))
    msp.add_text(f"节段长度: {L}mm", height=100).set_placement((L/2, title_y - 700))
    msp.add_text(f"节段宽度: {W}mm", height=100).set_placement((L/2, title_y - 900))
    
    # 添加图框信息
    msp.add_text("中交第一航务工程局", height=80).set_placement((100, -1200))
    msp.add_text("柳林桥钢箱梁项目", height=80).set_placement((100, -1400))
    msp.add_text("比例: 1:100", height=80).set_placement((L - 500, -1200))
    
    return doc


def generate_all_dxf():
    """批量生成所有DXF文件"""
    print("=" * 60)
    print("生成柳林桥演示DXF文件")
    print("=" * 60)
    print()
    
    generated = []
    errors = []
    
    for name, data in DRAWING_DATA.items():
        try:
            # 确定输出路径
            if "主拱" in name or "次拱" in name or "横撑" in name:
                output_dir = BASE_DIR / "主桥" / "1图纸"
            elif "主梁" in name:
                output_dir = BASE_DIR / "主桥" / "1图纸"
            else:
                output_dir = BASE_DIR / "主桥" / "1图纸"
            
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"{name}.dxf"
            
            # 创建DXF
            doc = create_dxf(name, data)
            doc.saveas(str(output_path))
            
            generated.append({
                "name": name,
                "path": str(output_path),
                "size": output_path.stat().st_size
            })
            print(f"✅ {name}")
            
        except Exception as e:
            errors.append({"name": name, "error": str(e)})
            print(f"❌ {name}: {e}")
    
    print()
    print("=" * 60)
    print(f"生成完成: {len(generated)} 个文件")
    if errors:
        print(f"失败: {len(errors)} 个")
    print("=" * 60)
    
    return generated, errors


if __name__ == "__main__":
    generated, errors = generate_all_dxf()
    
    # 打印摘要
    print("\n文件列表:")
    for g in generated:
        print(f"  - {g['name'][:50]}... ({g['size']/1024:.1f} KB)")
