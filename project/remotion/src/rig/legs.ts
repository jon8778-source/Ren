import {solve} from "./RenRig";

// Front-view legs. Ren's leg art faces the camera, so a knee bend is drawn as foreshortening: the knee comes
// towards the camera, the thigh looks shorter (squashed along its length, a little wider as it nears the
// lens) and everything below it rises with it. Legs stay vertical; nothing splays sideways.
const apply = (m: number[], p: number[]) => [m[0] * p[0] + m[2] * p[1] + m[4], m[1] * p[0] + m[3] * p[1] + m[5]];
const rest = solve({x: 0, y: 0, scale: 1});
const at = (n: string) => apply(rest.frames[n], [0, 0]);
export const THIGH = at("shin-r")[1] - at("thigh-r")[1]; // hip to knee, rig units
export const SHIN = at("shoe-r")[1] - at("shin-r")[1];   // knee to ankle
const MIN_THIGH = 0.35; // shortest a thigh may look (fully raised knee)
const SHIN_LEAN = 0.22, MAX_SHIN = 0.25;
// Deepest crouch (thigh foreshortening, rig units) before the thigh reaches its shortest
export const MAX_CROUCH = Math.min(THIGH * (1 - MIN_THIGH) / (1 - SHIN_LEAN), THIGH * (1 - MIN_THIGH) + SHIN * MAX_SHIN);

// lift: how far each foot rises (rig units); crouch: how deep the knees bend with both feet planted (rig
// units of thigh foreshortening). In a crouch the knees also part a little (KNEE_OUT degrees at full depth)
// while the shins angle back so the feet stay put. Returns joint angles, stretch, and how far the hips drop.
const KNEE_OUT = 14;
export const frontLegs = (lift: {r: number; l: number}, crouch = 0) => {
  const stretch: Record<string, [number, number]> = {};
  const angles: Record<string, number> = {};
  const shinShort = Math.min(crouch * SHIN_LEAN, SHIN * MAX_SHIN);
  const depth = Math.min(1, crouch / MAX_CROUCH);
  let drop = 0;
  for (const s of ["r", "l"] as const) {
    const sy = Math.max(MIN_THIGH, 1 - (lift[s] + crouch - shinShort) / THIGH);
    const ssy = 1 - shinShort / SHIN;
    stretch[`thigh-${s}`] = [1 + 0.14 * (1 - sy), sy];
    stretch[`shin-${s}`] = [1 + 0.05 * (shinShort / SHIN), ssy];
    // Knee out by a, shin back by b so the ankle stays under the hip: thigh*sin(a) = shin*sin(b)
    const a = (KNEE_OUT * depth * Math.PI) / 180;
    const b = Math.asin(Math.min(1, (THIGH * sy * Math.sin(a)) / (SHIN * ssy)));
    const out = s === "r" ? 1 : -1; // positive turns Ren's right leg (screen left) outward
    angles[`thigh-${s}`] = (out * a * 180) / Math.PI;
    angles[`shin-${s}`] = (-out * (a + b) * 180) / Math.PI;
    angles[`shoe-${s}`] = (out * b * 180) / Math.PI;
    if (lift[s] === 0) drop = THIGH + SHIN - (THIGH * sy * Math.cos(a) + SHIN * ssy * Math.cos(b));
  }
  return {stretch, angles, drop};
};
