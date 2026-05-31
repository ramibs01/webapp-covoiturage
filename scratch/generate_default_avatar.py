from PIL import Image, ImageDraw

# Create a 256x256 image with light slate background
img = Image.new('RGBA', (256, 256), color=(241, 245, 249, 255)) # slate-100
draw = ImageDraw.Draw(img)

# Draw head silhouette (circle)
# center=(128, 90), radius=45
draw.ellipse([83, 45, 173, 135], fill=(148, 163, 184, 255)) # slate-400

# Draw body/shoulders silhouette (arc/chord)
# bounding box from x: 40 to 216, y: 155 to 295
draw.chord([40, 155, 216, 315], start=180, end=360, fill=(148, 163, 184, 255)) # slate-400

# Save image
img.save('static/images/default-avatar.png')
print("Default avatar generated at static/images/default-avatar.png")
