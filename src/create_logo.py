#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from PIL import Image, ImageDraw, ImageFont

def create_logo():
    """Tạo logo đơn giản cho ứng dụng cờ tướng"""
    # Tạo hình ảnh mới với nền trắng
    img = Image.new('RGB', (400, 400), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Vẽ bàn cờ
    board_size = 300
    margin = 50
    
    # Vẽ khung bàn cờ
    draw.rectangle(
        [(margin, margin), (margin + board_size, margin + board_size)],
        outline=(0, 0, 0),
        width=2,
        fill=(238, 203, 173)  # Màu bàn cờ
    )
    
    # Vẽ các đường kẻ ngang và dọc
    cell_size = board_size // 9  # 9x10 bàn cờ
    
    # Đường ngang
    for i in range(10):
        y = margin + i * cell_size
        draw.line([(margin, y), (margin + board_size, y)], fill=(0, 0, 0), width=1)
    
    # Đường dọc
    for i in range(10):
        x = margin + i * cell_size
        draw.line([(x, margin), (x, margin + board_size)], fill=(0, 0, 0), width=1)
    
    # Vẽ sông
    river_y1 = margin + 4 * cell_size
    river_y2 = margin + 5 * cell_size
    draw.rectangle(
        [(margin, river_y1), (margin + board_size, river_y2)],
        fill=(220, 240, 255)
    )
    
    # Vẽ cung điện
    palace_width = 2 * cell_size
    
    # Cung điện trên
    palace_x = margin + 3 * cell_size
    palace_y = margin
    
    draw.line(
        [(palace_x, palace_y), (palace_x + palace_width, palace_y + palace_width)],
        fill=(0, 0, 0),
        width=1
    )
    
    draw.line(
        [(palace_x + palace_width, palace_y), (palace_x, palace_y + palace_width)],
        fill=(0, 0, 0),
        width=1
    )
    
    # Cung điện dưới
    palace_y = margin + board_size - palace_width
    
    draw.line(
        [(palace_x, palace_y), (palace_x + palace_width, palace_y + palace_width)],
        fill=(0, 0, 0),
        width=1
    )
    
    draw.line(
        [(palace_x + palace_width, palace_y), (palace_x, palace_y + palace_width)],
        fill=(0, 0, 0),
        width=1
    )
    
    # Vẽ một vài quân cờ
    # Tướng đỏ
    red_x = margin + 4 * cell_size
    red_y = margin + 9 * cell_size
    
    draw.ellipse(
        [(red_x - cell_size//2 + 5, red_y - cell_size//2 + 5),
         (red_x + cell_size//2 - 5, red_y + cell_size//2 - 5)],
        fill=(255, 50, 50),
        outline=(0, 0, 0),
        width=1
    )
    
    # Tướng đen
    black_x = margin + 4 * cell_size
    black_y = margin + 0 * cell_size
    
    draw.ellipse(
        [(black_x - cell_size//2 + 5, black_y - cell_size//2 + 5),
         (black_x + cell_size//2 - 5, black_y + cell_size//2 - 5)],
        fill=(20, 20, 20),
        outline=(0, 0, 0),
        width=1
    )
    
    # Lưu hình ảnh
    os.makedirs(os.path.join('resources', 'images'), exist_ok=True)
    logo_path = os.path.join('resources', 'images', 'logo.png')
    img.save(logo_path)
    print(f"Logo đã được tạo tại: {os.path.abspath(logo_path)}")

if __name__ == "__main__":
    create_logo() 