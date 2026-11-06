#!/usr/bin/env bash
# Download the public reference images used by the task set into tmp/refs/.
# Idempotent: existing files are kept. Sources and licenses: see the table below
# (all from Wikimedia Commons; 960 px thumbnails unless the original is smaller).
set -eu
repo=$(cd "$(dirname "$0")/../../.." && pwd); dest="$repo/tmp/refs"; mkdir -p "$dest"
ua="svg-skill-research/0.1"
c=https://thumb.wikimedia.org/wikipedia/commons/thumb
u=https://upload.wikimedia.org/wikipedia/commons
while read -r name url; do
  [ -z "$name" ] && continue
  [ -s "$dest/$name" ] && continue
  curl -sfL -A "$ua" -o "$dest/$name" "$url" && echo "fetched $name"; sleep 1
done <<LIST
lighthouse-marshall-point.jpg   $c/a/a9/Marshall_Point_Lighthouse_Center.JPG/960px-Marshall_Point_Lighthouse_Center.JPG
lighthouse-cape-may.jpg         $c/a/a3/Cape_May_Lighthouse_September_2020_002.jpg/960px-Cape_May_Lighthouse_September_2020_002.jpg
woodblock-great-wave.jpg        $c/0/0a/The_Great_Wave_off_Kanagawa.jpg/960px-The_Great_Wave_off_Kanagawa.jpg
photo-grey-heron.jpg            $c/8/82/Grey_heron_2022_04_17_02.jpg/960px-Grey_heron_2022_04_17_02.jpg
poster-zion-national-park.jpg   $u/2/2d/Zion_National_Park_poster_1938.jpg
product-photo-teapot.jpg        $c/6/6a/Teapot_and_cover_%28AM_1985.425-4%29.jpg/960px-Teapot_and_cover_%28AM_1985.425-4%29.jpg
botanical-plate-nutmeg.jpg      $u/2/24/Myristica_fragrans_-_K%C3%B6hler%E2%80%93s_Medizinal-Pflanzen-097.jpg
LIST
# | File | Commons page | License, author |
# | lighthouse-marshall-point | Marshall_Point_Lighthouse_Center.JPG | CC BY-SA 4.0, Derek Ramsey |
# | lighthouse-cape-may | Cape_May_Lighthouse_September_2020_002.jpg | CC BY-SA 4.0, User:King of Hearts |
# | woodblock-great-wave | The_Great_Wave_off_Kanagawa.jpg | public domain, after Katsushika Hokusai |
# | photo-grey-heron | Grey_heron_2022_04_17_02.jpg | CC BY 4.0, Alexis Lours |
# | poster-zion-national-park | Zion_National_Park_poster_1938.jpg | public domain, National Park Service (WPA) |
# | product-photo-teapot | Teapot_and_cover_(AM_1985.425-4).jpg | CC BY 4.0, Auckland Museum |
# | botanical-plate-nutmeg | Myristica_fragrans_-_Köhler–s_Medizinal-Pflanzen-097.jpg | public domain, Köhler's Medizinal-Pflanzen |
