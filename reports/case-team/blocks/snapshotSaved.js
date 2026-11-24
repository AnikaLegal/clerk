// Retool workflow JavaScript block "snapshotSaved": checks saveSnapshot
// wrote the month's row before any files are made.
console.log(`saveSnapshot raw: ${JSON.stringify(saveSnapshot.data)}`);
const rows = Array.isArray(saveSnapshot.data)
  ? saveSnapshot.data
  : (Object.values(saveSnapshot.data || {})[0] || []);
if (!rows.length) {
  throw new Error(`saveSnapshot saved no row for ${setup.data.month} (${setup.data.environment}).`);
}
console.log(`Saved ${setup.data.month.slice(0, 7)} (${setup.data.environment}).`);
return saveSnapshot.data;
