import subprocess
import os

def transcode_video(input_file, resolutions):
    for resolution in resolutions:
        output_file = f"output_{resolution}p.mp4"
        cmd = [
            'ffmpeg', '-i', input_file,
            '-vf', f'scale=-2:{resolution}',
            '-c:v', 'libx264',
            '-crf', '23',
            '-preset', 'medium',
            '-c:a', 'aac',
            '-b:a', '128k',
            output_file
        ]
        subprocess.run(cmd)
        print(f"Created {output_file}")

# def create_preview(input_file):
#     preview_file = 'preview.mp4'
#     cmd = [
#         'ffmpeg', '-i', input_file,
#         '-ss', '00:00:30',
#         '-t', '10',
#         '-vf', 'scale=-2:360',
#         '-c:v', 'libx264',
#         '-crf', '23',
#         '-preset', 'medium',
#         '-c:a', 'aac',
#         '-b:a', '64k',
#         preview_file
#     ]
#     subprocess.run(cmd)
#     print(f"Created {preview_file}")


def create_full_preview(input_file, duration_seconds=3, total_segments=10):
    """
    Creates a preview video with segments from throughout the video
    """
    # Get absolute path of input file
    input_file = os.path.abspath(input_file)
    
    # Get video duration
    duration_cmd = [
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1', input_file
    ]
    try:
        duration = float(subprocess.check_output(duration_cmd).decode().strip())
    except subprocess.CalledProcessError as e:
        print(f"Error getting video duration: {e}")
        return
    
    # Calculate segment positions
    interval = duration / (total_segments + 1)
    segment_files = []
    
    # Create temp directory in current working directory
    temp_dir = os.path.join(os.getcwd(), 'temp')
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        # Create segments
        for i in range(total_segments):
            start_time = interval * (i + 1)
            output_file = os.path.join(temp_dir, f'segment_{i}.mp4')
            segment_files.append(output_file)
            
            cmd = [
                'ffmpeg', '-i', input_file,
                '-ss', str(start_time),
                '-t', str(duration_seconds),
                '-vf', 'scale=-2:720',
                '-c:v', 'libx264',
                '-crf', '23',
                '-preset', 'fast',
                '-an',
                output_file
            ]
            print(f"Creating segment {i+1}/{total_segments}")
            subprocess.run(cmd, check=True)
        
        # Create file list for concatenation
        concat_file = os.path.join(temp_dir, 'files.txt')
        with open(concat_file, 'w') as f:
            for file in segment_files:
                # Use relative paths in the concat file
                relative_path = os.path.relpath(file, temp_dir)
                f.write(f"file '{relative_path}'\n")
        
        # Concatenate segments
        print("Concatenating segments...")
        concat_cmd = [
            'ffmpeg', '-f', 'concat',
            '-safe', '0',
            '-i', concat_file,
            '-c', 'copy',
            'preview.mp4'
        ]
        subprocess.run(concat_cmd, check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"Error during video processing: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        # Clean up temporary files
        print("Cleaning up temporary files...")
        try:
            for file in segment_files:
                if os.path.exists(file):
                    os.remove(file)
            if os.path.exists(concat_file):
                os.remove(concat_file)
            os.rmdir(temp_dir)
        except Exception as e:
            print(f"Error during cleanup: {e}")



def main():
    input_file = 'input.mp4'  # Change this to your video file name
    resolutions = [480, 720]  # Add or remove resolutions as needed
    
    # Create output directory
    os.makedirs('transcoded', exist_ok=True)
    os.makedirs('previews', exist_ok=True)
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found!")
        return
    
    # Transcode to different resolutions
    print("Starting video transcoding...")
    transcode_video(input_file, resolutions)
    
    # Create preview
    print("Creating preview...")
    create_full_preview(input_file)
    
    print("Processing complete!")

if __name__ == "__main__":
    main()