# Pilot technical QA

- PASS  video 1280x720 24 fps  1280x720 24/1
- PASS  frame count = shot table  1215 vs 1215
- PASS  audio/video length within 0.05 s  50.625000 vs 50.625000
- PASS  full decode, errors fatal  
- PASS  shots contiguous from frame 0  
- PASS  shot caps (Ren 5.5 / still 2.5 / graphic 3.5 s)  []
- PASS  hard cuts only at shot starts; other large changes only inside a 13-frame entrance animation (pop/slide) after a cut  42 large frame changes: 21 at cuts, 21 in entrance animations, unexplained: []
- PASS  no 1-2 frame shots  []
- PASS  all text >= 36 px at 1080p (= 24 px in the 720p file)  []
- PASS  text inside 55 px side / 40 px vertical margins  []
- PASS  no card text overlaps Ren's bounding box  []
- PASS  every displayed dollar figure is in the checked table  shown ['$263', '$300', '$341', '$78'], allowed ['$263', '$300', '$341', '$78']
- PASS  figure values: 158+183=341, 158+105=263, 341-263=78, 48+30=78, 300  
- PASS  loudness -17..-15 LUFS, true peak <= -1 dBFS  -16.2 LUFS, -1.6 dBFS

14/14 checks passed.
