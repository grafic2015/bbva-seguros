export const keysPressed: Record<string, boolean> = {};

window.addEventListener("keydown", (e) => {
  keysPressed[e.key.toLowerCase()] = true;
});

window.addEventListener("keyup", (e) => {
  keysPressed[e.key.toLowerCase()] = false;
});

window.addEventListener("blur", () => {
  for (const key in keysPressed) {
    keysPressed[key] = false;
  }
});
