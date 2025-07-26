#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Favicon Generator für BESS Simulation
Erstellt ein Batterie-Symbol mit "B" für BESS
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_bess_favicon():
    """Erstellt ein Favicon für die BESS Simulation"""
    
    # Favicon-Größen (Standard: 16x16, 32x32, 48x48)
    sizes = [16, 32, 48]
    
    for size in sizes:
        # Erstelle ein neues Bild mit transparentem Hintergrund
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Berechne Proportionen basierend auf Größe
        padding = max(1, size // 8)
        battery_width = size - (2 * padding)
        battery_height = size - (2 * padding)
        
        # Batterie-Form zeichnen
        # Hauptkörper der Batterie
        battery_rect = [
            padding, 
            padding + (battery_height // 4), 
            padding + battery_width - (battery_width // 6), 
            padding + battery_height - (battery_height // 4)
        ]
        
        # Batterie-Körper (grün)
        draw.rectangle(battery_rect, fill=(34, 197, 94, 255), outline=(22, 163, 74, 255), width=1)
        
        # Batterie-Pol (kleiner rechteckiger Bereich rechts)
        pole_width = battery_width // 6
        pole_rect = [
            padding + battery_width - pole_width,
            padding + (battery_height // 3),
            padding + battery_width,
            padding + battery_height - (battery_height // 3)
        ]
        draw.rectangle(pole_rect, fill=(22, 163, 74, 255))
        
        # Batterie-Ladestand (3 Striche)
        charge_width = (battery_width - pole_width - (2 * padding)) // 4
        charge_height = battery_height // 6
        
        for i in range(3):
            charge_x = padding + (i + 1) * charge_width
            charge_y = padding + (battery_height // 2) - (charge_height // 2)
            charge_rect = [charge_x, charge_y, charge_x + (charge_width // 2), charge_y + charge_height]
            draw.rectangle(charge_rect, fill=(255, 255, 255, 200))
        
        # "B" Buchstabe in der Mitte (nur bei größeren Größen)
        if size >= 32:
            try:
                # Versuche eine Standard-Schriftart zu verwenden
                font_size = max(8, size // 4)
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                # Fallback auf Standard-Schriftart
                font = ImageFont.load_default()
            
            # "B" Text zentriert platzieren
            text = "B"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            text_x = (size - text_width) // 2
            text_y = (size - text_height) // 2
            
            # Weißer Text mit schwarzem Rand für bessere Sichtbarkeit
            draw.text((text_x+1, text_y+1), text, fill=(0, 0, 0, 100), font=font)
            draw.text((text_x, text_y), text, fill=(255, 255, 255, 255), font=font)
        
        # Speichere das Favicon
        filename = f"app/static/favicon-{size}x{size}.png"
        img.save(filename, "PNG")
        print(f"✅ Favicon {size}x{size} erstellt: {filename}")
    
    # Erstelle auch eine .ico Datei (16x16)
    img_16 = Image.open("app/static/favicon-16x16.png")
    img_16.save("app/static/favicon.ico", format="ICO", sizes=[(16, 16)])
    print("✅ Favicon.ico erstellt: app/static/favicon.ico")

if __name__ == "__main__":
    print("🎨 Erstelle Favicon für BESS Simulation...")
    create_bess_favicon()
    print("🎉 Favicon-Erstellung abgeschlossen!") 