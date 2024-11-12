import subprocess
import os

def upscale_video(input_file, resolution):
    """
    Upscale video to specified resolution
    """
    output_file = f'output_{resolution}p.mp4'
    
    # Different scaling algorithms for better upscaling
    if resolution > 720:
        # Use lanczos scaling for higher resolutions
        scale_algorithm = "lanczos"
    else:
        # Use bicubic scaling for moderate upscaling
        scale_algorithm = "bicubic"
    
    cmd = [
        'ffmpeg', '-i', input_file,
        '-vf', f'scale=-2:{resolution}:flags={scale_algorithm}',
        '-c:v', 'libx264',
        '-crf', '18',  # Higher quality setting
        '-preset', 'slow',  # Slower encoding for better quality
        '-c:a', 'aac',
        '-b:a', '192k',
        output_file
    ]
    
    subprocess.run(cmd)
    print(f"Created {output_file}")

def enhance_upscaled_video(input_file, resolution):
    """
    Upscale with additional enhancement filters
    """
    output_file = f'output_{resolution}p_enhanced.mp4'
    
    # Complex filter chain for better upscaling
    filter_chain = [
        f"scale=-2:{resolution}:flags=lanczos",  # Initial scaling
        "unsharp=3:3:1.5:3:3:0.5",  # Sharpen
        "pp=al",  # Deblocking
        "hqdn3d=1.5:1.5:6:6",  # Denoise
    ]
    
    cmd = [
        'ffmpeg', '-i', input_file,
        '-vf', ','.join(filter_chain),
        '-c:v', 'libx264',
        '-crf', '18',
        '-preset', 'slow',
        '-c:a', 'aac',
        '-b:a', '192k',
        output_file
    ]
    
    subprocess.run(cmd)
    print(f"Created enhanced {output_file}")

def main():
    input_file = 'one.mp4'  # Your 480p video
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found!")
        return
    
    # Get input video resolution
    cmd = [
        'ffprobe', 
        '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=height',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        input_file
    ]
    
    input_height = int(subprocess.check_output(cmd).decode().strip())
    print(f"Input video height: {input_height}p")
    
    if input_height < 480:
        print("Warning: Input video is below 480p!")
    
    # List of target resolutions
    resolutions = [720, 1080, 1440, 2160]  # 720p, 1080p, 2K, 4K
    
    print("Starting video upscaling...")
    
    for res in resolutions:
        if res > input_height:
            print(f"\nUpscaling to {res}p...")
            upscale_video(input_file, res)
            
            # Optional: Create enhanced version
            # print(f"Creating enhanced {res}p version...")
            # enhance_upscaled_video(input_file, res)

if __name__ == "__main__":
    main()