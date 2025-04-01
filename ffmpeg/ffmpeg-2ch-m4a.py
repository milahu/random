import subprocess
import json
import shlex
import argparse
import time
import os



# todo add arg --to

# todo parse ffmpeg progress output
# todo make ffmpeg show progress less often




# downmix-audio-to-stereo-rfc7845.py

# https://superuser.com/a/1616102/951886
# Properly downmix 5.1 to stereo using ffmpeg

# https://www.rfc-editor.org/rfc/rfc7845#section-5.1.1.5
# RFC 7845 Section 5.1.1.5 Downmixing

# https://trac.ffmpeg.org/wiki/AudioChannelManipulation

# https://mediaarea.net/AudioChannelLayout # speaker positions

# mpv-downmix-gui/src/mpv_downmix_gui/downmix_rfc7845.py

# test:
# for L in 3.0 4.0 5.0 5.1 6.1 7.1; do echo; echo $L; ./downmix-audio-to-stereo-rfc7845.py $L; done

# TODO 5.1(side) versus 5.1

# note: ffmpeg says "back" instead of "rear"



from math import sqrt



def get_coefficients_for_downmix_to_stereo(
        input_channel_layout,
        scale_center = 1.0,
        scale_lfe = 1.0,
        scale_front = 1.0,
        scale_rear = 1.0,
        scale_side1 = 1.0,
        scale_side2 = 1.0,
    ):

    if input_channel_layout in ("mono", "monophonic", "1ch", "1.0"):
        return None # noop

    if input_channel_layout in ("stereo", "2ch", "2.0"):
        return None # noop

    if input_channel_layout in ("linear surround", "3ch", "3.0"):
        # Linear Surround Channel Mapping: L C R
        # left, center, right
        sides = 1
        center = (1/sqrt(2)) * scale_center
        n = 1/(sides + center)
        return dict(
            FL = dict(FL=sides*n, FC=center*n, FR=0),
            FR = dict(FL=0, FC=center*n, FR=sides*n),
        )

    # TODO verify downmix 3.1 to stereo
    # note: 4ch is ambiguous: 3.1 or 4.0
    # note: downmix formula for 3.1 channel layout is not specified in RFC7845
    if input_channel_layout in ("3.1",):
        # 3.1 Surround Mapping: L C R LFE
        # left, center, right, LFE
        # 3.0 with LFE
        """
        # based on the 3.0 formula
        sides = 1
        center = (1/sqrt(2)) * scale_center
        lfe = (1/sqrt(2)) * scale_lfe
        n = 1/(sides + center + lfe)
        """
        # based on one example...
        # Lammbock.2001.German.720p.BluRay.x264-SPiCY/spy-lammbock-720p.mkv
        # for this movie, i find only 3.1 or 2.0 releases
        # so probably the source has 3.1 audio
        # pan=stereo|FL=0.22058823529411767*FL+0.11029411764705883*FC+0.0*FR+0.5*LFE|FR=0.0*FL+0.11029411764705883*FC+0.22058823529411767*FR+0.5*LFE
        # -> music too loud, dialog too quiet
        # music is in FL + FR, dialog is in FC -> make FC louder
        # 0.5 + 1.0 + 0.5
        #       1.0
        # pan=stereo|FL=0.5*FL+0.5*FC+0.0*FR+0.5*LFE|FR=0.0*FL+0.5*FC+0.5*FR+0.5*LFE
        # -> could be more bass
        # 0.25 + 0.5 + 0.25
        #        1.0
        # pan=stereo|FL=0.25*FL+0.25*FC+0.0*FR+0.5*LFE|FR=0.0*FL+0.25*FC+0.25*FR+0.5*LFE
        # -> sounds good
        sides = 1
        center = 1
        lfe = 2
        n = 1/(sides + center + lfe)
        return dict(
            FL = dict(FL=sides*n, FC=center*n, FR=0, LFE=lfe*n),
            FR = dict(FL=0, FC=center*n, FR=sides*n, LFE=lfe*n),
        )

    # note: 4ch is ambiguous: 3.1 or 4.0
    if input_channel_layout in ("quadraphonic", "4.0"):
        # Quadraphonic Channel Mapping: FL FR RL RR
        # front left, front right, rear left, rear right
        front = 1 * scale_front
        side1 = (sqrt(3)/2) * scale_side1
        side2 = (1/2) * scale_side2
        n = 1/(front + side1 + side2)
        return dict(
            FL = dict(FL=front*n, FR=0, BL=side1*n, BR=side2*n),
            FR = dict(FL=0, FR=front*n, BL=side2*n, BR=side1*n),
        )

    # RFC7845:
    # Matrices for 3 and 4 channels are normalized so
    # each coefficient row sums to 1 to avoid clipping.  For 5 or more
    # channels, they are normalized to 2 as a compromise between clipping
    # and dynamic range reduction.

    if input_channel_layout in ("5.0", "5ch"):
        # 5.0 Surround Mapping: FL FC FR RL RR
        # front left, front center, front right, rear left, rear right
        # 5.1 without subwoofer (LFE)
        front = 1 * scale_front
        center = (1/sqrt(2)) * scale_center
        side1 = (sqrt(3)/2) * scale_side1
        side2 = (1/2) * scale_side2
        n = 2/(front + center + side1 + side2) # note: 2/
        return dict(
            FL = dict(FL=front*n, FC=center*n, FR=0, BL=side1*n, BR=side2*n),
            FR = dict(FL=0, FC=center*n, FR=front*n, BL=side2*n, BR=side1*n),
        )

    if input_channel_layout in ("5.1", "5.1(side)", "6ch"):
        # 5.1 Surround Mapping: FL FC FR RL RR LFE
        # front left, front center, front right, rear left, rear right, LFE
        front = 1 * scale_front
        center = (1/sqrt(2)) * scale_center
        side1 = (sqrt(3)/2) * scale_side1
        side2 = (1/2) * scale_side2
        lfe = (1/sqrt(2)) * scale_lfe
        n = 2/(front + center + side1 + side2 + lfe) # note: 2/
        return dict(
            FL = dict(FL=front*n, FC=center*n, FR=0, BL=side1*n, BR=side2*n, LFE=lfe*n),
            FR = dict(FL=0, FC=center*n, FR=front*n, BL=side2*n, BR=side1*n, LFE=lfe*n),
        )

    if input_channel_layout in ("6.1", "7ch"):
        # 6.1 Surround Mapping: FL FC FR SL SR RC LFE
        # front left, front center, front right, side left, side right, rear center, LFE
        # 5.1 + rear center, "rear" -> "side"
        front = 1 * scale_front
        center = (1/sqrt(2)) * scale_center
        side1 = (sqrt(3)/2) * scale_side1
        side2 = (1/2) * scale_side2
        rearC = (sqrt(3)/2)/sqrt(2)
        lfe = (1/sqrt(2)) * scale_lfe
        n = 2/(front + center + side1 + side2 + rearC + lfe) # note: 2/
        return dict(
            FL = dict(FL=front*n, FC=center*n, FR=0, SL=side1*n, SR=side2*n, BC=rearC*n, LFE=lfe*n),
            FR = dict(FL=0, FC=center*n, FR=front*n, SL=side2*n, SR=side1*n, BC=rearC*n, LFE=lfe*n),
        )

    if input_channel_layout in ("7.1", "8ch"):
        # 7.1 Surround Mapping: FL FC FR SL SR RL RR LFE
        # front left, front center, front right, side left, side right, rear left, rear right, LFE
        # 6.1 + RC -> RL RR
        front = 1 * scale_front
        center = (1/sqrt(2)) * scale_center
        side1 = (sqrt(3)/2) * scale_side1
        side2 = (1/2) * scale_side2
        lfe = (1/sqrt(2)) * scale_lfe
        n = 2/(front + center + 2*side1 + 2*side2 + lfe) # note: 2/
        return dict(
            FL = dict(FL=front*n, FC=center*n, FR=0, SL=side1*n, SR=side2*n, BL=side1*n, BR=side2*n, LFE=lfe*n),
            FR = dict(FL=0, FC=center*n, FR=front*n, SL=side2*n, SR=side1*n, BL=side2*n, BR=side1*n, LFE=lfe*n),
        )

    raise ValueError(f"unknown input_channel_layout {input_channel_layout}")



