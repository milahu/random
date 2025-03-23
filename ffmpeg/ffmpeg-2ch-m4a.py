import subprocess
import json
import shlex
import argparse

class VideoProcessor:
    def __init__(self, args):
        self.input_file = args.input_file
        self.audio_stream_index = args.audio_stream_index
        self.slow = args.slow
        self.dst_fps = args.dst_fps
        self.afilters = []

    def get_audio_channel_layout(self):
        """ Retrieve the audio channel layout using ffprobe. """
        command = [
            "ffprobe",
            "-v", "error",
            "-select_streams", f"a:{self.audio_stream_index}",
            "-show_entries", "stream=channel_layout",
            "-of", "json",
            self.input_file,
        ]

        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            print(f"Error getting audio layout: {result.stderr}")
            return None

        data = json.loads(result.stdout)
        if "streams" in data and len(data["streams"]) > 0:
            return data["streams"][0].get("channel_layout")

        return None

    def get_loudnorm_audio_filter(self):
        """ Run the first pass of loudnorm filter and extract JSON parameters correctly. """
        command = [
            "ffmpeg",
            "-hide_banner",
            "-nostdin",
            "-i", self.input_file,
            "-af", "loudnorm=I=-23:TP=-1.5:LRA=11:print_format=json",
            "-f", "null",
            "-"
        ]

        print(f"Running first pass:\n{shlex.join(command)}")

        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        loudnorm_json_lines = []
        found_loudnorm = False
        found_json = False

        while proc.poll() is None:  # Loop while process is running
            line = proc.stdout.readline().strip()
            if not line:
                continue

            print(line)  # Show progress output

            if not found_loudnorm and line.startswith("[Parsed_loudnorm_0"):
                found_loudnorm = True

            if not found_json and line == "{":
                found_json = True

            if found_loudnorm and found_json:
                loudnorm_json_lines.append(line)

            if found_json and line == "}":
                found_json = False
                found_loudnorm = False

        # todo remove?
        proc.communicate()

        if proc.returncode != 0:
            raise Exception(f"Error: ffmpeg first pass failed with exit code {proc.returncode}")

        if not loudnorm_json_lines:
            raise Exception("Error: Could not extract loudnorm JSON data.")
            return None

        loudnorm_json_str = "\n".join(loudnorm_json_lines)

        try:
            loudnorm_data = json.loads(loudnorm_json_str)
            measured_i = float(loudnorm_data["input_i"])

            # Apply loudnorm only if loudness is outside the -23 ±2 dB range
            if not (-25 <= measured_i <= -21):
                return f"loudnorm=I=-23:TP=-1.5:LRA=11:measured_I={loudnorm_data['input_i']}:measured_TP={loudnorm_data['input_tp']}:measured_LRA={loudnorm_data['input_lra']}:measured_thresh={loudnorm_data['input_thresh']}:offset={loudnorm_data['target_offset']}:linear=true:print_format=none"

        except json.JSONDecodeError:
            print("Error: Invalid JSON format from loudnorm.")

        return None

    def get_ffmpeg_audio_filter(self):
        """ Generate the audio filter chain. """
        acl = self.get_audio_channel_layout()

        if acl not in ("mono", "stereo"):
            self.afilters.append("downmix=stereo")

        loudnorm_filter = self.get_loudnorm_audio_filter()
        if loudnorm_filter:
            self.afilters.append(loudnorm_filter)

        return ",".join(self.afilters) if self.afilters else None

    def process_video(self):
        """ Process video with the selected filters and options. """
        output_file = f"{self.input_file}.2ch.m4a"
        afilter = self.get_ffmpeg_audio_filter()

        command = [
            "ffmpeg",
            "-hide_banner",
            "-nostdin",
            "-i", self.input_file,
            "-c:a", "aac",
            "-map", f"0:a:{self.audio_stream_index}",
            "-map_metadata", "0",
            "-movflags", "faststart",
        ]

        if self.slow:
            command.extend(["-threads", "1"])  # Removed "-filter_threads 1"

        if afilter:
            print(f"Applying audio filter: {afilter}")
            command.extend(["-af", afilter])

        command.extend(["-y", output_file])

        print(f"Executing command:\n{shlex.join(command)}")
        subprocess.run(command, check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process video audio with downmix and loudnorm filtering.")
    parser.add_argument("input_file", help="Path to the input video file", required=True)
    parser.add_argument("--audio-stream-index", type=int, default=0, help="Audio stream index to process")
    parser.add_argument("--slow", action="store_true", help="Limit CPU usage to 1 core")
    parser.add_argument("--dst-fps", type=str, default="24000/1001", help="Set the destination frame rate")

    args = parser.parse_args()

    processor = VideoProcessor(args)
    processor.process_video()
