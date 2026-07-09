/** @type {import('@rtk-query/codegen-openapi').ConfigFile} */
module.exports = {
  schemaFile: '../app/openapi.generated.yaml',
  apiFile: './src/api/baseApi.ts',
  apiImport: 'baseApi',
  outputFile: './src/api/api.generated.ts',
  exportName: 'generatedApi',
  hooks: true,
  // The public intake form endpoints are consumed by the intake/ app (via
  // openapi-typescript), not by this staff SPA's RTK Query client.
  filterEndpoints: (name) => !name.includes('Intake'),
}
