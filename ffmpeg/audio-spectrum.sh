#!/usr/bin/env bash

# audio-spectrum.sh
# get spectrograms of audio streams
#
# usage: audio-spectrum.sh a.mp3 b.m4a c.mp4 d.mkv ....
#
# dependencies: sox, ffmpeg
# license: public domain, warranty: none
# version: 2019-05-17 by milahu

# refs
# http://sox.sourceforge.net/sox.html # spectrogram [options]

trap "stty sane" EXIT # workaround for 'broken pipe'

ff_args="" # ffmpeg arguments
sx_args="" # sox arguments

ff_args+=" -loglevel error"

ff_astream=0 # only use first audio stream
ff_args+=" -map 0:a:${ff_astream}?"

ff_args+=" -ac 1" # use only one audio channel
sx_args+=" channels 1"

sx_args+=" gain -n -3" # normalize volume to -3dB

# set sampling rate
# only analyze frequencies below f_max = rate / 2
# also normalize spectrogram height to f_max
#sx_args+=" rate 6k"  # only show f <  3kHz "where the human auditory system is most sensitive"
sx_args+=" rate 48k" # only show f < 24kHz

#####sx_args+=" -V" # verbose

# use wav as temporary format, if sox cant read file
ff_args+=" -c:a pcm_s16le -f wav"
sx_type="wav"

# process files from "argv"
for i in "$@"
do
	echo "$i"
	o="$i.sg.png" # output file
	t=$(basename "$i") # title above spectrogram
	c="spectrogram by SoX, the Sound eXchange tool" # comment below spectrogram

sg_opts=""
#sg_opts+=" -r" # Raw spectrogram: suppress the display of axes and legends.
#sg_opts+=" -a" # Suppress the display of the axis lines. This is sometimes useful in helping to discern artefacts at the spectrogram edges.

sg_opts+=" -x 1080" # max width
#sg_opts+=" -X 100" # time resolution (pixels per second)
#sg_opts+=" -y 720" # relative height
sg_opts+=" -Y 720" # target total height
sg_opts+=" -z 100" # z-axis range in dB

	# try to read original format
	echo analyze
	sox "$i" -n \
		$sx_args \
		spectrogram -o "$o" $sg_opts \
		2>&1 | grep -v "no handler for detected file type"

		#spectrogram -o "$o" -c "$c" -t "$t" $sg_opts \

	if (( ${PIPESTATUS[0]} != 0 ))
	then
		# sox failed. convert audio and retry
		echo convert

		# get duration of stream or container
		# spectrogram filter has no "ignore length" option
		# and without a "duration prediction" will only read 8 seconds

# error on m4a files: Invalid stream specifier: 0:a:0?
#           ffprobe ....
#			-select_streams "0:a:${ff_astream}?" \
# --> select stream "0"

		d=$(ffprobe "$i" -v error -of compact=s=_ \
			-show_entries stream=duration:format=duration \
			| sort | grep -v =N/A \
			| tail -n 1 | cut -d= -f2)
		# 'tail -n 1' --> prefer stream duration
		# 'head -n 1' --> prefer container duration

		if [[ -z "$d" ]]
		then
			echo -e "skip. duration not found FIXME\n"
			continue
		fi

		# bash "process substitution" magic
		sox \
			--type "$sx_type" \
			--ignore-length \
			<( ffmpeg -i "$i" $ff_args - ) \
			--null \
			$sx_args \
			spectrogram -d "$d" -o "$o" -c "$c" -t "$t"
	fi

	echo -e "done\n$o\n"
done
