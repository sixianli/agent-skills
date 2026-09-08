# Visual comparison

Before comparing, fix the version, viewport, DPR, font loading, data, scroll position, animation time, and interaction state. Save a baseline before changes. Without a baseline or with inconsistent environments, describe observations only; do not claim visual parity.

Capture before and after images from the real interface using the same screenshot method. Preserve originals and diff images. First introduce a controlled difference to show that the comparison detects changes. Pixel-exact acceptance requires zero difference; a nonzero result is not identical. Other tolerances must come from the actual acceptance contract, not an expanded threshold chosen during testing.

Differences may come from implementation, environment, or a wrong baseline. Determine the cause first. Report any change to the baseline or comparison contract and follow existing authorization; never alter them just to pass. Handle shared components first. A shared browser instance has one operator. Divide independent components only when instances and writes are actually isolated and the benefit justifies it.
