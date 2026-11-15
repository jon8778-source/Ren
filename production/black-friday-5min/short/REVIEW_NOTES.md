# Prototype review notes (Black Friday Short)

Owner reviewed the 15 s prototype (SHA-256 b4207d27...). Review points: Ren in mouth-closed windows at the approved portrait position; Spending-to-Saving tag moved up so the opening chip no longer overlaps it; known limits (soft 1.8x/2x Alex crops, wave hand touching the left edge in beat 1, Ren in 13 of 22 beats). Launcher QA: no errors, no warnings. Not verified by me: audio listening, phone playback, frame-by-frame mouths. Owner replied "Approved" (14 Nov 2026).

Post-approval change (15 Nov 2026): the full render failed QA ("Less than the impulse cart" overflowed its card in the last beat). The label became "Less than impulse" (44 px) and the card module `bf_short_ui.py` is now a hashed manifest asset. This invalidated the approval fingerprint; the prototype was re-rendered and its decoded video frames are identical to the approved one (MD5 3fc50fca...). Fresh owner approval requested.

Re-approval (15 Nov 2026): owner replied 'Approved' to the unchanged prototype after the post-approval label fix.
