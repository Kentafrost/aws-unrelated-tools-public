# crop all mp4 video in the selected folder and save to the output folder
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.fx.Crop import Crop
from moviepy.video.fx.Resize import Resize
from tkinter import Tk, filedialog
import os
import know_coods
import json
import cv2


def select_folder():
    global selected_folder
    root = Tk()
    root.withdraw()  # Hide the root window
    selected_folder = filedialog.askdirectory()  # Show folder selection dialog
    root.destroy()  # Close the root window
    return selected_folder  


def save_coordinates(coords, folder_path):
    
    coords_file = os.path.join(folder_path, "crop_coordinates.json")
    coords_data = {
        "upper": coords[0],
        "lower": coords[1], 
        "left": coords[2],
        "right": coords[3]
    }
    with open(coords_file, 'w') as f:
        json.dump(coords_data, f, indent=2)
    print(f"saved the coordinates: {coords_file}")


def load_coordinates(folder_path):
    
    coords_file = os.path.join(folder_path, "crop_coordinates.json")
    if os.path.exists(coords_file):
        with open(coords_file, 'r') as f:
            coords_data = json.load(f)
        coords = (coords_data["upper"], coords_data["lower"], coords_data["left"], coords_data["right"])
        print(f"loaded saved coordinates: top={coords[0]}, bottom={coords[1]}, left={coords[2]}, right={coords[3]}")
        return coords
    return None


def adjust_coordinates(coords, video_path=None):
    
    upper, lower, left, right = coords
    print(f"\ncurrent target: upper={upper}, lower={lower}, left={left}, right={right}")
    print("Do you want to adjust the coordinates? (You can adjust up, down, left, right and preview)")
    
    while True:
        adjustment = input("\nSelect adjustment method:\n1. Adjust upper\n2. Adjust lower\n3. Adjust left\n4. Adjust right\n5. Show preview\n6. Show cropped result preview\n7. Done\nSelect (1-7): ")

        if adjustment == '1':
            offset = int(input("How much to move the upper coordinate? (Negative for up, positive for down): "))
            upper += offset
        elif adjustment == '2':
            offset = int(input("How much to move the lower coordinate? (Negative for up, positive for down): "))
            lower += offset
        elif adjustment == '3':
            offset = int(input("How much to move the left coordinate? (Negative for left, positive for right): "))
            left += offset
        elif adjustment == '4':
            offset = int(input("How much to move the right coordinate? (Negative for left, positive for right): "))
            right += offset
        elif adjustment == '5':
            if video_path:
                preview_crop_area(video_path, (upper, lower, left, right))
            else:
                print("path to video is not provided")
        elif adjustment == '6':
            if video_path:
                preview_cropped_result(video_path, (upper, lower, left, right))
            else:
                print("path to video is not provided")
        elif adjustment == '7':
            break
        else:
            print("Invalid selection. Please choose 1-7.")
            continue

        print(f"Adjusted coordinates: upper={upper}, lower={lower}, left={left}, right={right}")
        print(f"Crop size: {right-left}x{lower-upper}")

    return (upper, lower, left, right)


