import { ServiceCategory, ServiceCreate } from 'api'
import {
  DISCRETE_SERVICE_TYPES,
  ONGOING_SERVICE_TYPES,
  SERVICE_CATEGORIES,
} from 'consts'
import * as Yup from 'yup'

const REQUIRED = 'This field is required.'

export const SERVICE_TYPES: Record<ServiceCategory, Record<string, string>> = {
  DISCRETE: DISCRETE_SERVICE_TYPES,
  ONGOING: ONGOING_SERVICE_TYPES,
}

export const ServiceSchema = Yup.object().shape({
  category: Yup.string()
    .oneOf(Object.keys(SERVICE_CATEGORIES))
    .required(REQUIRED),
  type: Yup.string()
    .required(REQUIRED)
    .when('category', ([category], schema) =>
      category in SERVICE_TYPES
        ? schema.oneOf(Object.keys(SERVICE_TYPES[category]), REQUIRED)
        : schema
    ),
  started_at: Yup.string().required(REQUIRED),
  finished_at: Yup.string().nullable().optional(),
  count: Yup.number()
    .transform((value, original) => (original === '' ? undefined : value))
    .when('category', {
      is: 'DISCRETE',
      then: (schema) =>
        schema
          .required(REQUIRED)
          .integer('Count must be a whole number')
          .min(1),
      otherwise: (schema) => schema.nullable().optional(),
    }),
  notes: Yup.string().nullable().optional(),
})

/** Drop the fields that do not apply to the selected category. The count is
 * omitted rather than nulled for ongoing services as it is never nullable. */
export const toServicePayload = (values: ServiceCreate): ServiceCreate =>
  values.category === 'DISCRETE'
    ? { ...values, finished_at: null }
    : { ...values, count: undefined! }
