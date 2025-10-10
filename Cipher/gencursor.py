import os
from pathlib import Path
import subprocess
import shutil
from PIL import Image, ImageDraw
import math

def create_multisize_cursor_config(cursors_dir, cursor_name, image_file, sizes=[16, 24, 32, 48, 64]):
    """
    Create cursor configuration with multiple sizes for better scaling
    """
    config_file = cursors_dir / f"{cursor_name}.cursor"
    
    config_content = f"# {cursor_name} cursor - Multi-size version\n"
    
    for size in sizes:
        # Calculate hotspot (center for most cursors)
        hotspot_x = size // 2
        hotspot_y = size // 2
        
        # Special hotspot adjustments for specific cursors
        if cursor_name in ['left_ptr', 'arrow', 'default']:
            hotspot_x = 1  # Tip of arrow at left
            hotspot_y = 1
        elif cursor_name in ['hand2', 'hand', 'pointer']:
            hotspot_x = 8 * size // 32  # Finger tip
            hotspot_y = 1
        elif cursor_name in ['xterm', 'text', 'ibeam']:
            hotspot_x = size // 2
            hotspot_y = size // 2
        elif 'resize' in cursor_name or 'size' in cursor_name:
            hotspot_x = size // 2
            hotspot_y = size // 2
        elif cursor_name == 'crosshair':
            hotspot_x = size // 2
            hotspot_y = size // 2
        
        config_content += f"{size} {hotspot_x} {hotspot_y} {image_file} 100\n"
    
    with open(config_file, 'w') as f:
        f.write(config_content)
    
    print(f"  📐 {cursor_name} - sizes: {sizes}")

def create_scaled_images(original_image, cursor_name, output_dir, sizes=[16, 24, 32, 48, 64, 96, 128]):
    """
    Create scaled versions of the original image for different cursor sizes
    """
    scaled_images = {}
    
    try:
        with Image.open(original_image) as img:
            # Convert to RGBA if necessary
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            original_size = max(img.width, img.height)
            
            for size in sizes:
                # Calculate scale factor
                scale = size / original_size
                
                # Use high-quality resampling
                resized_img = img.resize((size, size), Image.Resampling.LANCZOS)
                
                # Save scaled image
                scaled_filename = f"{cursor_name}_{size}x{size}.png"
                scaled_path = output_dir / scaled_filename
                resized_img.save(scaled_path, 'PNG')
                
                scaled_images[size] = scaled_filename
                
    except Exception as e:
        print(f"  ⚠️  Could not scale {original_image}: {e}")
        # Fallback: use original for all sizes
        for size in sizes:
            scaled_images[size] = original_image.name
    
    return scaled_images

def create_optimized_multisize_config(cursors_dir, cursor_name, original_image, sizes=[16, 24, 32, 48, 64, 96, 128]):
    """
    Create optimized multi-size configuration with properly scaled images
    """
    config_file = cursors_dir / f"{cursor_name}.cursor"
    
    # Create scaled images
    scaled_images = create_scaled_images(original_image, cursor_name, cursors_dir, sizes)
    
    config_content = f"# {cursor_name} cursor - Optimized multi-size\n"
    
    for size in sizes:
        image_file = scaled_images.get(size, original_image.name)
        
        # Calculate dynamic hotspot based on cursor type and size
        hotspot_x, hotspot_y = calculate_hotspot(cursor_name, size)
        
        config_content += f"{size} {hotspot_x} {hotspot_y} {image_file} 100\n"
    
    with open(config_file, 'w') as f:
        f.write(config_content)
    
    print(f"  🎯 {cursor_name} - optimized sizes: {sizes}")