def preview_crop_area(video_path, coords):
    
    upper, lower, left, right = coords
    
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print("Failed to read video frame")
        return False
    
    preview_frame = frame.copy()
    cv2.rectangle(preview_frame, (left, upper), (right, lower), (0, 0, 255), 3)
    
    cv2.putText(preview_frame, f"Crop: ({left},{upper}) to ({right},{lower})", 
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.putText(preview_frame, f"Size: {right-left}x{lower-upper}", 
                (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.putText(preview_frame, "Press 'q' to close, 'c' to continue", 
                (10, frame.shape[0]-20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    height, width = preview_frame.shape[:2]
    if width > 1200: 
        scale = 1200 / width
        new_width = 1200
        new_height = int(height * scale)
        preview_frame = cv2.resize(preview_frame, (new_width, new_height))
    
    cv2.imshow("Crop Preview", preview_frame)

    print("\nPreview:")
    print("- The red rectangle indicates the crop area")
    print("- Press 'q' to close the preview")
    print("- Press 'c' to continue")

    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == ord('c'):
            break
    
    cv2.destroyAllWindows()
    return True

# make a preview of cropped result
def preview_cropped_result(video_path, coords, duration=5):

    upper, lower, left, right = coords
    
    try:
        video = VideoFileClip(video_path)
        preview_clip = video.subclipped(0, min(duration, video.duration))
        
        width = right - left
        height = lower - upper
        
        # Make width and height even
        if width % 2 != 0:
            width -= 1
            right = left + width
        if height % 2 != 0:
            height -= 1
            lower = upper + height
        
        cropped_preview = preview_clip.with_effects([Crop(x1=left, y1=upper, x2=right, y2=lower)])
        
        temp_preview = "temp_preview.mp4"
        cropped_preview.write_videofile(temp_preview, logger=None)

        print(f"\nPreview video created: {temp_preview}")
        print("Please check the preview (first {} seconds)".format(duration))

        # Play the preview video
        cap = cv2.VideoCapture(temp_preview)

        print("Playing preview... Press 'q' to stop")
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            cv2.imshow("Cropped Preview", frame)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        # 一時ファイルを削除
        if os.path.exists(temp_preview):
            os.remove(temp_preview)
            
        video.close()
        return True
        
    except Exception as e:
        print(f"Preview creation error: {e}")
        return False


def crop_video(input_path, output_path, upper, lower, left, right):
    print(f"Cropping video: {input_path} -> {output_path}")
    
    # print its video screenshot 
    # cv2.imshow("Video Screenshot", cv2.imread(input_path))
    
    # key = cv2.waitKey(1) & 0xFF
    # if key == ord("c"):
    #     cv2.destroyAllWindows()

    width = right - left
    height = lower - upper
    print("")
    print(f"Cropping to {width}x{height}")

    # chk = input("continue? (y/n): ")
    # if chk.lower() != 'y':
    #     print("Skipping this video.")
    #     return

    # Crop the video
    video = VideoFileClip(input_path)
    width = right - left
    height = lower - upper
    
    # Make width and height even
    if width % 2 != 0:
        width -= 1
        right = left + width
    if height % 2 != 0:
        height -= 1
        lower = upper + height

    cropped_video = video.with_effects([Crop(x1=left, y1=upper, x2=right, y2=lower)])
    cropped_video = cropped_video.with_effects([Resize((width, height))])
    cropped_video.write_videofile(
        output_path, 
        codec="libx264", 
        audio_codec="aac", 
        audio=True, 
        ffmpeg_params=[
            "-crf", "23",           # Constant Rate Factor for quality
            "-preset", "medium",    # Encoding speed vs compression
            "-profile:v", "high",   # H.264 profile
            "-level", "4.0",        # H.264 level
            "-pix_fmt", "yuv420p",  # Pixel format for compatibility
            "-movflags", "+faststart"  # Enable streaming
        ])


if __name__ == "__main__":
    folder_path = select_folder()
    
    # list up all mp4 files in the selected folder
    mp4_files = [f for f in os.listdir(folder_path) if f.endswith('.mp4')]
    os.makedirs(os.path.join(folder_path, "output"), exist_ok=True)

    # Check if there are saved coordinates
    saved_coords = load_coordinates(folder_path)
    if saved_coords:
        use_saved = input("Do you want to use the saved coordinates? (y/n): ")
        if use_saved.lower() == 'y':
            coords = saved_coords
            set_coords = True
        else:
            set_coords = False
    else:
        set_coords = False
    
    file_count = 0

    for file in mp4_files:
        file_count +=1
        input_video_path = os.path.join(folder_path, file)
        output_video_path = f"{folder_path}//output//cropped_file{file_count}.mp4"

        if not set_coords == True:
            coords = know_coods.click_and_know_coordinates_from_video(input_video_path)
            if coords is None:
                print("No valid coordinates found.")
                continue

            # Coordinate adjustment option
            adjust = input("Do you want to adjust the coordinates? (y/n): ")
            if adjust.lower() == 'y':
                coords = adjust_coordinates(coords, input_video_path)

            # Coordinate saving option
            save = input("Do you want to save these coordinates? (y/n): ")
            if save.lower() == 'y':
                save_coordinates(coords, folder_path)

        # upper, lower, left, right = coords

        # Final preview option
        final_preview = input("Do you want to show the final preview before cropping? (y/n): ")
        if final_preview.lower() == 'y':
            preview_crop_area(input_video_path, coords)
            preview_result = input("Do you want to show the cropped result preview? (y/n): ")
            if preview_result.lower() == 'y':
                preview_cropped_result(input_video_path, coords)

        chk = input("Do you want to crop with these coordinates? (y/n): ")
        if chk.lower() != 'y':
            coords = adjust_coordinates(coords, input_video_path)
        
        upper, lower, left, right = coords if coords else (79, 902, 203, 1682)
        crop_video(input_video_path, output_video_path, upper, lower, left, right)

        # Ask if user wants to set coordinates for all remaining videos when mp4 files are more than 1
        if not set_coords == True and not len(mp4_files) == 1:
            chk_coords = input("Set coordinates for all remaining videos? (y/n): ")
            if chk_coords.lower() == 'y':
                set_coords = True

    print("")
    print("Video cropping completed.")
    print(f"Number of files processed: {file_count}")