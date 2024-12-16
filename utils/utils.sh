# replace in texts
find {.,lectures,assignments,materials} -maxdepth 10 -name "*.qmd" | xargs sed -i 's/ 2024/ 2025/g'
find {.,lectures,assignments,materials} -maxdepth 10 -name "*.md" | xargs sed -i 's/ 2024/ 2025/g'
find {.,lectures,assignments,materials} -maxdepth 10 -name "*.qmd" | xargs sed -i 's/KED2024/KED2025/g'
find {.,lectures,assignments,materials} -maxdepth 10 -name "*.md" | xargs sed -i 's/KED2024/KED2025/g'

# rename filenames (-n is for dry run; remove to perform actual renaming)
ls **/*KED2024* | xargs rename -nv KED2024 KED2025

# check remaining text sections containing a year
grep -Prio ".{20}(ked| )2024 .{20}" .


# decrease image size
mogrify -format jpg -quality 70%  ma_flueckiger_country_mentions_black.png
