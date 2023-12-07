#!/bin/bash

#set -x

SOURCE_DIR="$(cd "$(dirname "$0")" && pwd)"
target=$SOURCE_DIR
LOG="$SOURCE_DIR/moveLog.txt"

logthis()
{
	MSG=$1
	echo $MSG
	echo $MSG >> $LOG
}

logthis $LOG
chmod 666 $LOG

logthis "------------------------------------------------"
logthis "$(date) staring file mover"

if [ $(ls -l "${target}/Camera" | wc -l) -gt 1 ]
then
	echo "moving photos" >> $LOG
	mv "${target}/Camera"/* "${target}/"
fi

find "$target" -maxdepth 1 | while read file
do
	ext=${file##*.} 
	ext=$(echo $ext | tr '[:upper:]' '[:lower:]')
	case $ext in
	"jpg")
		DATE=$(identify -verbose "$file" | grep 'DateTimeOriginal' | awk '{print $2}')
		#echo "$DATE - $file"
		y=$(echo $DATE | awk --field-separator=":" '{print $1}')
		m=$(echo $DATE | awk --field-separator=":" '{print $2}')
		d=$(echo $DATE | awk --field-separator=":" '{print $3}')
		size=${#d} 
		if [ $size -eq 0 ]
		then
			logthis "failed to get attrabute from file $file" 
			#exit
		else
			npath="../$y/$m/$d/"
			logthis "$file -to- $npath"
			mkdir -p "$npath"
			mv -f "$file" "$npath"
		fi
		;;
	"mp4")
		sp=$(echo $file | awk --field-separator="_" '{print $1}')
		sp=$(echo $sp | tr '[:upper:]' '[:lower:]')
		case $sp in
			"vid")
				date=$(echo $file | awk --field-separator="_" '{print $2}')
				y=${date:0:4}
				m=${date:4:2}
				d=${date:6:2}
				size=${#d}
                		if [ $size -eq 0 ]
                		then
                        		logthis "failed to get attrabute from file $file"
					#exit
				else
				
					npath="../$y/$m/$d/"
				
					logthis "$file -to- $npath"
					mkdir -p "$npath"
					mv -f "$file" "$npath"
               			fi
				
				;;
			*)
				date=$(echo $file | awk --field-separator="_" '{print $2}')
				y=${date:0:4}
				m=${date:4:2}
				d=${date:6:2}
				size=${#d}
				if [ $size -eq 0 ]
				then
						logthis "failed to get attrabute from file $file"
						#exit
				else
					npath="../$y/$m/$d/"
				
					logthis "$file -to- $npath"
					mkdir -p "$npath"
					mv -f "$file" "$npath"
                                fi
				;;
		esac
		;;
	*)
		logthis "skiping file: $file"
	;;
	esac

done

logthis "done: $(date)"

