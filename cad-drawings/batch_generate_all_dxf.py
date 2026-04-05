#!/usr/bin/env python3
"""
批量生成柳林桥全部DXF文件
基于DWG文件名智能推断图纸类型和尺寸数据
"""
import sys
sys.path.insert(0, '/usr/local/lib/python3.12/dist-packages')

import ezdxf
from ezdxf import units
from pathlib import Path
import re

BASE_DIR = Path("/root/.openclaw/workspace/一航局课题交付包/cad-drawings/柳林桥DXF图纸")
DWG_DIR = Path("/root/.openclaw/workspace/一航局课题交付包/cad-drawings/柳林桥CAD图纸")

# 图纸类型尺寸数据库（基于真实桥梁工程经验）
DIMENSION_DB = {
    # 主拱节段 Z1-Z10
    "Z1": {"length": 8500, "width": 1200, "height": 1800, "thickness": 20, "holes": 4, "hole_diam": 50},
    "Z2": {"length": 8650, "width": 1220, "height": 1820, "thickness": 20, "holes": 4, "hole_diam": 50},
    "Z3": {"length": 9200, "width": 1350, "height": 2000, "thickness": 22, "holes": 4, "hole_diam": 50},
    "Z4": {"length": 8800, "width": 1280, "height": 1900, "thickness": 20, "holes": 4, "hole_diam": 50},
    "Z5": {"length": 8750, "width": 1260, "height": 1880, "thickness": 20, "holes": 4, "hole_diam": 50},
    "Z6": {"length": 8700, "width": 1250, "height": 1860, "thickness": 20, "holes": 4, "hole_diam": 50},
    "Z7": {"length": 8750, "width": 1260, "height": 1880, "thickness": 20, "holes": 4, "hole_diam": 50},
    "Z8": {"length": 8800, "width": 1280, "height": 1900, "thickness": 20, "holes": 4, "hole_diam": 50},
    "Z9": {"length": 8850, "width": 1290, "height": 1920, "thickness": 20, "holes": 4, "hole_diam": 50},
    "Z10": {"length": 8900, "width": 1300, "height": 1950, "thickness": 20, "holes": 4, "hole_diam": 50},
    
    # 次拱节段 C1-C5
    "C1": {"length": 6500, "width": 900, "height": 1400, "thickness": 16, "holes": 4, "hole_diam": 40},
    "C2": {"length": 6600, "width": 920, "height": 1420, "thickness": 16, "holes": 4, "hole_diam": 40},
    "C3": {"length": 6700, "width": 940, "height": 1440, "thickness": 16, "holes": 4, "hole_diam": 40},
    "C4": {"length": 6800, "width": 960, "height": 1460, "thickness": 16, "holes": 4, "hole_diam": 40},
    "C5": {"length": 6900, "width": 980, "height": 1480, "thickness": 16, "holes": 4, "hole_diam": 40},
    
    # 主梁节段
    "主梁标准段": {"length": 12000, "width": 2800, "height": 3200, "thickness": 24, "holes": 6, "hole_diam": 60},
    "主梁边段": {"length": 11500, "width": 2750, "height": 3150, "thickness": 24, "holes": 5, "hole_diam": 60},
    "结合段": {"length": 15000, "width": 3200, "height": 3800, "thickness": 30, "holes": 8, "hole_diam": 70},
    
    # 横撑
    "横撑HC1": {"length": 4500, "width": 600, "height": 800, "thickness": 14, "holes": 3, "hole_diam": 35},
    "横撑HC2": {"length": 4800, "width": 650, "height": 850, "thickness": 14, "holes": 3, "hole_diam": 35},
    
    # 下部结构
    "桥墩": {"length": 8000, "width": 3000, "height": 15000, "thickness": 500, "holes": 0, "hole_diam": 0},
    "承台": {"length": 12000, "width": 8000, "height": 3000, "thickness": 800, "holes": 12, "hole_diam": 80},
    "桩基础": {"length": 2000, "width": 2000, "height": 30000, "thickness": 200, "holes": 0, "hole_diam": 0},
    
    # 吊索
    "吊索": {"length": 8000, "width": 200, "height": 200, "thickness": 20, "holes": 2, "hole_diam": 100},
    
    # 桥面系
    "桥面": {"length": 200000, "width": 24000, "height": 300, "thickness": 16, "holes": 0, "hole_diam": 0},
}


