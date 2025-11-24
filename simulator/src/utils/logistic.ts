export const logistic = (R: number, theta: number, beta: number): number => {
  return 1 / (1 + Math.exp(-beta * (R - theta)));
};

export const clamp = (value: number, min: number, max: number): number => {
  return Math.min(Math.max(value, min), max);
};

export const invertedSigmoid = (
  R: number,
  theta: number,
  beta: number,
  amplitude = 1,
  baseline = 0
): number => {
  return amplitude / (1 + Math.exp(beta * (R - theta))) + baseline;
};

export const cubicRootJump = (
  R: number,
  theta: number,
  betaBase = 4.236,
  k = 6.5,
  epsilon = 1e-6
): number => {
  const proximity = Math.max(R / (theta + epsilon) - 1, 0);
  return k * Math.cbrt(proximity) + betaBase;
};

export const tauStar = (R: number, theta: number, beta: number, epsilon = 1e-6): number => {
  const safeBeta = Math.max(beta, epsilon);
  const distance = Math.max(Math.abs(R - theta), epsilon);
  return Math.log(distance / epsilon) / safeBeta;
};
