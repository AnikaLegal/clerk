import { Model } from 'survey-core'

import { api } from '../api'
import { logException } from '../utils'
import { Upload } from './types'

/**
 * Wire the survey's file questions to POST /api/upload/. Files upload
 * immediately on selection (one request per file, like the old form) and
 * the question value items carry the backend Upload object as `content`,
 * which serializeAnswers unwraps into the wire format [{id, issue, file}].
 * Files are settled independently: a corrupt or mis-named file (400) fails
 * alone without discarding the rest of the batch.
 */
export const attachUploadHandler = (survey: Model) => {
  survey.onUploadFiles.add(async (_, options) => {
    const results = await Promise.allSettled(
      options.files.map((file) => api.upload.create(file))
    )
    const uploaded: { file: File; content: Upload }[] = []
    const errors: string[] = []
    results.forEach((result, i) => {
      if (result.status === 'fulfilled') {
        uploaded.push({ file: options.files[i], content: result.value })
      } else {
        logException(result.reason)
        errors.push(`Could not upload ${options.files[i].name}`)
      }
    })
    options.callback(uploaded, errors.length > 0 ? errors : undefined)
  })
}
