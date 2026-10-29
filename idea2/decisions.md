# Idea 2 (OL pass set): decisions log

Running record of every scope and method choice, with the reason. Newest at the bottom of each section.

## Framing
- **Analysis, not a predictive model** (2026-10-26). The question is whether set quality is measurable, stable, linked to the Combine, and related to pressure. Any regression is the baseline vs better-measure comparison inside the analysis.

## Preprocessing (01_preprocess)
- **Savitzky-Golay smoothing**, window 7 frames (0.7 s), order 2, within each clip or play. Raw frame differences of `s` gave impossible accelerations. Window 5/7/9 barely changes 40 peaks (peak accel 5.54/5.43/5.33, peak speed 10.59 at all three).
- **Combine kinematics grouped by `event_id` + `entity_type`.** 551 clips mix ball rows into the same event_id.
- **Glitch tracks dropped** (`~glitch_track`): one-frame jump over 1.5 yd or raw speed change over 15 yd/s^2. About 0.2% of game tracks (112 / 212 / 239 by season).
- **Direction flip checked**: 94 to 95% of route runners gain x and 91 to 92% of pass blockers lose x in the first 1.5 s after the snap.

## Sample (step 1)
- **OL by `nfl_position`** (T, G, C). `lined_up_position` kept as a column.
- **Pass blocking** = `pass_rushers_encountered` not null and `route_ran` null.
- **Regular season only.** No preseason (different players and effort) and no postseason (scope choice: every team contributes the same kind of game).
- **Nullified penalty plays dropped.**
- **Short dropbacks (2 s or less) kept and flagged** (`short_dropback`), about 1 in 6 plays. Reason: on dropbacks of 1.5 s or less, about half of linemen do not retreat (aggressive or quick sets), and under-center formations show more forward sets (play-action). Decide later whether the main analysis cuts them.
- **2025 kept in.** Holding out the 2025 season also removed the whole 2025 draft class (56 players instead of 89). Replication will be within player across seasons, which doubles as game-side reliability.
- **No minimum play count yet.** 100 was a placeholder. The cutoff will come from split-half reliability plus Spearman-Brown after features exist, or players are kept and shrunk (partial pooling).
- Result: pressure allowed 8.7%, no nulls. 89 linemen, median 433 plays.

## Game window (step 2)
- **Snap** = first frame tagged `ball_snap` on the play.
- **Window** = 0.3 s before the snap to 1.5 s after, fixed length. Pre-snap frames give a clean stance position. Fixed length keeps plays comparable; ending at the throw would make window length a variable.
- Load: 48,688 lineman-plays found in tracking, 3.67M frames.
- Window result: 48,688 lineman-plays loaded, 48,649 after dropping glitch tracks and plays with no snap, 48,607 with the full window. Every full window has exactly 19 frames. Total lost: 81 (0.17%).

## Features (step 3)
- **Stance** = mean x and y over the 3 frames before the snap.
- **Three features picked** (2026-10-27): `retreat_depth` (stance x minus x at 1.5 s, positive = back), `peak_accel_05` (max smoothed acceleration from snap to 0.5 s), `momentum` (Combine weight in kg x peak smoothed speed in m/s over 0 to 1.5 s).
- Mass is Combine-day weight, fixed per player; linemen often gain weight in the NFL, so this is a known limitation.
- Distributions (48,607 lineman-plays, no NaNs): retreat depth median 1.93 yd (IQR 1.1 to 2.6, min -4.1, max 6.0); peak accel median 2.32 yd/s^2 (min -1.8, max 7.4); momentum median 322 kg m/s.
- **Play-level correlation: momentum vs peak speed 0.99.** Weight vs momentum 0.19. Among OL, weight varies too little to separate momentum from speed at the play level. Player-level check pending before deciding whether momentum stays.
- **Player-level check (89 OL):** momentum vs peak speed 0.95, momentum vs weight 0.48, weight vs peak speed 0.18.
- **Decision (2026-10-27): momentum replaced by peak speed, with Combine weight kept as a separate covariate.** A product locks mass into a fixed role; separate variables let the pressure model estimate how much mass matters. Reported finding: among OL, a mass-aware momentum metric was 0.95 correlated with speed alone at the player level.
- Final game features: `retreat_depth`, `peak_accel_05`, `peak_speed`; covariate `combine_weight`.