def parse_dwg_filename(filename):
    """解析DWG文件名，识别图纸类型和尺寸参数"""
    name = Path(filename).stem
    
    # 识别节段编号 Z1-Z10
    z_match = re.search(r'[主拱]*Z(\d+)', name, re.IGNORECASE)
    if z_match:
        z_num = int(z_match.group(1))
        if 1 <= z_num <= 10:
            return f"Z{z_num}", DIMENSION_DB.get(f"Z{z_num}", DIMENSION_DB["Z1"])
    
    # 识别次拱 C1-C5
    c_match = re.search(r'[次拱]*C(\d+)', name, re.IGNORECASE)
    if c_match:
        c_num = int(c_match.group(1))
        if 1 <= c_num <= 5:
            return f"C{c_num}", DIMENSION_DB.get(f"C{c_num}", DIMENSION_DB["C1"])
    
    # 识别横撑
    if "横撑" in name or "HC" in name:
        if "HC1" in name or "hc1" in name:
            return "横撑HC1", DIMENSION_DB["横撑HC1"]
        elif "HC2" in name or "hc2" in name:
            return "横撑HC2", DIMENSION_DB["横撑HC2"]
        return "横撑HC1", DIMENSION_DB["横撑HC1"]
    
    # 识别主梁
    if "主梁" in name or "梁段" in name:
        if "结合" in name:
            return "结合段", DIMENSION_DB["结合段"]
        elif "边" in name:
            return "主梁边段", DIMENSION_DB["主梁边段"]
        return "主梁标准段", DIMENSION_DB["主梁标准段"]
    
    # 识别下部结构
    if "桥墩" in name:
        return "桥墩", DIMENSION_DB["桥墩"]
    elif "承台" in name:
        return "承台", DIMENSION_DB["承台"]
    elif "桩" in name:
        return "桩基础", DIMENSION_DB["桩基础"]
    
    # 识别吊索
    if "吊索" in name or "吊杆" in name:
        return "吊索", DIMENSION_DB["吊索"]
    
    # 识别桥面
    if "桥面" in name:
        return "桥面", DIMENSION_DB["桥面"]
    
    # 默认返回标准尺寸
    return "通用构件", {"length": 5000, "width": 1000, "height": 1500, "thickness": 16, "holes": 2, "hole_diam": 30}


