# Idea 1 (route running): decisions log

Running record of every scope and method choice, with the reason. Built 2026-10-27 night at Logan's request ("now construct the full idea 1"), mirroring the idea 2 pipeline. Tests are written here before they run and logged either way.

## Framing
- Same as idea 2: analysis with a baseline and a better measure, not a predictive model. Draft slot excluded everywhere.
- Logan's original framing (10/20): four route phases, launch, break, ball in the air, YAC. Game tracking has no ball and no defenders, so ball-in-air and YAC can't be measured from movement in games; this build covers launch and break, with separation at pass forward as the outcome.

## Sample
- WR by `nfl_position`, plays with a `route_ran`, regular season, not nullified: 34,889 route plays, 82 WR (62 with 100+ plays).
- Route types: GO 6,752, HITCH 5,640, CROSS 4,406, IN 3,984, POST 3,621, OUT 3,349, CORNER 2,912, SLANT 2,255, SCREEN 969, FLAT 931, WHEEL 51, ANGLE 19.
- Separation at pass forward is filled on 88% of WR route plays (targeted or not); cushion on 95%.
- Play-level dropback duration comes from the OL rows of the same play; time to pass forward comes from the tracking `pass_forward` event.

## Pre-specified tests (written before running)
**Game features per route play** (smoothed speed and acceleration from 01, direction flipped so the offense moves toward +x, glitch tracks dropped, snap to pass forward):
- Launch: `launch_accel` = peak acceleration 0 to 1.0 s; `speed_1s` = speed at 1.0 s.
- Break, only for routes with a break (HITCH, IN, OUT, SLANT, POST, CORNER, CROSS) and pass forward at 1.5 s or later: the break is the 0.4 s span with the largest heading change between 0.5 s and pass forward. `entry_speed` = mean speed in the 0.5 s before it; `break_retention` = minimum speed in the break span divided by entry speed; `reaccel` = peak acceleration in the 0.7 s after the break.
- Reliability: split-half across random halves of each player's plays (players with 100+ plays), within route type where relevant.

**Separation over expected (SOE):** separation at pass forward minus a linear model on route type, cushion, man vs zone, slot vs wide alignment, time to pass forward and play action. Player SOE = mean residual.

**Test A (game):** player-level route features from a random half of plays added to the expected-separation model on the other half; 5-fold CV holding out players; 20 splits. Same design as idea 2 step 7.

**Test B (Combine tracking to SOE):** features from Combine WR route drills (the single-rep route drills, each player's drill values z-scored within drill and averaged): `launch_accel`, `entry_speed`, `break_retention`, `reaccel`, computed the same way as in games with clip start as time 0; plus gauntlet peak speed and tracked 40 peak speed. 6 features, Pearson r with player SOE, Holm across the 6. Reliability of the route composites = split-half across drills.

## Deviation from the pre-specified break definition (logged before any outcome test ran)
- Looking at Combine route clips (positions and headings only, no outcome) showed the breaks are rounded: a dig or speed out turns over 1 to 2 s, not 0.4 s. With a 0.4 s span the detector found only 15 to 27 degrees of turn on 90-degree routes, and the 3.5 s Combine cap cut deep breaks in half (dagger turn runs from about 2.1 to 4.2 s).
- Change: break span 0.8 s (both Combine and games), Combine window capped at 5.0 s instead of 3.5 s. Games stay capped at pass forward. Everything else as specified. No separation or SOE numbers had been computed when this changed.

## Combine route drill features (with the revised break)
- 9 single-rep route drills (8 with a break; GO has launch only), 107 WR. Each drill's values are z-scored within drill and averaged per player.
- Reliability, split-half across drills (200 random drill splits, Spearman-Brown): launch_accel 0.75, entry_speed 0.42, break_retention 0.05, reaccel −0.33. Break quality does not hold up across different routes; launch does. Break retention and re-acceleration are kept in Test B as specified, but with reliability this low they cannot correlate with anything.

## Results (2026-10-27 night)
- Game route features: 34,589 route plays with a clean window; break features on 22,318 break-route plays. Game breaks look shallower than Combine breaks (median turn 20 to 39 degrees over 0.8 s; many routes are thrown before the break finishes, median pass forward 2.7 s).
- Modeling sample: 27,985 plays with separation, cushion, coverage and pass-forward time; 62 WR with 100+ plays.
- **Expected separation** (route, cushion, man vs zone, slot, time to pass forward, play action) explains 24% of play-level variance.
- **Separation over expected is a stable player trait:** split-half reliability 0.78.
- **Game route features are stable too** (split-half, z-scored within route): launch accel 0.95, speed at 1 s 0.95, entry speed 0.73, break retention 0.57, re-accel 0.51.
- **Test A (game route features to SOE for unseen players): null.** Adding them made held-out prediction worse in 19 of 20 splits. Descriptively, on the same plays, WR who enter breaks faster have higher SOE (r 0.38) and speed at 1 s r 0.33, but that does not carry to new players in this design.
- **Test B (Combine tracking to SOE): null after correction.** 6 features, 56 to 62 WR. Tracked 40 peak speed r = +0.32 (p 0.018, Holm p 0.11); re-accel r −0.21; the rest near zero. Combine route-drill composites are not related to SOE; break retention and re-accel were unreliable across drills (0.05 and −0.33), so they could not show a link.
