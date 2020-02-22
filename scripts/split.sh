# Needs to be used in combination with a `splits` file containing instructions
# on what to do

rm -f output/*.mp3
while IFS=, read -r name start_t end_t
do
  # TODO: Handle comments in the split file!!
  output_file="./output/$name.mp3"
  echo "Working on >$name<"
  ffmpeg -i all.mp3 -n -acodec copy -ss "00:$start_t" -to "00:$end_t" -f mp3 "$output_file"
done < splits
