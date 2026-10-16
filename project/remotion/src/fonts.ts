import {loadFont} from "@remotion/fonts";
import {staticFile} from "remotion";

export const FONT = "Fredoka";
for (const weight of ["500", "600", "700"]) {
  loadFont({family: FONT, url: staticFile(`fonts/fredoka-latin-${weight}-normal.woff2`), weight});
}
