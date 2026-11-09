// Public student registration implemented in app/api/v1/base/base.py.
// The server fixes the role; never substitute an administrator create-user API.
export const studentRegistrationContract = {
  path: '/base/register',
  // Match Python's Unicode code-point length (8..128).
  passwordValidator: (value) =>
    typeof value === 'string' && [...value].length >= 8 && [...value].length <= 128,
}

// This endpoint derives the user exclusively from the authenticated request.
export const studentClassroomContract = { path: '/sessions/mine' }

export function registrationReady() {
  return (
    typeof studentRegistrationContract.path === 'string' &&
    studentRegistrationContract.path.startsWith('/base/') &&
    typeof studentRegistrationContract.passwordValidator === 'function'
  )
}