def calculate_hotspot(cursor_name, size):
    """
    Calculate appropriate hotspot for different cursor types and sizes
    """
    # Default center hotspot
    hotspot_x = size // 2
    hotspot_y = size // 2
    
    # Arrow pointers - tip at top-left
    if cursor_name in ['left_ptr', 'arrow', 'default', 'right_ptr', 'top_left_arrow']:
        hotspot_x = max(1, size // 16)  # Very left for tip
        hotspot_y = max(1, size // 16)  # Very top for tip
    
    # Hand cursors - at finger tip
    elif cursor_name in ['hand2', 'hand', 'pointer', 'pointing_hand']:
        hotspot_x = max(1, size * 6 // 32)  # About 1/5 from left
        hotspot_y = max(1, size // 16)      # Very top
    
    # Text cursors - centered but slightly left
    elif cursor_name in ['xterm', 'text', 'ibeam']:
        hotspot_x = size // 2
        hotspot_y = size // 2
    
    # Cross cursors - exact center
    elif cursor_name in ['crosshair', 'cross', 'tcross', 'diamond_cross']:
        hotspot_x = size // 2
        hotspot_y = size // 2
    
    # Move cursor - center
    elif cursor_name in ['fleur', 'size_all', 'move']:
        hotspot_x = size // 2
        hotspot_y = size // 2
    
    # Resize cursors - various edge positions
    elif cursor_name in ['sb_h_double_arrow', 'size_hor', 'h-double-arrow', 'col-resize']:
        hotspot_x = size // 2
        hotspot_y = size // 2
    elif cursor_name in ['sb_v_double_arrow', 'size_ver', 'v_double_arrow', 'row-resize']:
        hotspot_x = size // 2
        hotspot_y = size // 2
    elif cursor_name in ['top_left_corner', 'nw-resize', 'size_fdiag']:
        hotspot_x = max(1, size // 8)
        hotspot_y = max(1, size // 8)
    elif cursor_name in ['top_right_corner', 'ne-resize', 'size_bdiag']:
        hotspot_x = size - max(1, size // 8)
        hotspot_y = max(1, size // 8)
    elif cursor_name in ['bottom_left_corner', 'sw-resize']:
        hotspot_x = max(1, size // 8)
        hotspot_y = size - max(1, size // 8)
    elif cursor_name in ['bottom_right_corner', 'se-resize']:
        hotspot_x = size - max(1, size // 8)
        hotspot_y = size - max(1, size // 8)
    
    # Wait cursors - center
    elif cursor_name in ['watch', 'wait', 'progress']:
        hotspot_x = size // 2
        hotspot_y = size // 2
    
    # Forbidden cursors - center
    elif cursor_name in ['forbidden', 'not_allowed', 'crossed_circle']:
        hotspot_x = size // 2
        hotspot_y = size // 2
    
    return hotspot_x, hotspot_y

def create_fullsize_cursor_theme(image_folder=".", theme_name="fullsize_cursors"):
    """
    Create full-size cursor theme with multiple sizes
    """
    
    # Standard cursor sizes for X11
    standard_sizes = [16, 24, 32, 48, 64, 96, 128]
    # Extended sizes for high-DPI displays
    extended_sizes = [16, 20, 24, 28, 32, 40, 48, 56, 64, 72, 80, 96, 112, 128]
    
    # Mapping từ file ảnh của bạn sang tên cursor X11
    image_to_cursor_map = {
        'pointer.png': 'left_ptr',
        'alternate.png': 'right_ptr',
        'help.png': 'question_arrow',
        'working.png': 'progress',
        'busy.png': 'wait',
        'link.png': 'hand2',
        'handwriting.png': 'pencil',
        'person.png': 'hand1',
        'cross.png': 'crosshair',
        'loc.png': 'cross',
        'horz.png': 'sb_h_double_arrow',
        'vert.png': 'sb_v_double_arrow',
        'dgn1.png': 'top_left_corner',
        'dgn2.png': 'top_right_corner',
        'move.png': 'fleur',
        'unavailable.png': 'forbidden'
    }
    
    # Create theme directory structure
    theme_dir = Path(theme_name)
    cursors_dir = theme_dir / "cursors"
    cursors_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"🎨 Creating FULL-SIZE cursor theme: {theme_name}")
    print(f"📐 Supported sizes: {standard_sizes}")
    
    # Get available images
    image_files = list(Path(image_folder).glob("*.png"))
    available_images = {img.name: img for img in image_files}
    
    # Create cursor configurations with multiple sizes
    for image_name, cursor_name in image_to_cursor_map.items():
        if image_name in available_images:
            original_image = available_images[image_name]
            create_optimized_multisize_config(cursors_dir, cursor_name, original_image, standard_sizes)
    
    # Create essential cursors with fallbacks
    create_fullsize_essential_cursors(cursors_dir, image_to_cursor_map, available_images, standard_sizes)
    
    # Create aliases
    create_fullsize_aliases(cursors_dir)
    
    # Create comprehensive theme index
    create_fullsize_theme_index(theme_dir, theme_name, standard_sizes)
    
    print(f"\n✅ Full-size theme structure created in: {theme_dir}")
    return theme_dir

def create_fullsize_essential_cursors(cursors_dir, cursor_map, available_images, sizes):
    """Create essential cursors with full-size support"""
    
    essential_cursors = {
        'default': 'left_ptr',
        'arrow': 'left_ptr',
        'text': 'xterm',
        'ibeam': 'xterm',
        'watch': 'wait',
        'half-busy': 'progress',
        'col-resize': 'sb_h_double_arrow',
        'row-resize': 'sb_v_double_arrow',
        'size_ver': 'sb_v_double_arrow',
        'size_hor': 'sb_h_double_arrow',
        'size_bdiag': 'top_right_corner',
        'size_fdiag': 'top_left_corner',
        'size_all': 'fleur',
        'n_resize': 'top_side',
        's_resize': 'bottom_side',
        'e_resize': 'right_side',
        'w_resize': 'left_side',
        'ne-resize': 'top_right_corner',
        'nw-resize': 'top_left_corner',
        'se-resize': 'bottom_right_corner',
        'sw-resize': 'bottom_left_corner',
        'hand': 'hand2',
        'pointing_hand': 'hand2',
        'openhand': 'hand1',
        'closedhand': 'hand1',
        'grab': 'hand1',
        'grabbing': 'hand1',
        'dnd-move': 'fleur',
        'dnd-none': 'forbidden',
        'dnd_no_drop': 'forbidden',
        'no_drop': 'forbidden',
        'not_allowed': 'forbidden',
        'whats_this': 'question_arrow',
        'crossed_circle': 'forbidden'
    }
    
    for cursor_name, fallback in essential_cursors.items():
        if cursor_name not in cursor_map:
            config_file = cursors_dir / f"{cursor_name}.cursor"
            if not config_file.exists():
                # Find appropriate image
                image_file = None
                if fallback in cursor_map and fallback in available_images:
                    image_file = available_images[cursor_map[fallback]]
                elif available_images:
                    image_file = list(available_images.values())[0]
                
                if image_file:
                    create_optimized_multisize_config(cursors_dir, cursor_name, image_file, sizes)

def create_fullsize_aliases(cursors_dir):
    """Create aliases for full-size theme"""
    
    alias_groups = [
        ['left_ptr', 'default', 'arrow', 'top_left_arrow'],
        ['xterm', 'text', 'ibeam'],
        ['hand2', 'hand', 'pointer', 'pointing_hand'],
        ['hand1', 'openhand', 'grab'],
        ['wait', 'watch'],
        ['progress', 'half-busy'],
        ['sb_h_double_arrow', 'size_hor', 'h-double-arrow', 'ew-resize', 'col-resize'],
        ['sb_v_double_arrow', 'size_ver', 'v_double_arrow', 'ns-resize', 'row-resize'],
        ['top_left_corner', 'size_fdiag', 'nw-resize', 'nwse-resize'],
        ['top_right_corner', 'size_bdiag', 'ne-resize', 'nesw-resize'],
        ['bottom_left_corner', 'sw-resize'],
        ['bottom_right_corner', 'se-resize'],
        ['fleur', 'size_all', 'move', 'all-scroll'],
        ['forbidden', 'not_allowed', 'no_drop', 'dnd-none', 'crossed_circle']
    ]
    
    for group in alias_groups:
        source_cursor = None
        for cursor in group:
            config_file = cursors_dir / f"{cursor}.cursor"
            if config_file.exists():
                source_cursor = cursor
                break
        
        if source_cursor:
            for alias in group:
                if alias != source_cursor:
                    alias_file = cursors_dir / f"{alias}.cursor"
                    if not alias_file.exists():
                        try:
                            alias_file.symlink_to(f"{source_cursor}.cursor")
                        except OSError:
                            shutil.copy2(cursors_dir / f"{source_cursor}.cursor", alias_file)

def create_fullsize_theme_index(theme_dir, theme_name, sizes):
    """Create comprehensive theme index with size information"""
    
    theme_content = f"""[Icon Theme]
Name={theme_name}
Name[en]={theme_name} - Full Size
Comment=High-quality X11 cursor theme with multiple sizes
Comment[en]=High-quality X11 cursor theme with multiple sizes for all display types
Inherits=core
Example=left_ptr

[Icon Theme Directory]
Size=24
Type=Fixed
Sizes={','.join(map(str, sizes))}
MinSize=16
MaxSize=128
Threshold=2

[Desktop Entry]
Type=X-Cursor-Theme
Name={theme_name}
Comment=Full-size cursor theme
X-KDE-FallbackTheme=core
"""

    with open(theme_dir / "index.theme", 'w') as f:
        f.write(theme_content)

def generate_fullsize_cursors(theme_dir):
    """Generate all cursor files with verbose output"""
    cursors_dir = Path(theme_dir) / "cursors"
    
    if not cursors_dir.exists():
        print(f"❌ Cursors directory not found: {cursors_dir}")
        return
    
    print(f"\n🔨 Generating FULL-SIZE cursor files...")
    print("⏳ This may take a while for high-resolution cursors...")
    
    successful = 0
    failed = 0
    
    # Get all cursor config files (excluding symlinks)
    config_files = [f for f in sorted(cursors_dir.glob("*.cursor")) if not f.is_symlink()]
    
    for i, config_file in enumerate(config_files, 1):
        cursor_name = config_file.stem
        output_file = cursors_dir / cursor_name
        
        # Progress indicator
        progress = f"[{i}/{len(config_files)}]"
        
        try:
            original_cwd = os.getcwd()
            os.chdir(cursors_dir)
            
            result = subprocess.run([
                'xcursorgen',
                config_file.name,
                cursor_name
            ], capture_output=True, text=True, timeout=30)
            
            os.chdir(original_cwd)
            
            if result.returncode == 0 and output_file.exists():
                # Get file size for information
                file_size = output_file.stat().st_size
                size_kb = file_size / 1024
                print(f"  {progress} ✅ {cursor_name:20} ({size_kb:5.1f} KB)")
                successful += 1
            else:
                print(f"  {progress} ❌ {cursor_name:20} - {result.stderr.strip()}")
                failed += 1
                
        except FileNotFoundError:
            print("❌ xcursorgen not found. Please install:")
            print("   Ubuntu/Debian: sudo apt-get install x11-apps")
            print("   Fedora: sudo dnf install xorg-x11-apps")
            print("   Arch: sudo pacman -S xorg-xcursorgen")
            break
        except subprocess.TimeoutExpired:
            print(f"  {progress} ⏰ {cursor_name:20} (timeout)")
            failed += 1
            os.chdir(original_cwd)
        except Exception as e:
            print(f"  {progress} 💥 {cursor_name:20} - {e}")
            failed += 1
            os.chdir(original_cwd)
    
    print(f"\n📊 Generation complete: {successful}✅ {failed}❌")
    
    # Show total theme size
    if successful > 0:
        total_size = sum(f.stat().st_size for f in cursors_dir.glob("*") if f.is_file() and not f.suffix == '.cursor')
        total_size_mb = total_size / (1024 * 1024)
        print(f"💾 Total theme size: {total_size_mb:.1f} MB")

def create_high_dpi_script(theme_dir):
    """Create script for high-DPI display optimization"""
    
    script_content = f"""#!/bin/bash
# High-DPI Cursor Configuration Script for {theme_dir}

echo "Configuring high-DPI cursor settings..."

# Set cursor size based on display scale
set_cursor_size() {{
    local scale=$1
    local base_size=24
    local new_size=$(echo "$base_size * $scale" | bc | cut -d. -f1)
    
    echo "Setting cursor size to $new_size (scale: $scale)"
    
    # X11 settings
    xsetroot -cursor_name left_ptr
    if command -v gsettings >/dev/null 2>&1; then
        gsettings set org.gnome.desktop.interface cursor-size $new_size
    fi
    
    # KDE settings
    if command -v kwriteconfig6 >/dev/null 2>&1; then
        kwriteconfig6 --file kcminputrc --group Mouse --key cursorSize $new_size
    fi
}}

# Detect display scale
detect_scale() {{
    if command -v xdpyinfo >/dev/null 2>&1; then
        local dpi=$(xdpyinfo | grep -oP 'resolution:\\s+\\K[0-9]+' | head -1)
        if [ -n "$dpi" ]; then
            local scale=$(echo "scale=1; $dpi / 96" | bc)
            echo $scale
        else
            echo "1.0"
        fi
    else
        echo "1.0"
    fi
}}

# Main execution
SCALE=$(detect_scale)
echo "Detected display scale: $SCALE"

if [ "$1" = "--auto" ]; then
    set_cursor_size $SCALE
elif [ -n "$1" ]; then
    set_cursor_size $1
else
    echo "Usage: $0 [--auto|SIZE]"
    echo "  --auto  : Set cursor size based on detected DPI"
    echo "  SIZE    : Set specific scale factor (e.g., 2.0 for 200%)"
    echo ""
    echo "Current theme supports sizes: 16, 24, 32, 48, 64, 96, 128"
fi

echo "Cursor theme: {theme_dir}"
echo "To manually set: export XCURSOR_THEME={theme_dir}"
"""

    script_file = theme_dir / "configure_hidpi.sh"
    with open(script_file, 'w') as f:
        f.write(script_content)
    
    script_file.chmod(0o755)
    print(f"📜 High-DPI script created: {script_file}")

# Main execution
if __name__ == "__main__":
    print("🎯 FULL-SIZE X11 Cursor Theme Generator")
    print("=" * 60)
    
    # Create full-size theme
    theme_dir = create_fullsize_cursor_theme(
        image_folder=".",
        theme_name="fullsize_pro_cursors"
    )
    
    # Generate cursor files
    response = input("\n🚀 Generate full-size cursor files? This may take a while (y/n): ").lower()
    if response in ['y', 'yes']:
        generate_fullsize_cursors(theme_dir)
    
    # Create high-DPI configuration script
    create_high_dpi_script(theme_dir)
    
    print(f"\n🎉 FULL-SIZE theme creation complete!")
    print(f"📁 Location: {theme_dir}")
    print(f"📐 Sizes: 16, 24, 32, 48, 64, 96, 128 pixels")
    print(f"🖥️  Run: ./{theme_dir}/configure_hidpi.sh --auto")