## Combine drop drill (step 4)
- **Drill structure (Logan's clip review plus tracking, 2026-10-27):** set back and to one side, contact on a first pad, shuffle to a second pad on the other side, then flip and run about 8 yd back. Clips about 4.4 s. Each player gets two reps, one to each side (117 players with 2 reps, 106 of them go to opposite sides by y at 1.5 s; the other 11 need a look). Some reps show the pad bumps around 1.9 s and 2.5 to 2.7 s.
- **Timing of the first speed dip (first pad):** median 1.6 s; 10th / 25th / 75th / 90th percentile 1.3 / 1.4 / 1.8 / 2.0 s; no clear dip in 36 reps.
- `attempt` numbers are not 1 and 2 (values 1 to 7), so rep order comes from time.
- Viewer for clip review: Drop drill rep viewer artifact (claude.ai), built from 01-era clean Combine data.
- **Drill review (02_combine_drill_review, 2026-10-27):** keep PASS_RUSH_DROP (set phase, two reps one per side), PASS_PRO_MIRROR_DRILL and FIVE_YARD_WAVE_DRILL_SLIDE_AND_SHUFFLE (change of direction; one rep each, 121 and 120 OL). Dropped: the three pull drills, screen drill, 40, short shuttle, three cone (forward or along-the-line movement, or under half the OL tracked).
- PASS_RUSH_DROP was first chosen on 10/20 because it is the only OL drill with two reps and its name suggested a pass set; that "direct analogue of the game first 1.5 s" mapping in lit-07 was not checked against clips at the time. Clip review shows only the first ~1.2 s is a set.
- **Lateral shift will be added** to the game features and the drop-drill set phase (Logan, 2026-10-27).
- **Window stays at 1.5 s for now** (Logan, 2026-10-27: start with the original 1.5 s, expand to other windows later). Lateral shift added as plain distance, |y at 1.5 s minus stance y|; signed toward the outside needs a left/right side, which the data does not give. Note for the drill side: at 1.5 s the first pad has already hit on about a third of drop-drill reps; 1.2 s is the planned comparison when windows expand.

## Drop drill set features (03_drop_drill_features, 2026-10-27, run while Logan was away; findings only, no decisions taken)
- Same four features as games, 1.5 s window, with clip start standing in for the stance. Clips start with the player already moving (median start speed 0.35 yd/s), so the drill has no stance; first-step acceleration is not fully comparable to the game side.
- Drill scale is close to games: median retreat 1.60 vs 1.97 yd, lateral 1.03 vs 0.88, peak speed 1.97 vs 2.44, first-step accel 2.50 vs 2.32.
- First pad lands inside the window on 33% of reps at 1.5 s and 7.5% at 1.2 s.
- **Side and rep order are the same thing:** rep 1 goes to −y in 112 of 120 cases, rep 2 to +y in 114 of 118. Side effects and warm-up or learning effects can't be separated.
- **Left vs right agreement is near zero** (108 players, ICC(2,1) at 1.5 s: retreat 0.04, lateral 0.00, peak speed −0.02, first-step accel 0.10; similar at 1.2 s and after aligning to movement onset). Right-side (rep 2) reps are deeper and faster on average (retreat 2.01 vs 1.20 yd). Sanity check: the same ICC code gives 0.92 for OL tracked-40 peak speed (84 players). Whole-clip peak speed (the run at the end) agrees better, ICC 0.44.
- **Game set features are very stable:** split-half reliability 0.93 to 0.99 (64 players, 100+ plays, dropback over 2 s), 0.92 to 0.96 within position. Caveat: stability can also come from team scheme, which split-half does not separate.
- **Drill vs game, player level (63 players):** r between −0.19 and 0.11, within position −0.17 to 0.00; rough 95% CI ±0.25. Consistent with no link, which is expected given the drill's near-zero reliability.
- Open questions for Logan: whether a drill feature that disagrees with itself across sides is usable at all; whether to treat each side as its own measure (then no reliability check); whether the mirror and wave COD drills or the drop drill's later phases are a better Combine side.
- **Decision (Logan, 2026-10-27 20:37, read as "game side yes, option 1 yes"):** game set measures are kept; each drop-drill side is treated as its own measure. Result of that split: left (rep 1) vs game r between −0.22 and 0.14 (59 players); right (rep 2) vs game r between −0.12 and 0.12 (62 players). Still null; rough 95% CI about ±0.25.

## Set style vs pressure (step 7, 04_set_vs_pressure, 2026-10-27)
- **Design (Logan: "go with ur gut"):** outcome pressure_allowed, with peak_pressure_probability_allowed as a check; set style is player-level (mean features), built from a random half of each player's plays and tested on the other half; plays with pressure inside the 1.5 s window dropped; baseline = Combine weight, position, dropback duration, rushers encountered (no draft slot); logistic with player-clustered SEs and 5-fold CV holding out whole players; 20 random splits.
- Leakage was small: 51 plays (1.2% of pressures) had pressure inside the window.
- Sample: 47,865 plays, 66 players with 100+ plays.
- **Result: set style adds nothing to predicting pressure for unseen players.** CV log loss is slightly worse with set features in every split (mean +0.0005; AUC 0.771 base vs 0.768 full). Set coefficients average near zero across splits (largest: lateral shift −0.06 per SD).
- The baseline does the work: dropback duration (+0.58 log-odds per second) and two rushers (+1.16) dominate; tackles allow more than centers; weight adds nothing.
- Within position and without situation controls, players who shift more laterally allow less pressure (r about −0.3) and deeper retreaters allow a bit more (about +0.2). These largely disappear once dropback and rushers are controlled, which points to scheme or situation rather than skill.
- Continuous check (one split): lateral shift slightly negative and peak speed slightly positive with p under 0.05, small effects that vary by split. Not a finding without repeats and a multiple-testing correction.

## Post-set "anchor" test (written before running, 2026-10-27 21:30)
- Logan: "keep going, we need to make this work." Guardrail: each new test is specified before it runs and logged either way, judged on held-out data like step 7.
- Reason: the first 1.5 s is before contact; pressure is decided after contact. Blocker-side STRAIN-like measure (lit-07: STRAIN authors list a blocker version as future work).
- Features, from 1.5 s to the throw (dropback_duration), capped at 3.5 s, dropbacks over 2 s: `pushback_rate` (yd per s lost toward the QB after 1.5 s) and `max_depth` (deepest point before the throw, yd behind stance).
- Test: trait from half A using only non-pressure plays; outcome pressure in half B; baseline adds the player's half-A pressure rate on top of weight, position, dropback, rushers; logistic, player-clustered SEs, 5-fold CV holding out players, 20 splits.
- This is test 2 of the idea-2 pressure question (test 1 = set style, null).
- **Anchor test result:** null. 39,252 plays, 64 players. The anchor traits are very stable (half vs half r 0.95 max depth, 0.93 pushback rate) but add nothing for unseen players: CV log loss slightly worse on average (better in 7 of 20 splits), AUC 0.733 base vs 0.732. Coefficients flip sign relative to expectation and reach p < 0.05 in only 35 to 40% of splits. Note: pushback_rate (mean 1.75 yd/s) mostly reflects the continuing set retreat, not being driven back.
- **Player pressure tendency is real:** the player's own half-A pressure rate improves CV prediction in 20 of 20 splits, and situation-adjusted pressure rate has split-half reliability 0.66. So there is a stable player signal; the blocker's own movement (set or post-set) does not explain it. Consistent with lit-07 (pressure depends heavily on the rusher, who is not tracked).

## Combine link check (2026-10-27 21:40)
- Logan asked whether pressure over expected connects to the Combine. Kaggle rules (saved overview page): the writeup must explicitly link Combine **tracking** to regular-season performance (pass/fail), so a pressure metric alone does not qualify.
- Pre-specified test (written before running): POE per player = mean(observed − expected pressure), expected from a logistic on dropback duration, rushers, position, weight; all regular-season OL pass-pro plays with no pressure inside 1.5 s; players with 100+ plays. Combine tracking features, player mean over reps, each residualized on position: 40 (peak speed, peak accel), drop drill (whole-clip peak speed), mirror and wave (peak speed, peak accel, peak decel = min smoothed accel, mean speed over the first 6 s). 11 features, Pearson r with POE, Holm correction across the 11.
