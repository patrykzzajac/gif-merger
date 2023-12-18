from PIL import Image

def get_frames(gif):
    """Extract frames and their durations from an animated GIF."""
    frames = []
    durations = []
    try:
        gif.seek(0)
        while True:
            frames.append(gif.copy())
            durations.append(gif.info.get('duration', 100))  # Default duration is 100ms
            gif.seek(gif.tell() + 1)
    except EOFError:
        pass
    return frames, durations

def resize_frames(frames, target_height):
    """Resize frames to a specific height while maintaining aspect ratio."""
    resized_frames = []
    for frame in frames:
        aspect_ratio = frame.width / frame.height
        new_width = int(target_height * aspect_ratio)
        resized_frames.append(frame.resize((new_width, target_height), Image.ANTIALIAS))
    return resized_frames

def merge_gifs_side_by_side(gif_paths, output_path):
    gifs = [Image.open(gif) for gif in gif_paths]
    all_frames_durations = [get_frames(gif) for gif in gifs]

    # Determine the uniform height
    uniform_height = min(frames[0].height for frames, _ in all_frames_durations)

    # Resize frames to have the same height
    resized_gifs = [resize_frames(frames, uniform_height) for frames, _ in all_frames_durations]

    # Create a set of all frame change times
    frame_change_times = set()
    for _, durations in all_frames_durations:
        time = 0
        for duration in durations:
            time += duration
            frame_change_times.add(time)

    # Sort the times
    sorted_times = sorted(frame_change_times)

    merged_frames = []
    for time in sorted_times:
        new_frame_pieces = []
        max_height = uniform_height

        for frames, durations in zip(resized_gifs, [durations for _, durations in all_frames_durations]):
            frame_time = 0
            for i, duration in enumerate(durations):
                frame_time += duration
                if frame_time >= time:
                    new_frame_pieces.append(frames[i])
                    break

        total_width = sum(frame.width for frame in new_frame_pieces)
        new_frame = Image.new('RGBA', (total_width, max_height))
        current_x = 0
        for frame in new_frame_pieces:
            new_frame.paste(frame, (current_x, 0))
            current_x += frame.width

        merged_frames.append(new_frame)

    # Save the frames as a new animated GIF with higher quality
    merged_frames[0].save(output_path, save_all=True, append_images=merged_frames[1:], loop=0, duration=sorted_times[0], optimize=False, quality=95)


# Example usage
gif_files = ['gif1.gif', 'gif2.gif']  # Add your file paths here
merge_gifs_side_by_side(gif_files, 'output.gif')