export function sampleNormal(mean, variance) {
  const u1 = Math.random();
  const u2 = Math.random();
  const z = Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
  return mean + Math.sqrt(Math.max(variance, 1e-9)) * z;
}

export function pdfNormal(x, mean, variance) {
  if (variance <= 0) return x === mean ? 1 : 0;
  const sigma = Math.sqrt(variance);
  return (
    Math.exp(-0.5 * ((x - mean) / sigma) ** 2) / (sigma * Math.sqrt(2 * Math.PI))
  );
}
