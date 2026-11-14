# Pilot technical QA

- PASS  video 1280x720 24 fps  1280x720 24/1
- PASS  frame count = shot table  5875 vs 5875
- PASS  audio/video length within 0.05 s  244.792000 vs 244.791667
- PASS  full decode, errors fatal  
- PASS  shots contiguous from frame 0  
- PASS  shot caps (Ren 5.5 / still 2.5 / graphic 3.5 s)  []
- PASS  hard cuts only at shot starts; other large changes only inside a 13-frame entrance animation (pop/slide) after a cut  204 large frame changes: 104 at cuts, 100 in entrance animations, unexplained: []
- PASS  no 1-2 frame shots  []
- PASS  all text >= 36 px at 1080p (= 24 px in the 720p file)  []
- PASS  text inside 55 px side / 40 px vertical margins  []
- PASS  no card text overlaps Ren's bounding box  []
- PASS  every displayed dollar figure is in the checked table  shown ['$10', '$105', '$107', '$115', '$120', '$150', '$158', '$183', '$20', '$205', '$25', '$263', '$30', '$300', '$32', '$341', '$37', '$41', '$45', '$48', '$60', '$78', '$80', '$90'], allowed ['$10', '$105', '$107', '$115', '$120', '$150', '$158', '$183', '$20', '$205', '$25', '$263', '$30', '$300', '$32', '$341', '$37', '$41', '$45', '$48', '$60', '$78', '$80', '$90']
- PASS  figure values: 158+183=341, 158+105=263, 341-263=78, 48+30=78, 300  
- PASS  loudness -17..-15 LUFS, true peak <= -1 dBFS  -16.2 LUFS, -1.4 dBFS

14/14 checks passed.
