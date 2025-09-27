import cv2
import os
import tkinter as tk
from tkinter import filedialog
import gc
import psutil
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.audio.AudioClip import concatenate_audioclips

def get_memory_usage():

    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024  # MB単位

def create_repeated_audio(audio_clip, repeat_count):

    print(f"音声を{repeat_count}回繰り返し中...")
    repeated_clips = [audio_clip] * repeat_count
    return concatenate_audioclips(repeated_clips)

def add_audio_to_video(video_path, original_video_path, repeat_count):
    
    print("音声を動画に追加中...")
    
    try:
        # 元の動画から音声を抽出
        original_clip = VideoFileClip(original_video_path)
        if original_clip.audio is None:
            print("元の動画に音声が含まれていません。")
            original_clip.close()
            return video_path
        
        # 音声を繰り返し
        original_audio = original_clip.audio
        repeated_audio = create_repeated_audio(original_audio, repeat_count)
        
        # 動画を読み込み
        video_clip = VideoFileClip(video_path)
        
        # 音声の長さを動画の長さに合わせる
        if repeated_audio.duration > video_clip.duration:
            repeated_audio = repeated_audio.subclipped(0, video_clip.duration)
        elif repeated_audio.duration < video_clip.duration:
            # 音声が短い場合は最後まで再生してから無音
            print(f"音声時間: {repeated_audio.duration:.2f}秒, 動画時間: {video_clip.duration:.2f}秒")
        
        # 音声付き動画を作成
        final_video = video_clip.with_audio(repeated_audio)
        
        # 音声付きファイル名
        base_name = os.path.splitext(video_path)[0]
        audio_video_path = f"{base_name}_with_audio.mp4"
        
        # 出力（音声付き）
        final_video.write_videofile(
            audio_video_path,
            codec='libx264',
            audio_codec='aac',
            logger=None
        )
        
        # メモリ解放
        original_clip.close()
        video_clip.close()
        final_video.close()
        original_audio.close()
        repeated_audio.close()
        
        print(f"音声付き動画を保存しました: {audio_video_path}")
        
        # 音声なし動画を削除するか確認
        delete_silent = input("音声なしの動画ファイルを削除しますか？ (y/n): ")
        if delete_silent.lower() == 'y':
            os.remove(video_path)
            print(f"音声なし動画を削除しました: {video_path}")
        
        return audio_video_path
        
    except Exception as e:
        print(f"音声追加エラー: {e}")
        return video_path

def process_video_with_memory_management(selected_file, add_audio_option=None):
   
    print("処理中の動画:", selected_file)
    print(f"開始時メモリ使用量: {get_memory_usage():.1f} MB")
    
    cap = cv2.VideoCapture(selected_file)
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    cap.release()
    
    # 保存先パス
    base_name = os.path.splitext(os.path.basename(selected_file))[0]
    os.makedirs(os.path.join(os.path.dirname(selected_file), "repeated"), exist_ok=True)
    save_path = os.path.join(os.path.dirname(selected_file), "repeated", f"{base_name}_repeated.mp4")
    
    # 解像度を下げるオプション（必要に応じて）
    scale_factor = 1.0
    available_memory = psutil.virtual_memory().available / 1024 / 1024  # MB
    estimated_frame_size = (width * height * 3) / 1024 / 1024  # MB
    
    print(f"利用可能メモリ: {available_memory:.1f} MB")
    print(f"1フレームの推定サイズ: {estimated_frame_size:.2f} MB")
    
    if available_memory < 1000:  # 1GB未満の場合は解像度を下げる
        scale_factor = 0.5
        width = int(width * scale_factor)
        height = int(height * scale_factor)
        print(f"メモリ不足のため解像度を{scale_factor}倍に調整: {width}x{height}")
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(save_path, fourcc, fps, (width, height))
    count = 20
    print(f"動画を{count}回繰り返して保存します。")
    print(f"フレーム数: {total_frames}, 解像度: {width}x{height}")
    print(f"保存先: {save_path}")
    
    # 動画を20回繰り返して処理（メモリ効率的な方法）
    for repeat_num in range(count):
        print(f"繰り返し {repeat_num + 1}/{count} を処理中...")
        
        # 各繰り返しごとに動画を再度開く
        cap = cv2.VideoCapture(selected_file)
        
        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # 必要に応じて解像度を調整
            if scale_factor != 1.0:
                frame = cv2.resize(frame, (width, height))
            
            out.write(frame)
            frame_count += 1
            
            # メモリ使用量を抑えるため、定期的にガベージコレクションを促す
            if frame_count % 50 == 0:
                gc.collect()
                
            # メモリ使用量をモニタリング
            if frame_count % 200 == 0:
                current_memory = get_memory_usage()
                print(f"  フレーム {frame_count}: メモリ使用量 {current_memory:.1f} MB")
        
        cap.release()
        gc.collect()  # 各繰り返し後にガベージコレクション
        print(f"  {frame_count} フレームを処理しました (メモリ: {get_memory_usage():.1f} MB)")
    
    out.release()
    print(f"完了時メモリ使用量: {get_memory_usage():.1f} MB")
    
    # 音声を追加するか確認
    if add_audio_option is None:
        add_audio = input("元の動画の音声を繰り返し動画に追加しますか？ (y/n): ")
        should_add_audio = add_audio.lower() == 'y'
    else:
        should_add_audio = add_audio_option
    
    if should_add_audio:
        final_path = add_audio_to_video(save_path, selected_file, count)
        return final_path
    
    return save_path

# GUIで動画ファイルを選択
root = tk.Tk()
root.withdraw()

# select few files
selected_files = filedialog.askopenfilenames(title="動画ファイルを選択してください", filetypes=[("MP4ファイル", "*.mp4")])

if not selected_files:
    print("動画ファイルが選択されませんでした。")
    exit(1)

# 複数ファイル処理時の音声追加設定
add_audio_to_all = None
if len(selected_files) > 1:
    batch_audio = input("すべての動画に音声を追加しますか？ (y/n/ask): ")
    if batch_audio.lower() == 'y':
        add_audio_to_all = True
    elif batch_audio.lower() == 'n':
        add_audio_to_all = False
    # 'ask'の場合は各ファイルで個別に確認

for selected_file in selected_files:
    
    if not selected_file.lower().endswith('.mp4'):
        print("MP4ファイル以外が選択されました。\n処理スキップします。")
        continue
    
    try:
        save_path = process_video_with_memory_management(selected_file, add_audio_to_all)
        print("保存完了:", save_path)
    except MemoryError as e:
        print(f"メモリ不足エラー: {e}")
        print("動画の解像度が高すぎるか、利用可能メモリが不足しています。")
        print("動画を短くするか、システムのメモリを増やしてください。")
    except Exception as e:
        print(f"処理エラー: {e}")
        
print("すべての動画の処理が完了しました。")