def get_ffmpeg_audio_filter_for_downmix_to_stereo(input_channel_layout, **kwargs):
        coefficients = get_coefficients_for_downmix_to_stereo(input_channel_layout, **kwargs)
        if coefficients is None:
            return ""
        return "pan=stereo|" + "|".join(map(lambda kv: kv[0] + "=" + "+".join(map(lambda kv2: f"{kv2[1]}*{kv2[0]}", kv[1].items())), coefficients.items()))


def format_loudnorm_af(d):
  return ":".join([
    f"loudnorm=I=-23",
    "TP=-1.5",
    "LRA=11",
    f"measured_I={d['input_i']}",
    f"measured_TP={d['input_tp']}",
    f"measured_LRA={d['input_lra']}",
    f"measured_thresh={d['input_thresh']}",
    f"offset={d['target_offset']}",
    f"linear=true",
    f"print_format=none"
  ])


class VideoProcessor:
    def __init__(self, args):
        self.args = args
        self.input_file = args.input_file
        self.audio_stream_index = args.audio_stream_index
        self.slow = args.slow
        self.dst_fps = args.dst_fps
        self.ss = args.ss
        self.to = args.to
        self.t = args.t
        self.flac = args.flac
        self.wav = args.wav
        self.afilters = []
        self.t1 = time.time()

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
            time.sleep(3)
            return None

        data = json.loads(result.stdout)
        if "streams" in data and len(data["streams"]) > 0:
            return data["streams"][0].get("channel_layout")

        return None

    def get_loudnorm_audio_filter(self):
        """ Run the first pass of loudnorm filter and extract JSON parameters correctly. """
        af = ""
        if self.downmix_af:
          af += self.downmix_af + ","
        af += "loudnorm=I=-23:TP=-1.5:LRA=11:print_format=json"
        command = [
            "ffmpeg",
            "-hide_banner",
            "-nostdin",
            "-i", self.input_file,
            "-af", af,
            "-f", "null",
        ]
        if self.ss:
          command += [
            "-ss", self.ss
          ]
        if self.to:
          command += [
            "-to", self.to
          ]
        if self.t:
          command += [
            "-t", self.t
          ]
        if self.slow:
            # limit cpu usage
            command += [
              "-threads", "1",
            ]
        command += ["-"]

        print(f"Running first loudnorm pass\n> {shlex.join(command)}")
        time.sleep(3)

        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        loudnorm_json_lines = []
        found_loudnorm = False
        found_json = False

        while proc.poll() is None:  # Loop while process is running
            line = proc.stdout.readline().strip()
            if not line:
                continue

            print(line)  # Show progress output

            if not found_loudnorm and line.startswith("[Parsed_loudnorm_"):
                found_loudnorm = True
                # todo parse stream id
                # Parsed_loudnorm_0
                # Parsed_loudnorm_1
                # Parsed_loudnorm_2
                # ...

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
                return format_loudnorm_af(loudnorm_data)

        except json.JSONDecodeError:
            print(f"failed to parse json string {loudnorm_json_str!r}")
            raise Exception("Error: Invalid JSON format from loudnorm.")

        return None

    def get_ffmpeg_audio_filter(self):
        """ Generate the audio filter chain. """
        acl = self.get_audio_channel_layout()
        
        self.downmix_af = None

        if acl not in ("", "mono", "stereo"):
            self.downmix_af = get_ffmpeg_audio_filter_for_downmix_to_stereo(acl)
            self.afilters.append(self.downmix_af)

        loudnorm_filter = self.get_loudnorm_audio_filter()
        if loudnorm_filter:
            self.afilters.append(loudnorm_filter)

        return ",".join(self.afilters) if self.afilters else None

    def process_video(self):
        """ Process video with the selected filters and options. """
        if self.flac:
          output_ext = "flac"
        elif self.wav:
          output_ext = "wav"
        else:
          output_ext = "m4a"
        output_file = f"{self.input_file}.{self.audio_stream_index}.2ch.{output_ext}"
        afilter = self.get_ffmpeg_audio_filter()

        command = [
            "ffmpeg",
            "-hide_banner",
            "-nostdin",
            "-i", self.input_file,
            "-map", f"0:a:{self.audio_stream_index}",
            "-map_metadata", "0",
            "-movflags", "faststart",
        ]
        if self.flac:
          pass
        elif self.wav:
          # default: pcm_s16le
          pass
        else:
          command += [
            # todo use fdk_aac or qaac
            "-c:a", "aac",
          ]
        if self.ss:
          command += [
            "-ss", self.ss
          ]
        if self.to:
          command += [
            "-to", self.to
          ]
        if self.t:
          command += [
            "-t", self.t
          ]
        if self.slow:
            # limit cpu usage
            command += [
              "-threads", "1",
            ]
        if afilter:
            print(f"Applying audio filter: {afilter}")
            command += [
              "-af", afilter
            ]
            time.sleep(3)
        command += [
          "-y",
          output_file
        ]

        print(f"Executing command:\n{shlex.join(command)}")
        time.sleep(3)
        subprocess.run(command, check=True)
        dt = time.time() - self.t1
        print(f"done {output_file!r} in {dt} seconds")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process video audio with downmix and loudnorm filtering.")
    parser.add_argument("input_file", help="Path to the input video file")
    parser.add_argument("--audio-stream-index", type=int, default=0, help="Audio stream index to process")
    parser.add_argument("--slow", action="store_true", help="Limit CPU usage to 1 core")
    parser.add_argument("--dst-fps", type=str, default="24000/1001", help="Set the destination frame rate")
    parser.add_argument("--ss", type=str, help="start position")
    parser.add_argument("--to", type=str, help="end position")
    parser.add_argument("--t", type=str, help="output duration")
    parser.add_argument("--flac", action="store_true", help="produce flac file")
    # note: flac is better than wav
    # Filesize 6815932518 invalid for wav, output file will be broken
    parser.add_argument("--wav", action="store_true", help="produce wav file")

    args = parser.parse_args()
    
    assert os.path.exists(args.input_file)

    processor = VideoProcessor(args)
    processor.process_video()

r"""
pass 1:
speed=3x

pass 2:
size= 1561642KiB
time=01:57:15.70
bitrate=1818.3kbits/s
speed=12.6x
done 'x.mkv.0.2ch.flac' in 2806.6607785224915 seconds

total:
real    46m47.064s
user    153m32.608s
sys     7m36.345s



size=116485KiB
time=01:57:15.70
bitrate= 135.6kbits/s
speed= 8.4x
[aac @ 0xb4000076817633d0] Qavg: 603.010
done 'x.mkv.0.2ch.m4a' in 2038.131929397583 seconds

real    33m58.566s
user    164m48.518s
sys     5m28.551s
"""

