#!/usr/bin/env python3

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
        return "pan=stereo|" + "|".join(map(lambda kv: kv[0] + "=" + "+".join(map(lambda kv2: f"{kv2[1]}*{kv2[0]}", kv[1].items())), coefficients.items()))



if __name__ == "__main__":
    import sys
    input_channel_layout = sys.argv[1]
    #print(get_coefficients_for_downmix_to_stereo(input_channel_layout))
    print(get_ffmpeg_audio_filter_for_downmix_to_stereo(input_channel_layout))
