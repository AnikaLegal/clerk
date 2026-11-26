// Retool workflow JavaScript block "folders": finds the report month's
// financial year folder and its "Chart data" subfolder, creating either if
// it's missing. Uses the workflow functions findFolder and createFolder.

// A function's result may come back as the response itself or wrapped in
// .data; accept both.
const unwrap = (result) => (result && result.data !== undefined ? result.data : result);

async function findOrCreate(name, parentId) {
  const found = unwrap(await findFolder(name, parentId)).files || [];
  if (found.length > 1) {
    throw new Error(`More than one folder called "${name}"; remove the extra one.`);
  }
  if (found.length === 1) {
    return found[0].id;
  }
  return unwrap(await createFolder(name, parentId)).id;
}

const fyFolderId = await findOrCreate(setup.data.fyFolderName, setup.data.rootFolderId);
const chartFolderId = await findOrCreate("Chart data", fyFolderId);
return { deckFolderId: fyFolderId, chartFolderId };
