export const logistic = (R: number, theta: number, beta: number): number => {
  return 1 / (1 + Math.exp(-beta * (R - theta)));
};

export const clamp = (value: number, min: number, max: number): number => {
  return Math.min(Math.max(value, min), max);
};
