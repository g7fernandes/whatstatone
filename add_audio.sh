vin="words_animated_chart.mp4"
vout="words_animated_chart_out.mp4"
audin="Shona.mp3"
a=$(ffprobe -i "$vin" -show_entries format=duration -v quiet -of csv="p=0")
a=${a%.*}
a=`expr $a + 3`
ffmpeg -i "$audin" -ss 0 -to $a -c copy "audout.mp3"
ffmpeg -i "$vin" -i 'audout.mp3' -map 0:0 -map 1:0 -vcodec copy -acodec copy "$vout"
rm audout.mp3
