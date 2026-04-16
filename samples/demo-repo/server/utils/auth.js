// Extremely naive auth helper — demo only.
const TOKENS = new Set();

function issueToken(userId) {
  const token = `${userId}-${Date.now()}`;
  TOKENS.add(token);
  return token;
}

function verifyToken(token) {
  return TOKENS.has(token);
}

module.exports = { issueToken, verifyToken };
