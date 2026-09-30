import { FormNavProps, FormSidebar } from './FormSidebar'
import { MobileNav } from './MobileNav'

// The form's navigation in both its shapes - the docked rail and the collapsed
// bar with its sheet. Both are rendered; the stylesheet shows the one the
// viewport has room for, at the breakpoint where the rail docks.
export const FormNav = (props: FormNavProps) => (
  <>
    <MobileNav {...props} />
    <FormSidebar {...props} />
  </>
)
