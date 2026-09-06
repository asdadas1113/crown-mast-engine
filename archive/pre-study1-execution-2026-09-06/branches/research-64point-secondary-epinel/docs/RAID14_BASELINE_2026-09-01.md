# 14-burst raid baseline (2026-09-01)

This note records the practical 180-second burst timing model used by the Crown–Mast research engine.
It supplements, rather than rewrites, the legacy 12-burst regression timeline in `RESEARCH_HANDOFF_V6.md`.

## Measurement basis

One shooting-range run was played with the goal of activating every burst stage as quickly as possible.
The observed B1 countdown display was:

```text
c1  2:57
c2  2:44
c3  2:32  (B2 crossed to 2:31)
c4  2:19
c5  2:06
c6  1:54
c7  1:41
c8  1:29  (B2 crossed to 1:28)
c9  1:16
c10 1:03
c11 0:51
c12 0:38
c13 0:26  (B2 crossed to 0:25)
c14 0:13
```

Across the run, 28 manual stage-transition observations clustered around 9.9x seconds remaining on the
10-second chain timer. Their mean is approximately 9.94 seconds, corresponding to roughly 0.06 seconds
per B1->B2 or B2->B3 input. Auto activation was observed around 9.59 seconds remaining, so the manual run
was substantially closer to immediate input than auto.

A further observation was that the next B1 cooldown became ready at exactly 0:00 after c14. This is used
only as a convenient model anchor, not as a frame-accurate measurement.

## Engine baseline

The practical research baseline is:

```text
battle duration             180.00 s
burst cycles                14
B1-to-B1 interval           12.70 s
B1-to-B2 input gap           0.06 s
B2-to-B3 input gap           0.06 s
full-burst duration         10.00 s
first B1                     2.20 s elapsed (177.80 s remaining)
```

With these values:

```text
c14 B1                       167.30 s elapsed (12.70 s remaining)
c14 B3 / full-burst start   167.42 s elapsed
c14 full-burst end          177.42 s elapsed (2.58 s remaining)
theoretical c15 B1          180.00 s elapsed
```

`12.70 s` is deliberately slightly conservative relative to the shooting-range run. It represents a
realistic fast raid baseline rather than a machine-level 15-burst target. A 15-burst run is therefore not
part of the standard policy and must be modeled explicitly as an exceptional case if needed.

## Terminal Mast rule

Mast: Romantic Maid gains one Drunken stack at each B1 and resets when a 3-stack full burst ends.
Under both the conventional and sustained-funnel policies, c12 reaches/reset a 3-stack state. Therefore:

```text
c13 B1 -> Drunken 1
c14 B1 -> Drunken 2
```

There is no c15 in the practical baseline, so another 3-stack Mast cannot occur. The standard terminal
choice is therefore **Mast at c14 with 2 stacks**.

The resulting 14-cycle B2 policies are:

```text
Conventional:
C, C, M / C, C, M / C, C, M / C, C, M / C, M2

Sustained funnel:
C, C, M / C, M2, C / C, C, M / C, M2, C / C, M2
```

This has a useful research property: c13 and c14 use the same direct B2 choices in both policies. Any
remaining difference in those terminal cycles can therefore reflect state propagated from earlier choices,
especially the c11/c12 difference, instead of introducing a new terminal B2 mismatch.
