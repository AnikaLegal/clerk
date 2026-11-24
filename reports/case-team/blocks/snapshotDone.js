// Retool workflow JavaScript block "snapshotDone": says what snapshot mode
// did. An empty result from saveSnapshotOnly means the row already existed.
console.log(`saveSnapshotOnly raw: ${JSON.stringify(saveSnapshotOnly.data)}`);
const saved = Array.isArray(saveSnapshotOnly.data)
  ? saveSnapshotOnly.data.length
  : (Object.values(saveSnapshotOnly.data || {})[0] || []).length;
const message = saved
  ? `Saved ${setup.data.month.slice(0, 7)} (${setup.data.environment}).`
  : `Kept the existing ${setup.data.month.slice(0, 7)} row (${setup.data.environment}); run with force to replace it.`;
console.log(message);
return message;