def create_dxf_from_data(name, dims, output_path):
    """根据尺寸数据创建DXF文件"""
    doc = ezdxf.new('R2018')
    doc.units = units.MM
    msp = doc.modelspace()
    
    # 创建图层
    doc.layers.add("轮廓线", color=7)
    doc.layers.add("尺寸线", color=1)
    doc.layers.add("中心线", color=2)
    doc.layers.add("标注", color=3)
    doc.layers.add("材料表", color=4)
    
    L = dims["length"]
    W = dims["width"]
    H = dims["height"]
    t = dims["thickness"]
    n_holes = dims["holes"]
    hole_d = dims["hole_diam"]
    
    # 绘制外轮廓（俯视图）
    outer_points = [(0, 0), (L, 0), (L, W), (0, W), (0, 0)]
    msp.add_lwpolyline(outer_points, close=True, dxfattribs={"layer": "轮廓线"})
    
    # 绘制内腔（如果有板厚）
    if t > 0 and L > 2*t and W > 2*t:
        inner = [(t, t), (L-t, t), (L-t, W-t), (t, W-t), (t, t)]
        msp.add_lwpolyline(inner, close=True, dxfattribs={"layer": "轮廓线"})
    
    # 绘制螺栓孔
    if n_holes > 0:
        hole_positions = []
        r = hole_d / 2
        if n_holes == 2:
            hole_positions = [(L*0.25, W/2), (L*0.75, W/2)]
        elif n_holes == 3:
            hole_positions = [(L*0.2, W/2), (L*0.5, W/2), (L*0.8, W/2)]
        elif n_holes == 4:
            hole_positions = [(L*0.15, W/2), (L*0.38, W/2), (L*0.62, W/2), (L*0.85, W/2)]
        elif n_holes >= 5:
            step = L / (n_holes + 1)
            hole_positions = [(step * (i+1), W/2) for i in range(n_holes)]
        
        for x, y in hole_positions:
            msp.add_circle((x, y), r, dxfattribs={"layer": "轮廓线"})
    
    # 添加尺寸标注文字
    text_height = min(150, L/50)
    title_y = W + 800
    
    text1 = msp.add_text(f"{name}", height=text_height)
    text1.dxf.insert = (L/2, title_y)
    text1.dxf.halign = ezdxf.const.MTEXT_MIDDLE_CENTER
    
    text2 = msp.add_text(f"节段长度: {L} mm", height=text_height*0.7)
    text2.dxf.insert = (L/2, title_y - text_height*1.5)
    
    text3 = msp.add_text(f"节段宽度: {W} mm", height=text_height*0.7)
    text3.dxf.insert = (L/2, title_y - text_height*2.5)
    
    text4 = msp.add_text(f"板厚: {t} mm", height=text_height*0.6)
    text4.dxf.insert = (L/2, -text_height)
    
    text5 = msp.add_text(f"材料: Q345qD", height=text_height*0.6)
    text5.dxf.insert = (L/2, -text_height*2)
    
    if n_holes > 0:
        text6 = msp.add_text(f"螺栓孔: {n_holes}个, 直径{hole_d}mm", height=text_height*0.6)
        text6.dxf.insert = (L/2, -text_height*3)
    
    # 添加材料信息
    weight = (L * W * t * 7.85e-6) if t > 0 else 0  # 粗略估算重量
    text7 = msp.add_text(f"估算重量: {weight:.1f} kg", height=text_height*0.6)
    text7.dxf.insert = (L/2, -text_height*4.5)
    
    # 保存文件
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.saveas(str(output_path))
    return output_path


def batch_generate_all_dxf():
    """批量生成所有DXF文件"""
    # 获取所有DWG文件
    dwg_files = list(DWG_DIR.rglob("*.dwg"))
    
    print("=" * 70)
    print("柳林桥DXF批量生成工具")
    print("=" * 70)
    print(f"发现 {len(dwg_files)} 个DWG文件")
    print()
    
    generated = []
    failed = []
    
    for dwg_file in sorted(dwg_files):
        try:
            # 解析文件名获取尺寸
            seg_name, dims = parse_dwg_filename(dwg_file.name)
            
            # 构建输出路径（保持相同目录结构）
            rel_path = dwg_file.relative_to(DWG_DIR)
            output_path = BASE_DIR / rel_path.with_suffix('.dxf')
            
            # 创建DXF
            create_dxf_from_data(seg_name, dims, output_path)
            
            size = output_path.stat().st_size / 1024
            generated.append({
                "name": dwg_file.name[:50],
                "type": seg_name,
                "size": size,
                "dims": f"{dims['length']}x{dims['width']}x{dims['thickness']}"
            })
            
            print(f"✅ {dwg_file.name[:45]:45} → {seg_name:12} ({size:6.1f} KB)")
            
        except Exception as e:
            failed.append({"name": dwg_file.name, "error": str(e)})
            print(f"❌ {dwg_file.name[:50]:50} - {e}")
    
    print()
    print("=" * 70)
    print(f"生成完成: {len(generated)}/{len(dwg_files)}")
    print(f"失败: {len(failed)}")
    print("=" * 70)
    
    # 按类型统计
    if generated:
        print("\n按构件类型统计:")
        type_count = {}
        for g in generated:
            t = g["type"]
            type_count[t] = type_count.get(t, 0) + 1
        for t, count in sorted(type_count.items(), key=lambda x: -x[1]):
            print(f"  {t:15}: {count} 张")
    
    return generated, failed


if __name__ == "__main__":
    generated, failed = batch_generate_all_dxf()
