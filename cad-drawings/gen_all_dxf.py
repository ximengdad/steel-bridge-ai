import sys
sys.path.insert(0, '/usr/local/lib/python3.12/dist-packages')
import ezdxf
from ezdxf import units
from pathlib import Path
import traceback

BASE_DIR = Path("/root/.openclaw/workspace/一航局课题交付包/cad-drawings/柳林桥DXF图纸")

def create_dxf(name, length, width, thickness, holes, subdir="主桥/1图纸"):
    try:
        doc = ezdxf.new('R2018')
        doc.units = units.MM
        msp = doc.modelspace()
        doc.layers.add("轮廓线", color=7)
        doc.layers.add("标注", color=3)
        
        L, W, t = length, width, thickness
        
        # 外轮廓
        points = [(0, 0), (L, 0), (L, W), (0, W), (0, 0)]
        msp.add_lwpolyline(points, close=True, dxfattribs={"layer": "轮廓线"})
        
        # 内腔
        inner = [(t, t), (L-t, t), (L-t, W-t), (t, W-t), (t, t)]
        msp.add_lwpolyline(inner, close=True, dxfattribs={"layer": "轮廓线"})
        
        # 孔
        for x, y, r in holes:
            msp.add_circle((x, y), r, dxfattribs={"layer": "轮廓线"})
        
        # 文字标注 - 使用兼容写法
        text = msp.add_text(f"{name}", height=min(150, L/50))
        text.dxf.insert = (L/2, W+500)
        text.dxf.halign = ezdxf.const.MTEXT_MIDDLE_CENTER
        
        text2 = msp.add_text(f"长度: {L}mm", height=100)
        text2.dxf.insert = (L/2, W+300)
        
        text3 = msp.add_text(f"宽度: {W}mm", height=100)
        text3.dxf.insert = (L/2, W+100)
        
        text4 = msp.add_text(f"板厚: {t}mm", height=100)
        text4.dxf.insert = (L/2, -300)
        
        text5 = msp.add_text(f"材料: Q345qD", height=100)
        text5.dxf.insert = (L/2, -500)
        
        text6 = msp.add_text(f"螺栓孔: {len(holes)}个, 直径{holes[0][2]*2}mm", height=100)
        text6.dxf.insert = (L/2, -700)
        
        # 保存
        parts = subdir.split('/')
        output_dir = BASE_DIR
        for p in parts:
            output_dir = output_dir / p
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f"{name}.dxf"
        doc.saveas(str(output_file))
        
        size = output_file.stat().st_size / 1024
        return True, f"✅ {name} ({size:.1f} KB)"
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        return False, f"❌ {name}: {str(e)}\n{error_detail[:200]}"

# 批量创建
print("=" * 60)
print("生成柳林桥演示DXF文件")
print("=" * 60)
print()

drawings = [
    ("S2-1-2-5 柳林桥主桥 主拱Z1节段构造", 8500, 1200, 20, [(1000, 600, 25), (3000, 600, 25), (5500, 600, 25), (7500, 600, 25)]),
    ("S2-1-2-7 柳林桥主桥 主拱Z3节段构造", 9200, 1350, 22, [(1200, 675, 30), (3500, 675, 30), (5700, 675, 30), (8000, 675, 30)]),
    ("S2-1-2-6 柳林桥主桥 主拱Z2节段构造", 8800, 1280, 20, [(1100, 640, 25), (3300, 640, 25), (5500, 640, 25), (7700, 640, 25)]),
    ("S2-1-2-15 柳林桥主桥 次拱C1节段构造", 6500, 900, 16, [(800, 450, 20), (2200, 450, 20), (4300, 450, 20), (5700, 450, 20)]),
    ("S2-1-3-5 柳林桥主桥 主梁节段构造", 12000, 2800, 24, [(1500, 1400, 30), (4000, 1400, 30), (8000, 1400, 30), (10500, 1400, 30)]),
    ("S2-1-3-8 柳林桥主桥 主梁拱梁结合段构造", 15000, 3200, 30, [(2000, 1600, 35), (5000, 1600, 35), (10000, 1600, 35), (13000, 1600, 35)]),
    ("S2-1-2-22 柳林桥主桥 拱肋横撑HC1构造", 4500, 600, 14, [(500, 300, 20), (2250, 300, 20), (4000, 300, 20)]),
]

success_count = 0
for name, L, W, t, holes in drawings:
    success, msg = create_dxf(name, L, W, t, holes)
    print(msg)
    if success:
        success_count += 1

print()
print("=" * 60)
print(f"完成: {success_count}/{len(drawings)}")
print("=" * 60)
